"""
Utility helpers for text tokenization and config-driven limits.

- Loads a tokenizer via `tokenizers` fast backend first; falls back to
  `transformers.AutoTokenizer`.
- Caches tokenizer to avoid repeated expensive loads.
- Reads `model.name` and `magrpo.max_new_tokens` from repo config with
  best-effort YAML parsing and a fast fallback when YAML isn't available.
"""

from __future__ import annotations

import os
from typing import List, Optional, Callable, Any


_CACHE: dict[str, Any] = {
    "tokenizer": None,
    "tokenizer_name": None,
    "max_new_tokens": None,
    "model_name": None,
}


def _repo_config_path() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    repo_root = os.path.dirname(here)  # LLM_Collab_Code_Completion
    return os.path.join(repo_root, "configs", "magrpo_classeval_config.yaml")


def _read_yaml_safely(path: str) -> Optional[dict]:
    try:
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        return None


def _fast_scan_kv(path: str, key: str) -> Optional[str]:
    """Fast scan for a `key: value` line in YAML without importing yaml.

    Returns the stripped value if found.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith(key) and ":" in line:
                    try:
                        val = line.split(":", 1)[1]
                        val = val.split("#", 1)[0].strip()
                        return val
                    except Exception:
                        continue
    except Exception:
        pass
    return None


def read_default_model_from_config() -> Optional[str]:
    """Return `model.name` from repo config if available.

    Tries YAML first; falls back to a simple scan.
    """
    if _CACHE.get("model_name"):
        return _CACHE["model_name"]

    cfg = _repo_config_path()
    data = _read_yaml_safely(cfg)
    name: Optional[str] = None
    if isinstance(data, dict):
        try:
            model = data.get("model") or {}
            name = model.get("name") if isinstance(model, dict) else None
            if isinstance(name, str) and name.strip():
                _CACHE["model_name"] = name.strip()
                return _CACHE["model_name"]
        except Exception:
            pass

    # Fallback fast scan within model: block
    try:
        with open(cfg, "r", encoding="utf-8") as fh:
            in_model = False
            for raw in fh:
                line = raw.rstrip("\n")
                if not in_model:
                    if line.strip().startswith("model:"):
                        in_model = True
                    continue
                # End of model block when next top-level key appears
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    break
                if "name:" in line:
                    try:
                        val = line.split(":", 1)[1].split("#", 1)[0].strip()
                        if val:
                            _CACHE["model_name"] = val
                            return val
                    except Exception:
                        continue
    except Exception:
        pass
    return None


def get_effective_max_new_tokens(default: int = 512) -> int:
    """Read magrpo.max_new_tokens with env override and caching.

    - Env `CLASSEVAL_MAX_NEW_TOKENS` overrides config.
    - Uses YAML when available; falls back to fast scan.
    """
    if isinstance(_CACHE.get("max_new_tokens"), int):
        return int(_CACHE["max_new_tokens"])

    # Env override
    try:
        env_val = os.environ.get("CLASSEVAL_MAX_NEW_TOKENS")
        if env_val is not None:
            v = int(env_val)
            _CACHE["max_new_tokens"] = v
            return v
    except Exception:
        pass

    cfg = _repo_config_path()
    data = _read_yaml_safely(cfg)
    if isinstance(data, dict):
        try:
            magrpo = data.get("magrpo") or {}
            v = magrpo.get("max_new_tokens") if isinstance(magrpo, dict) else None
            if isinstance(v, int):
                _CACHE["max_new_tokens"] = v
                return v
        except Exception:
            pass

    scanned = _fast_scan_kv(cfg, "max_new_tokens")
    if scanned is not None:
        try:
            v = int(scanned)
            _CACHE["max_new_tokens"] = v
            return v
        except Exception:
            pass

    _CACHE["max_new_tokens"] = int(default)
    return int(default)


class TokenizerAdapter:
    """Light adapter around underlying tokenizer backends.

    Provides a unified interface for `encode_ids(text, add_special_tokens=False)`.
    """

    def __init__(self, encode_ids: Callable[[str, bool], List[int]], name: str):
        self.encode_ids = encode_ids
        self.name = name


def _load_tokenizer_impl(model_name: str) -> TokenizerAdapter:
    # Prefer `tokenizers`
    try:
        from tokenizers import Tokenizer  # type: ignore
        t = Tokenizer.from_pretrained(model_name)

        def enc_ids(s: str, add_special: bool) -> List[int]:
            enc = t.encode(s, add_special_tokens=add_special)
            return enc.ids

        return TokenizerAdapter(enc_ids, name=f"tokenizers::{model_name}")
    except Exception:
        pass

    # Fallback to transformers
    try:
        from transformers import AutoTokenizer  # type: ignore

        tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

        def enc_ids_tf(s: str, add_special: bool) -> List[int]:
            out = tok(
                s,
                add_special_tokens=add_special,
                return_attention_mask=False,
                return_token_type_ids=False,
            )
            ids = out.get("input_ids") or []
            return list(ids)

        # Ensure pad token exists (not strictly needed for counting)
        try:
            if getattr(tok, "pad_token", None) is None and getattr(tok, "eos_token", None) is not None:
                tok.pad_token = tok.eos_token  # type: ignore[attr-defined]
        except Exception:
            pass

        return TokenizerAdapter(enc_ids_tf, name=f"transformers::{model_name}")
    except Exception as e:
        raise RuntimeError(f"Failed to load tokenizer '{model_name}': {e}")


def get_cached_tokenizer() -> Optional[TokenizerAdapter]:
    """Return a cached tokenizer instance.

    - Uses env `CLASSEVAL_TOKENIZER_NAME` if set; otherwise uses model.name from config.
    - Returns None if both loading strategies fail, to allow heuristics.
    """
    tok = _CACHE.get("tokenizer")
    if tok is not None:
        return tok

    model_name = os.environ.get("CLASSEVAL_TOKENIZER_NAME") or read_default_model_from_config()
    if not model_name:
        _CACHE["tokenizer"] = None
        return None
    try:
        tok = _load_tokenizer_impl(model_name)
        _CACHE["tokenizer"] = tok
        _CACHE["tokenizer_name"] = model_name
        return tok
    except Exception:
        _CACHE["tokenizer"] = None
        return None


def count_new_tokens(text: str, add_special_tokens: bool = False) -> int:
    """Count tokens for `text` using cached tokenizer when available.

    Falls back to a simple heuristic (len(text)/4) when tokenizer cannot be loaded.
    """
    if not text:
        return 0
    tok = get_cached_tokenizer()
    if tok is not None:
        try:
            return len(tok.encode_ids(text, add_special_tokens))
        except Exception:
            pass
    # Heuristic for code-like text: ~4 chars per token
    try:
        return max(1, int(len(text) / 4))
    except Exception:
        return len(text)
