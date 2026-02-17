"""MAGRPO training entrypoint for ClassEval module completion with collaboration."""

import argparse
import os
import re
import sys
from typing import Any, Dict, List, Optional
import time

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

from comlrl.trainers.reinforce import MAGRPOTrainer  # type: ignore
from LLM_Collab_Code_Completion.utils.trainer_args import (
    get_trainer_args,
    get_agent_sampling_config,
)

from LLM_Collab_Code_Completion.utils.data import (
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Code_Completion.rewards.CE_reward import (
    get_reward_function,
)
import LLM_Collab_Code_Completion.rewards.CE_reward as ce_reward
from comlrl.utils.reward_processor import RewardProcessors  # type: ignore
from LLM_Collab_Code_Completion.train.strategies import (
    get_strategy,
    build_agent_formatters,
)
from LLM_Collab_Code_Completion.utils.prompting import build_agent_prompt
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


def main():
    parser = argparse.ArgumentParser(description="Train MAGRPO for ClassEval module completion")
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join(REPO_ROOT, "configs", "magrpo_classeval_config.yaml"),
        help="Path to YAML config",
    )
    parser.add_argument("--override", nargs="*", help="Override config values (format: key=value)")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    if args.override:
        overrides = parse_overrides(args.override)
        _deep_merge(cfg, overrides)

    model_cfg = cfg.get("agent_model", {})
    dataset_cfg = cfg.get("dataset", {})
    magrpo_cfg = cfg.get("magrpo", {})
    output_cfg = cfg.get("output", {})
    external_cfg = cfg.get("external", {})
    output_verbose = bool(output_cfg.get("verbose", False))
    if not isinstance(magrpo_cfg, dict):
        magrpo_cfg = {}
        cfg["magrpo"] = magrpo_cfg
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

    num_agents = int(magrpo_cfg.get("num_agents", 2))

    if not eval_split:
        print("dataset.eval_split is required.")
        return
    try:
        train_ds = load_dataset(dataset_name, split=train_split)
        eval_ds = load_dataset(dataset_name, split=eval_split)
    except Exception as e:
        print(
            f"Failed to load dataset name={dataset_name} train_split={train_split} eval_split={eval_split}: {e}"
        )
        return

    try:
        train_ds = train_ds.map(
            lambda _, i: {"phase": "train", "prompt": f"classeval:train:{i}"},
            with_indices=True,
        )
        eval_ds = eval_ds.map(
            lambda _, i: {"phase": "eval", "prompt": f"classeval:eval:{i}"},
            with_indices=True,
        )
    except Exception:
        train_ds = train_ds.map(lambda _: {"phase": "train"})
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
    model_name = model_cfg.get("name", "Qwen/Qwen3-4B-Instruct-2507")
    agent_names = cfg.get("agents")
    if agent_names is not None:
        if not isinstance(agent_names, (list, tuple)) or not all(
            isinstance(x, str) for x in agent_names
        ):
            raise ValueError("agents must be a list of model names.")
        agent_names = [str(x) for x in agent_names]
    dtype_cfg = (
        model_cfg.get("dtype")
        or model_cfg.get("torch_dtype")
    )

    def _map_dtype(x):
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

    torch_dtype = _map_dtype(dtype_cfg)
    if torch_dtype is None:
        try:
            if torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8:
                torch_dtype = torch.bfloat16
        except Exception:
            torch_dtype = None

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

    strategy = get_strategy(num_agents=num_agents, seed=seed)

    sampling_cfg = get_agent_sampling_config(cfg)
    magrpo_args = get_trainer_args(cfg, sampling_cfg=sampling_cfg)
    formatters = build_agent_formatters(strategy)
    reward_func = get_reward_function(strategy=strategy, num_agents=num_agents)

    wandb_cfg = cfg.get("wandb", None)
    wandb_config = None
    if isinstance(wandb_cfg, dict) and wandb_cfg.get("enabled", True):
        dir_val = wandb_cfg.get("dir") or output_dir
        if dir_val:
            dir_val = str(dir_val)
        try:
            num_turns_val = int(getattr(magrpo_args, "num_turns", 1))
        except Exception:
            num_turns_val = 1
        default_name = f"{dataset_type}-magrpo"
        run_name = (
            wandb_cfg.get("name")
            or wandb_cfg.get("run_name")
            or default_name
        )
        tags = wandb_cfg.get(
            "tags",
            ["magrpo", dataset_type, f"agents_{num_agents}", f"turns_{num_turns_val}"],
        )
        if not isinstance(tags, list):
            tags = ["magrpo", dataset_type, f"agents_{num_agents}", f"turns_{num_turns_val}"]
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
                "trainer": magrpo_cfg,
            },
        }
        if wandb_config.get("dir"):
            os.environ.setdefault("WANDB_DIR", str(wandb_config["dir"]))

    ce_reward.VERBOSE = output_verbose
    try:
        num_turns_val = int(getattr(magrpo_args, "num_turns", 1) or 1)
    except Exception:
        num_turns_val = 1
    try:
        eval_samples = int(getattr(magrpo_args, "eval_num_samples", 0) or 0)
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

    trainer_kwargs = {
        "agent_model": model_name or None,
        "agents": agent_names,
        "num_agents": num_agents,
        "model_config": {
            "torch_dtype": torch_dtype,
            "special_tokens": model_cfg.get("special_tokens", {}),
        },
        "reward_func": reward_func,
        "formatters": formatters,
        "args": magrpo_args,
        "train_dataset": train_ds,
        "eval_dataset": eval_ds,
        "tokenizer": tokenizers if agent_names else tokenizer,
        "wandb_config": wandb_config,
        "dataset_type": dataset_type,
    }
    if reward_processor is not None:
        trainer_kwargs["reward_processor"] = reward_processor

    is_multi_turn = False
    try:
        is_multi_turn = int(getattr(magrpo_args, "num_turns", 1)) > 1
    except Exception:
        is_multi_turn = False

    if is_multi_turn:
        def _normalize_key(s: str) -> str:
            return " ".join((s or "").split()).strip()

        context_map: Dict[str, Any] = {}

        def _register_split(ds, split_name: str):
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
                    context_map[key] = payload
        _register_split(train_ds, "train")
        _register_split(eval_ds, "eval")

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
            return external_get_transition(
                prompt=prompt,
                agent_completions=agent_completions,
                num_agents=num_agents_val,
                mode=external_mode,
                prompt_history_per_agent=prompt_history_per_agent,
                response_history_per_agent=response_history_per_agent,
                original_prompt=original_prompt_flag,
                previous_response=previous_response_flag,
            )

        trainer_kwargs["external_transition"] = external_transition_wrapper

    trainer = MAGRPOTrainer(**trainer_kwargs)
    trainer.verbose = bool(output_verbose)
    trainer.train()

    out_cfg = cfg.get("output", {})
    if bool(out_cfg.get("save_final_model", False)):
        save_path_cfg = out_cfg.get("save_path")
        if save_path_cfg:
            save_path = str(save_path_cfg)
        else:
            save_path = os.path.join(os.path.abspath(output_dir), "final_model")

        trainer.save_model(save_path)
        print(f"Model saved to: {save_path}")


if __name__ == "__main__":
    main()
