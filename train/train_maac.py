"""MAAC training entrypoint for ClassEval module completion with collaboration."""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
import inspect
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        f"PyYAML is required to read the config file. Please install pyyaml. Error: {e}"
    )


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO_ROOT))
sys.path.insert(0, REPO_ROOT)
COMLRL_ROOT = os.path.join(os.path.dirname(REPO_ROOT), "CoMLRL")
if COMLRL_ROOT not in sys.path:
    sys.path.insert(0, COMLRL_ROOT)

from datasets import load_dataset  # type: ignore
from transformers import AutoTokenizer  # type: ignore
import torch  # type: ignore

from comlrl.trainers.actor_critic import MAACConfig, MAACTrainer  # type: ignore
from comlrl.utils.reward_processor import RewardProcessors  # type: ignore

from LLM_Collab_Code_Completion.utils.data import (
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Code_Completion.utils.prompting import build_agent_prompt
from LLM_Collab_Code_Completion.train.strategies import (
    get_strategy,
    build_agent_formatters,
)
from LLM_Collab_Code_Completion.rewards.CE_reward import get_reward_function
import LLM_Collab_Code_Completion.rewards.CE_reward as ce_reward
import LLM_Collab_Code_Completion.external as external_mod
from LLM_Collab_Code_Completion.external import (
    set_context_resolver as external_set_context_resolver,
    get_external_transition as external_get_transition,
)


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> None:
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _parse_override_value(raw: str) -> Any:
    value = raw.strip()
    lowered = value.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("none", "null"):
        return None
    try:
        import ast

        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def parse_overrides(overrides: List[str]) -> Dict[str, Any]:
    if not overrides:
        return {}

    result: Dict[str, Any] = {}

    for override in overrides:
        if "=" not in override:
            raise ValueError(f"Invalid override format: {override}. Use key=value format.")

        key, value = override.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "wandb.run_name":
            key = "wandb.name"

        keys = key.split(".")

        value = _parse_override_value(value)
        current = result
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    return result


def _as_int(x: Any, default: int) -> int:
    try:
        if x is None or isinstance(x, bool):
            return int(default)
        if isinstance(x, (int, float)):
            return int(x)
        s = str(x).strip()
        if s.lower().startswith("0x"):
            return int(s, 16)
        return int(float(s))
    except Exception:
        return int(default)


def _as_float(x: Any, default: float) -> float:
    try:
        if x is None or isinstance(x, bool):
            return float(default)
        if isinstance(x, (int, float)):
            return float(x)
        return float(str(x).strip())
    except Exception:
        return float(default)


def _as_opt_float(x: Any, default: Optional[float]) -> Optional[float]:
    if x is None or isinstance(x, bool):
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
    if x is None or isinstance(x, bool):
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
        return bool(x)
    if isinstance(x, (int, float)):
        return bool(x)
    if isinstance(x, str):
        s = x.strip().lower()
        if s in ("true", "1", "yes", "y", "on"):
            return True
        if s in ("false", "0", "no", "n", "off"):
            return False
    return bool(default)


def _map_dtype(x: Any) -> Any:
    if isinstance(x, torch.dtype):
        return x
    if not isinstance(x, str):
        return None
    s = x.strip().lower()
    if s in ("bf16", "bfloat16"):
        return torch.bfloat16
    if s in ("fp16", "float16"):
        return torch.float16
    if s in ("fp32", "float32"):
        return torch.float32
    if s == "auto":
        return "auto"
    return None


def _filter_config(candidate: Dict[str, Any], cfg_cls: Any) -> Dict[str, Any]:
    try:
        params = set(inspect.signature(cfg_cls.__init__).parameters.keys())
    except Exception:
        params = set()
    params.discard("self")
    params.discard("args")
    params.discard("kwargs")
    return {k: v for k, v in candidate.items() if k in params}


def _build_maac_args(cfg: Dict[str, Any], *, model_name: Optional[str]) -> MAACConfig:
    tr = cfg.get("maac") or {}
    if not isinstance(tr, dict):
        tr = {}
    output_cfg = cfg.get("output", {}) or {}

    adv_norm = tr.get("advantage_normalization", tr.get("normalize_advantage", True))
    critic_type = tr.get("critic_type", "v")
    if critic_type is not None:
        critic_type = str(critic_type)

    candidate = {
        "num_turns": _as_int(tr.get("num_turns", 1), 1),
        "num_train_epochs": _as_int(tr.get("num_train_epochs", 40), 40),
        "agent_learning_rate": _as_float(tr.get("agent_learning_rate", 5e-6), 5e-6),
        "critic_learning_rate": _as_float(
            tr.get("critic_learning_rate", 5e-6), 5e-6
        ),
        "rollout_buffer_size": _as_int(tr.get("rollout_buffer_size", 8), 8),
        "value_loss_coef": _as_float(tr.get("value_loss_coef", 0.6), 0.6),
        "advantage_normalization": _as_bool(adv_norm, True),
        "max_new_tokens": _as_int(tr.get("max_new_tokens", 256), 256),
        "temperature": _as_float(tr.get("temperature", 0.6), 0.6),
        "top_p": _as_float(tr.get("top_p", 0.6), 0.6),
        "top_k": _as_opt_int(tr.get("top_k", None), None),
        "num_agents": _as_int(tr.get("num_agents", 2), 2),
        "num_generations": _as_int(tr.get("num_generations", 1), 1),
        "discount": _as_float(tr.get("discount", 0.9), 0.9),
        "critic_type": critic_type,
        "early_termination_threshold": _as_opt_float(
            tr.get("early_termination_threshold", None), None
        ),
        "eval_interval": _as_int(tr.get("eval_interval", 16), 16),
        "eval_num_samples": _as_int(tr.get("eval_num_samples", 4), 4),
        "eval_batch_size": _as_int(tr.get("eval_batch_size", 1), 1),
        "logging_steps": _as_int(tr.get("logging_steps", 1), 1),
    }
    filtered = _filter_config(candidate, MAACConfig)
    return MAACConfig(**filtered)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train MAAC for ClassEval module completion")
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join(REPO_ROOT, "configs", "maac_classeval_config.yaml"),
        help="Path to YAML config",
    )
    parser.add_argument("--override", nargs="*", help="Override config values (format: key=value)")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    if args.override:
        overrides = parse_overrides(args.override)
        _deep_merge(cfg, overrides)

    model_cfg = cfg.get("agent_model", {})
    critic_model_cfg = cfg.get("critic_model", {})
    if not isinstance(critic_model_cfg, dict):
        critic_model_cfg = {}
    dataset_cfg = cfg.get("dataset", {})
    maac_cfg = cfg.get("maac", {})
    output_cfg = cfg.get("output", {})
    external_cfg = cfg.get("external", {})
    output_verbose = bool(output_cfg.get("verbose", False))
    if not isinstance(maac_cfg, dict):
        maac_cfg = {}
        cfg["maac"] = maac_cfg
    if not isinstance(external_cfg, dict):
        external_cfg = {}
        cfg["external"] = external_cfg

    try:
        import secrets

        seed = int(secrets.randbits(32))
    except Exception:
        try:
            seed = int(abs(hash(f"{time.time_ns()}_{os.getpid()}")) % (2**31 - 1))
        except Exception:
            seed = int(time.time()) & 0x7FFFFFFF

    dataset_name_raw = dataset_cfg.get("name", "FudanSELab/ClassEval")
    dataset_name = str(dataset_name_raw).strip() or "FudanSELab/ClassEval"
    dataset_type = str(dataset_cfg.get("type", "classeval")).strip() or "classeval"
    train_split = dataset_cfg.get("train_split", None)
    eval_split = dataset_cfg.get("eval_split", None)
    if isinstance(train_split, str):
        train_split = train_split.strip() or None
    if isinstance(eval_split, str):
        eval_split = eval_split.strip() or None

    try:
        train_ds = load_dataset(dataset_name, split=train_split)
        eval_ds = load_dataset(dataset_name, split=eval_split) if eval_split else None
    except Exception as e:
        print(
            f"Failed to load dataset name={dataset_name} train_split={train_split} eval_split={eval_split}: {e}"
        )
        return 1

    try:
        train_ds = train_ds.map(
            lambda _, i: {"phase": "train", "prompt": f"classeval:train:{i}"},
            with_indices=True,
        )
        if eval_ds is not None:
            eval_ds = eval_ds.map(
                lambda _, i: {"phase": "eval", "prompt": f"classeval:eval:{i}"},
                with_indices=True,
            )
    except Exception:
        train_ds = train_ds.map(lambda _: {"phase": "train"})
        if eval_ds is not None:
            eval_ds = eval_ds.map(lambda _: {"phase": "eval"})
    output_dir = str(
        output_cfg.get("base_dir", os.path.join(os.getcwd(), "output"))
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp_base = None
    try:
        tmp_base = output_cfg.get("tmp_base_dir")
    except Exception:
        tmp_base = None
    if tmp_base:
        os.environ["CLASSEVAL_TMP_BASE"] = str(tmp_base)

    model_name = str(model_cfg.get("name", "Qwen/Qwen2.5-Coder-7B")).strip()
    agent_names = cfg.get("agents")
    model_kwargs: Dict[str, Any] = {}

    torch_dtype = _map_dtype(
        model_cfg.get("dtype") or model_cfg.get("torch_dtype")
    )
    if torch_dtype is None:
        try:
            if torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8:
                torch_dtype = torch.bfloat16
        except Exception:
            torch_dtype = None
    if torch_dtype is not None:
        model_kwargs["torch_dtype"] = torch_dtype

    maac_args = _build_maac_args(cfg, model_name=model_name)
    num_agents = int(getattr(maac_args, "num_agents", 1))
    if agent_names is not None:
        if not isinstance(agent_names, (list, tuple)) or not all(
            isinstance(x, str) for x in agent_names
        ):
            raise ValueError("agents must be a list of model names.")
        agent_names = [str(x) for x in agent_names]

    tokenizer_source = agent_names[0] if agent_names else model_name
    if not tokenizer_source:
        raise ValueError("agent_model.name or agents must be provided.")
    if agent_names:
        tokenizers = [AutoTokenizer.from_pretrained(name) for name in agent_names]
    else:
        tokenizers = [AutoTokenizer.from_pretrained(tokenizer_source)]
    for tok in tokenizers:
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
    tokenizer = tokenizers[0]

    critic_names = None
    critics_field = cfg.get("critics")
    if critics_field is not None:
        if not isinstance(critics_field, (list, tuple)) or not all(
            isinstance(x, str) for x in critics_field
        ):
            raise ValueError("critics must be a list of model names.")
        critic_names = [str(x) for x in critics_field]
    critic_name = str(critic_model_cfg.get("name", "")).strip() or None
    critic_torch_dtype = _map_dtype(
        critic_model_cfg.get("torch_dtype") or critic_model_cfg.get("dtype")
    )
    critic_model_kwargs: Dict[str, Any] = {}
    if critic_torch_dtype is not None:
        critic_model_kwargs["torch_dtype"] = critic_torch_dtype

    strategy = get_strategy(num_agents=num_agents, seed=seed)
    formatters = build_agent_formatters(strategy)
    base_reward_fn = get_reward_function(strategy=strategy, num_agents=num_agents)

    prompt_to_item: Dict[str, Dict[str, Any]] = {}
    dataset_prompt_map: Dict[str, Dict[str, Any]] = {}

    def _normalize_key(s: str) -> str:
        return " ".join((s or "").split()).strip()

    def _register_prompt(prompt: str, item: Dict[str, Any]) -> None:
        key = _normalize_key(prompt)
        if not key:
            return
        prompt_to_item[key] = dict(item)

    def _register_dataset_prompts(ds, split_name: str) -> None:
        if ds is None:
            return
        for idx in range(len(ds)):
            item = ds[idx]
            skeleton = str(item.get("skeleton", ""))
            test_code = str(item.get("test", ""))
            class_name = extract_class_name(skeleton) or ""
            method_names = extract_incomplete_methods(skeleton)
            example = {
                "skeleton": skeleton,
                "class_name": class_name,
                "task_id": f"{split_name}:{idx}",
            }
            try:
                part = strategy.partition(example)
            except Exception:
                part = {}
            assignments: Dict[int, List[str]] = {i: [] for i in range(num_agents)}
            if part:
                for m, aid in part.items():
                    if 0 <= int(aid) < num_agents:
                        assignments[int(aid)].append(m)

            prompts_for_agents: List[str] = []
            for aidx, fmt in enumerate(formatters):
                try:
                    p = fmt(example)
                except Exception:
                    p = build_agent_prompt(
                        skeleton=skeleton,
                        class_name=class_name,
                        assigned_methods=assignments.get(aidx, []),
                    )
                prompts_for_agents.append(p)
                if p:
                    _register_prompt(p, item)

            payload = {
                "skeleton": skeleton,
                "class_name": class_name,
                "tests_eval": test_code,
                "tests_sandbox": test_code,
                "method_names": method_names,
                "assignments": assignments,
            }
            ds_key = _normalize_key(str(item.get("prompt", f"classeval:{split_name}:{idx}")))
            if ds_key:
                dataset_prompt_map[ds_key] = dict(item)
            if ds_key:
                _register_prompt(ds_key, item)
            for p in prompts_for_agents:
                key = _normalize_key(p)
                if key:
                    dataset_prompt_map[key] = dict(item)
    _register_dataset_prompts(train_ds, "train")
    _register_dataset_prompts(eval_ds, "eval")

    def _lookup_item(prompts: List[str]) -> Dict[str, Any]:
        for p in prompts or []:
            key = _normalize_key(str(p))
            if key in prompt_to_item:
                return prompt_to_item[key]
            if key in dataset_prompt_map:
                return dataset_prompt_map[key]
        return {}

    if num_agents == 1:
        def reward_func(prompts: List[str], agent1_completions: List[str]) -> List[float]:
            item = _lookup_item(prompts)
            batch_size = len(agent1_completions)
            batch_items = [item] * max(1, batch_size)
            return base_reward_fn(agent1_completions, batch_items=batch_items, prompts=prompts)
    else:
        def reward_func(
            prompts: List[str], agent1_completions: List[str], agent2_completions: List[str]
        ) -> List[float]:
            item = _lookup_item(prompts)
            batch_size = min(len(agent1_completions), len(agent2_completions))
            batch_items = [item] * max(1, batch_size)
            return base_reward_fn(
                agent1_completions,
                agent2_completions,
                batch_items=batch_items,
                prompts=prompts,
            )

    wandb_cfg = cfg.get("wandb", None)
    wandb_config = None
    if isinstance(wandb_cfg, dict) and wandb_cfg.get("enabled", True):
        dir_val = wandb_cfg.get("dir") or output_dir
        if dir_val:
            dir_val = str(dir_val)
        try:
            num_turns_val = int(getattr(maac_args, "num_turns", 1))
        except Exception:
            num_turns_val = 1
        default_name = f"{dataset_type}-maac"
        run_name = (
            wandb_cfg.get("name")
            or wandb_cfg.get("run_name")
            or default_name
        )
        tags = wandb_cfg.get(
            "tags",
            ["maac", dataset_type, f"agents_{num_agents}", f"turns_{num_turns_val}"],
        )
        if not isinstance(tags, list):
            tags = ["maac", dataset_type, f"agents_{num_agents}", f"turns_{num_turns_val}"]
        wandb_config = {
            "project": wandb_cfg.get("project", "classeval"),
            "entity": wandb_cfg.get("entity", None),
            "name": run_name,
            "dir": dir_val,
            "tags": tags,
            "config_sections": {
                "dataset": dataset_cfg,
                "agent_model": model_cfg,
                "output": output_cfg,
                "external": external_cfg,
                "trainer": maac_cfg,
            },
        }
        if wandb_config.get("dir"):
            os.environ.setdefault("WANDB_DIR", str(wandb_config["dir"]))

    ce_reward.VERBOSE = output_verbose
    try:
        num_turns_val = int(getattr(maac_args, "num_turns", 1) or 1)
    except Exception:
        num_turns_val = 1
    try:
        eval_samples = int(getattr(maac_args, "eval_num_samples", 0) or 0)
    except Exception:
        eval_samples = 0
    try:
        eval_len = len(eval_ds) if eval_ds is not None else 0
    except Exception:
        eval_len = 0
    if eval_samples > 0:
        eval_count = min(eval_samples, eval_len) if eval_len > 0 else eval_samples
        ce_reward.EVAL_LOG_EVERY = int(eval_count) * max(1, num_turns_val)
    else:
        ce_reward.EVAL_LOG_EVERY = None
    ce_reward.reset_eval_log_state()
    external_mod.VERBOSE = output_verbose
    reward_processor = None
    reward_proc_cfg = cfg.get("reward_processor", {}) or {}
    if reward_proc_cfg.get("enabled", True):
        scale_factor = reward_proc_cfg.get("scale_factor", 1.0)
        reward_processor = RewardProcessors.scale(factor=scale_factor)
        shift_val = reward_proc_cfg.get("shift", None)
        if shift_val is not None:
            try:
                shift_val_f = float(shift_val)
            except Exception:
                shift_val_f = None
            if shift_val_f is not None:
                shift_proc = RewardProcessors.shift(value=shift_val_f)
                prev = reward_processor
                reward_processor = (lambda p=prev, s=shift_proc: (lambda x: s(p(x))))()

    trainer_kwargs: Dict[str, Any] = {
        "tokenizer": tokenizers if agent_names else tokenizer,
        "reward_func": reward_func,
        "formatters": formatters,
        "args": maac_args,
        "train_dataset": train_ds,
        "eval_dataset": eval_ds,
        "model_config": {
            "model_kwargs": model_kwargs,
            "critic_model_kwargs": critic_model_kwargs,
            "critic_value_head_hidden_dim": maac_cfg.get("critic_value_head_hidden_dim"),
        },
        "wandb_config": wandb_config,
    }
    trainer_kwargs["agent_model"] = model_name or None
    if agent_names:
        trainer_kwargs["agents"] = agent_names
    if critic_name:
        trainer_kwargs["critic_model"] = critic_name
    if critic_names:
        trainer_kwargs["critics"] = critic_names
    if reward_processor is not None:
        trainer_kwargs["reward_processor"] = reward_processor


    is_multi_turn = False
    try:
        is_multi_turn = int(getattr(maac_args, "num_turns", 1)) > 1
    except Exception:
        is_multi_turn = False

    if is_multi_turn:
        context_map: Dict[str, Any] = {}

        def _register_context(ds, split_name: str) -> None:
            if ds is None:
                return
            for idx in range(len(ds)):
                item = ds[idx]
                skeleton = str(item.get("skeleton", ""))
                test_code = str(item.get("test", ""))
                class_name = extract_class_name(skeleton) or ""
                method_names = extract_incomplete_methods(skeleton)
                example = {
                    "skeleton": skeleton,
                    "class_name": class_name,
                    "task_id": f"{split_name}:{idx}",
                }
                try:
                    part = strategy.partition(example)
                except Exception:
                    part = {}
                assignments: Dict[int, List[str]] = {i: [] for i in range(num_agents)}
                if part:
                    for m, aid in part.items():
                        if 0 <= int(aid) < num_agents:
                            assignments[int(aid)].append(m)

                prompts_for_agents: List[str] = []
                for aidx, fmt in enumerate(formatters):
                    try:
                        p = fmt(example)
                    except Exception:
                        p = build_agent_prompt(
                            skeleton=skeleton,
                            class_name=class_name,
                            assigned_methods=assignments.get(aidx, []),
                        )
                    prompts_for_agents.append(p)

                payload = {
                    "skeleton": skeleton,
                    "class_name": class_name,
                    "tests_eval": test_code,
                    "tests_sandbox": test_code,
                    "method_names": method_names,
                    "assignments": assignments,
                }
                ds_key = _normalize_key(str(item.get("prompt", f"classeval:{split_name}:{idx}")))
                if ds_key:
                    context_map[ds_key] = payload
                for p in prompts_for_agents:
                    key = _normalize_key(p)
                    if key:
                        context_map[key] = payload
        _register_context(train_ds, "train")
        _register_context(eval_ds, "eval")

        def _resolver(p: str):
            return context_map.get(_normalize_key(p))

        external_set_context_resolver(_resolver)

        external_mode = str(external_cfg.get("mode", "code_feedback"))
        original_prompt_flag = bool(external_cfg.get("original_prompt", True))
        previous_response_flag = bool(external_cfg.get("previous_response", True))

        def external_transition_wrapper(
            prompt,
            agent_completions,
            num_agents=None,
            prompt_history_per_agent=None,
            response_history_per_agent=None,
            _default_num_agents=num_agents,
            **_kwargs,
        ):
            num_agents_val = num_agents if num_agents is not None else _default_num_agents
            prompts = external_get_transition(
                prompt=prompt,
                agent_completions=agent_completions,
                num_agents=num_agents_val,
                mode=external_mode,
                prompt_history_per_agent=prompt_history_per_agent,
                response_history_per_agent=response_history_per_agent,
                original_prompt=original_prompt_flag,
                previous_response=previous_response_flag,
            )
            item_key = _normalize_key(str(prompt or ""))
            item = prompt_to_item.get(item_key) or dataset_prompt_map.get(item_key)
            if item and isinstance(prompts, (list, tuple)):
                for p in prompts:
                    _register_prompt(str(p), item)
            return prompts

        trainer_kwargs["external_transition"] = external_transition_wrapper

    trainer = MAACTrainer(**trainer_kwargs)
    trainer.verbose = bool(output_verbose)
    trainer.train()

    if bool(output_cfg.get("save_final_model", False)):
        save_path_cfg = output_cfg.get("save_path")
        if save_path_cfg:
            save_path = str(save_path_cfg)
        else:
            save_path = os.path.join(os.path.abspath(output_dir), "final_model")
        trainer.save_model(save_path)
        print(f"Model saved to: {save_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
