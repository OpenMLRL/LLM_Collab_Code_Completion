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

from datasets import load_dataset  # type: ignore
from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
import torch  # type: ignore

from comlrl.trainers.magrpo import MAGRPOTrainer  # type: ignore
from LLM_Collab_Code_Completion.utils.patches import apply_default_patches
from LLM_Collab_Code_Completion.utils.trainer_args import get_trainer_args

from LLM_Collab_Code_Completion.utils.data import (
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Code_Completion.rewards.CE_reward import (
    get_reward_function,
)
from LLM_Collab_Code_Completion.train.strategies import (
    get_strategy,
    build_agent_formatters,
)
from LLM_Collab_Code_Completion.utils.prompting import build_agent_prompt
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


def parse_overrides(overrides: List[str]) -> Dict[str, Any]:
    if not overrides:
        return {}

    alias_root = {
        "trainer": "magrpo",
        "data": "dataset",
    }
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
        if keys and keys[0] in alias_root:
            keys[0] = alias_root[keys[0]]

        try:
            import ast
            value = ast.literal_eval(value)
        except Exception:
            pass

        current = result
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

    return result


def _resolve_job_id() -> str:
    jid = os.environ.get("SLURM_JOB_ID") or os.environ.get("JOB_ID")
    if jid:
        return str(jid)
    return time.strftime("nojid-%Y%m%d-%H%M%S")


def _expand_jobid_placeholder(path: str) -> str:
    if not isinstance(path, str) or not path:
        return path
    if "[jobid]" in path:
        return path.replace("[jobid]", _resolve_job_id())
    return path


def _preferred_split_key(ds_all: Any) -> Optional[str]:
    try:
        keys = list(ds_all.keys())  # type: ignore[attr-defined]
    except Exception:
        return None
    for k in ("train", "validation", "val", "test"):
        if k in ds_all:
            return k
    return keys[0] if keys else None


def _manual_slice_dataset(ds: Any, split_expr: Optional[str]) -> Any:
    if not split_expr or "[" not in split_expr or "]" not in split_expr:
        return ds
    try:
        m = re.search(r"\[\s*(?P<start>-?\d*)\s*:\s*(?P<end>-?\d*)\s*\]", split_expr)
        if not m:
            return ds
        start_raw = m.group("start")
        end_raw = m.group("end")
        start = int(start_raw) if start_raw not in (None, "", "+") else None
        end = int(end_raw) if end_raw not in (None, "", "+") else None
        n = len(ds)
        s_idx = start if start is not None else 0
        e_idx = end if end is not None else n
        if s_idx < 0:
            s_idx = max(0, n + s_idx)
        if e_idx < 0:
            e_idx = max(0, n + e_idx)
        e_idx = min(max(s_idx, e_idx), n)
        return ds.select(range(s_idx, e_idx))
    except Exception:
        return ds


def _load_dataset_with_optional_split(dataset_name: str, dataset_split: Optional[str]):
    if dataset_split:
        try:
            return load_dataset(dataset_name, split=dataset_split)
        except Exception:
            try:
                ds_all = load_dataset(dataset_name)
            except Exception as e:
                raise e
            base_split = str(dataset_split).split("[", 1)[0].split(":", 1)[0].strip()
            base_ds = ds_all
            try:
                if base_split and hasattr(ds_all, "keys") and base_split in ds_all:  # type: ignore[attr-defined]
                    base_ds = ds_all[base_split]
                else:
                    preferred = _preferred_split_key(ds_all)
                    if preferred is not None:
                        base_ds = ds_all[preferred]
            except Exception:
                pass
            sliced = _manual_slice_dataset(base_ds, dataset_split)
            print(
                f"[data] Loaded {dataset_name} via fallback split={dataset_split}; using {len(sliced)} examples"
            )
            return sliced
    ds_all = load_dataset(dataset_name)
    try:
        preferred = _preferred_split_key(ds_all)
        if preferred is not None and hasattr(ds_all, "keys"):  # type: ignore[attr-defined]
            return ds_all[preferred]
    except Exception:
        pass
    return ds_all


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

    model_cfg = cfg.get("model", {})
    dataset_cfg = cfg.get("dataset", {})
    magrpo_cfg = cfg.get("magrpo", {})
    output_cfg = cfg.get("output", {})
    if not isinstance(magrpo_cfg, dict):
        magrpo_cfg = {}
        cfg["magrpo"] = magrpo_cfg
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

    num_agents = int(magrpo_cfg.get("num_agents", 1))

    if not eval_split:
        print("dataset.eval_split is required when using slice-based loading.")
        return
    try:
        train_ds = _load_dataset_with_optional_split(dataset_name, train_split)
        eval_ds = _load_dataset_with_optional_split(dataset_name, eval_split)
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
        try:
            train_ds = train_ds.map(lambda _: {"phase": "train"})
            eval_ds = eval_ds.map(lambda _: {"phase": "eval"})
        except Exception:
            pass

    output_dir_cfg = magrpo_cfg.get("output_dir") or output_cfg.get(
        "base_dir", os.path.join(os.getcwd(), "output")
    )
    output_dir = _expand_jobid_placeholder(str(output_dir_cfg))
    magrpo_cfg["output_dir"] = output_dir
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception:
        pass

    tmp_base = None
    try:
        tmp_base = output_cfg.get("tmp_base_dir")
    except Exception:
        tmp_base = None
    if not tmp_base:
        tmp_base = os.path.join(output_dir, "tmp")
    if tmp_base:
        os.environ["CLASSEVAL_TMP_BASE"] = _expand_jobid_placeholder(str(tmp_base))
    keep_tmp_val = None
    try:
        keep_tmp_val = output_cfg.get("keep_tmp", None)
    except Exception:
        keep_tmp_val = None
    if keep_tmp_val is not None:
        keep_flag = str(keep_tmp_val).strip().lower() in ("1", "true", "yes", "on")
        os.environ["CLASSEVAL_KEEP_TMP"] = "1" if keep_flag else "0"

    model_name = model_cfg.get("name", "Qwen/Qwen2.5-3B")
    tokenizer_kwargs = model_cfg.get("tokenizer_kwargs", {})
    model_kwargs = model_cfg.get("model_kwargs", {})

    dtype_cfg = (
        model_cfg.get("dtype")
        or model_cfg.get("torch_dtype")
        or model_kwargs.get("torch_dtype")
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

    if torch_dtype is not None and "torch_dtype" not in model_kwargs:
        model_kwargs["torch_dtype"] = torch_dtype

    model_kwargs.setdefault("low_cpu_mem_usage", True)
    model_kwargs.setdefault("attn_implementation", "sdpa")

    tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    agents = []
    for idx in range(num_agents):
        agent = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        try:
            if hasattr(agent, "config"):
                agent.config.use_cache = False
        except Exception:
            pass
        if bool(model_cfg.get("gradient_checkpointing", True)):
            try:
                agent.gradient_checkpointing_enable()
            except Exception:
                pass
        agents.append(agent)

    strategy = get_strategy(num_agents=num_agents, seed=seed)

    magrpo_args = get_trainer_args(cfg)
    formatters = build_agent_formatters(strategy)
    reward_func = get_reward_function(strategy=strategy, num_agents=num_agents)

    wandb_cfg = cfg.get("wandb", None)
    wandb_config = None
    if isinstance(wandb_cfg, dict) and wandb_cfg.get("enabled", True):
        dir_val = wandb_cfg.get("dir") or output_dir
        if dir_val:
            try:
                dir_val = _expand_jobid_placeholder(str(dir_val))
            except Exception:
                dir_val = str(dir_val)
        try:
            num_turns_val = int(getattr(magrpo_args, "num_turns", 1))
        except Exception:
            num_turns_val = 1
        default_name = "codecompletion_classeval_magrpo"
        run_name = wandb_cfg.get("name", default_name)
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
        }
        if wandb_config.get("dir"):
            os.environ.setdefault("WANDB_DIR", str(wandb_config["dir"]))

    trainer_kwargs = {
        "agents": agents,
        "num_agents": num_agents,
        "reward_func": reward_func,
        "formatters": formatters,
        "args": magrpo_args,
        "train_dataset": train_ds,
        "eval_dataset": eval_ds,
        "tokenizer": tokenizer,
        "wandb_config": wandb_config,
        "dataset_type": dataset_type,
    }
    apply_default_patches(cfg)

    is_multi_turn = False
    try:
        is_multi_turn = int(getattr(magrpo_args, "num_turns", 1)) > 1
    except Exception:
        is_multi_turn = False

    external_cfg = cfg.get("external", {})

    if is_multi_turn:
        def _normalize_key(s: str) -> str:
            return " ".join((s or "").split()).strip()

        context_map: Dict[str, Any] = {}

        def _register_split(ds, split_name: str):
            try:
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
            except Exception:
                pass

        _register_split(train_ds, "train")
        _register_split(eval_ds, "eval")

        def _resolver(p: str):
            return context_map.get(_normalize_key(p))

        external_set_context_resolver(_resolver)

        external_mode = str(external_cfg.get("mode", "level_feedback"))

        def external_transition_wrapper(
            prompt,
            agent_completions,
            num_agents=None,
            prompt_history_per_agent=None,
            response_history_per_agent=None,
            _default_num_agents=num_agents,
            **_kwargs,
        ):
            original_prompt_flag = external_cfg.get("original_prompt", True)
            previous_response_flag = external_cfg.get("previous_response", True)
            num_agents_val = num_agents if num_agents is not None else _default_num_agents
            return external_get_transition(
                prompt=prompt,
                agent_completions=agent_completions,
                num_agents=num_agents_val,
                mode=external_mode,
                original_prompt=original_prompt_flag,
                previous_response=previous_response_flag,
                prompt_history_per_agent=prompt_history_per_agent,
                response_history_per_agent=response_history_per_agent,
            )

        trainer_kwargs["external_transition"] = external_transition_wrapper

    trainer = MAGRPOTrainer(**trainer_kwargs)
    trainer.train()

    out_cfg = cfg.get("output", {})
    if bool(out_cfg.get("save_final_model", False)):
        save_path_cfg = out_cfg.get("save_path")
        if save_path_cfg:
            try:
                save_path = _expand_jobid_placeholder(str(save_path_cfg))
            except Exception:
                save_path = str(save_path_cfg)
        else:
            save_path = os.path.join(os.path.abspath(magrpo_args.output_dir), "final_model")

        trainer.save_model(save_path)
        print(f"Model saved to: {save_path}")


if __name__ == "__main__":
    main()
