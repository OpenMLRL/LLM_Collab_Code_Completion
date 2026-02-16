from __future__ import annotations

from typing import Any, Dict, Optional
import inspect

from comlrl.trainers.reinforce import MAGRPOConfig  # type: ignore


def _as_int(x: Any, default: int) -> int:
    if x is None:
        return int(default)
    if isinstance(x, bool):
        return int(default)
    if isinstance(x, int):
        return int(x)
    if isinstance(x, float):
        return int(x)
    if isinstance(x, str):
        s = x.strip()
        try:
            if s.lower().startswith("0x"):
                return int(s, 16)
            return int(float(s))
        except Exception:
            return int(default)
    return int(default)


def _as_float(x: Any, default: float) -> float:
    if x is None:
        return float(default)
    if isinstance(x, bool):
        return float(default)
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        try:
            return float(s)
        except Exception:
            return float(default)
    return float(default)


def _as_opt_float(x: Any, default: Optional[float]) -> Optional[float]:
    if x is None:
        return default
    if isinstance(x, bool):
        return default
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("none", "null", ""):
            return None
        try:
            return float(s)
        except Exception:
            return default
    return default


def _as_opt_int(x: Any, default: Optional[int]) -> Optional[int]:
    if x is None:
        return default
    if isinstance(x, bool):
        return default
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("none", "null", ""):
            return None
        try:
            return int(float(s))
        except Exception:
            return default
    return default


def _as_bool(x: Any, default: bool) -> bool:
    if x is None:
        return bool(default)
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return bool(x)
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("true", "1", "yes", "y", "t"):
            return True
        if s in ("false", "0", "no", "n", "f"):
            return False
    return bool(x)


def _as_device_spec(x: Any) -> Any:
    if x is None:
        return None
    if isinstance(x, str):
        s = x.strip()
        if s.lower() in ("none", "null", ""):
            return None
        return s
    if isinstance(x, (list, tuple)):
        return [str(v) for v in x]
    return str(x)


def get_agent_sampling_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    model_cfg = cfg.get("agent_model")
    if not isinstance(model_cfg, dict):
        raise ValueError("agent_model must be a mapping.")
    missing = [key for key in ("temperature", "top_p", "top_k") if key not in model_cfg]
    if missing:
        raise ValueError(
            f"agent_model is missing required sampling fields: {', '.join(missing)}"
        )

    def _require_float(key: str) -> float:
        value = model_cfg.get(key)
        if value is None or isinstance(value, bool):
            raise ValueError(f"agent_model.{key} must be provided as a float.")
        try:
            return float(value)
        except Exception as exc:
            raise ValueError(f"agent_model.{key} must be a float, got {value!r}.") from exc

    top_k_raw = model_cfg.get("top_k")
    if isinstance(top_k_raw, str) and top_k_raw.strip().lower() in ("none", "null", ""):
        top_k_val: Optional[int] = None
    elif top_k_raw is None:
        top_k_val = None
    else:
        try:
            top_k_val = int(float(top_k_raw))
        except Exception as exc:
            raise ValueError(
                f"agent_model.top_k must be an integer or null, got {top_k_raw!r}."
            ) from exc

    return {
        "temperature": _require_float("temperature"),
        "top_p": _require_float("top_p"),
        "top_k": top_k_val,
    }


def get_trainer_args(cfg: Dict[str, Any], *, sampling_cfg: Dict[str, Any]) -> MAGRPOConfig:
    tr = cfg.get("magrpo", {})
    lr_val = tr.get("agent_learning_rate", 1e-5)

    candidate = {
        "num_turns": _as_int(tr.get("num_turns", 2), 2),
        "num_train_epochs": _as_int(tr.get("num_train_epochs", 13), 13),
        "agent_learning_rate": _as_float(lr_val, 1e-5),
        "logging_steps": _as_int(tr.get("logging_steps", 1), 1),
        "num_generations": _as_int(tr.get("num_generations", 2), 2),
        "max_new_tokens": _as_int(tr.get("max_new_tokens", 600), 600),
        "temperature": _as_float(sampling_cfg.get("temperature"), 0.6),
        "top_p": _as_float(sampling_cfg.get("top_p"), 0.6),
        "top_k": _as_opt_int(sampling_cfg.get("top_k"), None),
    }
    candidate.update(
        {
            "num_agents": _as_int(tr.get("num_agents", 2), 2),
            "parallel_training": str(tr.get("parallel_training", "none")).strip().lower(),
            "agent_devices": _as_device_spec(tr.get("agent_devices", ["cuda:0"])),
            "discount": _as_float(tr.get("discount", 0.9), 0.9),
            "joint_mode": str(tr.get("joint_mode", "aligned")),
            "early_termination_threshold": _as_opt_float(
                tr.get("early_termination_threshold", -0.2), -0.2
            ),
        }
    )
    candidate.update(
        {
            "rollout_buffer_size": _as_int(tr.get("rollout_buffer_size", 1), 1),
            "train_batch_size": _as_opt_int(tr.get("train_batch_size", 1), 1),
            "advantage_normalization": _as_bool(
                tr.get("advantage_normalization", True), True
            ),
            "eval_interval": _as_int(tr.get("eval_interval", 10), 10),
            "eval_num_samples": _as_int(tr.get("eval_num_samples", 4), 4),
            "eval_batch_size": _as_int(tr.get("eval_batch_size", 1), 1),
            "external_prompt_passthrough": True,
        }
    )

    try:
        params = set(inspect.signature(MAGRPOConfig.__init__).parameters.keys())
    except Exception:
        params = set()
    params.discard("self")
    params.discard("args")
    params.discard("kwargs")

    filtered = {k: v for k, v in candidate.items() if k in params}
    cfg_obj = MAGRPOConfig(**filtered)

    return cfg_obj
