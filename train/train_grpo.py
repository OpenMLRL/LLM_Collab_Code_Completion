"""
GRPO/MAG(R)PO training entrypoint for ClassEval module completion with collaboration.

Supports two collaboration modes:
- ONE:     All methods in a class assigned to a single agent.
- RAND_PARTITION: Randomly partition methods across N agents (configurable).

This script uses CoMLRL's MAGRPOTrainer to handle sampling and PPO-style updates.

Config file: LLM_Collab_Module_Completion/configs/config.yaml
Key parameters:
- dataset.name:   HF dataset name (e.g., FudanSELab/ClassEval)
- data.split_ratio: train/eval split ratio (0..1)
- collab.mode:    ONE | RAND_PARTITION
- collab.num_agents: number of agents (for RAND_PARTITION)
- seed:           RNG seed for splits and method partition
- trainer.*:      MAGRPO trainer args (epochs, lr, sampling settings, etc.)
- model.*:        Base model and tokenizer settings

This file intentionally keeps dataset-specific parsing/merging utilities
in utils/ and the reward in rewards/CE_reward.py.
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional, Tuple, Callable
import time

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        f"PyYAML is required to read config.yaml. Please install pyyaml. Error: {e}"
    )


# Make repo importable
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO_ROOT))
sys.path.insert(0, REPO_ROOT)

from datasets import load_dataset  # type: ignore
from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
import torch  # type: ignore

from comlrl.trainers.magrpo import MAGRPOConfig, MAGRPOTrainer  # type: ignore
from comlrl.utils.reward_processor import RewardProcessors  # type: ignore
from LLM_Collab_Module_Completion.utils.patches import apply_default_patches
from LLM_Collab_Module_Completion.utils.trainer_args import get_trainer_args

# Local utils
from LLM_Collab_Module_Completion.utils.data import (
    dataset_train_eval_split,
    extract_class_name,
    extract_incomplete_methods,
)
from LLM_Collab_Module_Completion.utils.parse_completion import extract_method_snippets
from LLM_Collab_Module_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Module_Completion.utils.test_analysis import (
    methods_called_per_test,
)
from LLM_Collab_Module_Completion.rewards.CE_reward import (
    get_reward_function,
)
from LLM_Collab_Module_Completion.collaborations import (
    get_strategy,
    build_agent_formatters,
)
from LLM_Collab_Module_Completion.utils.prompting import (
    build_agent_prompt,
)
# External transition (multi-turn)
from LLM_Collab_Module_Completion.external import (
    set_context_resolver as external_set_context_resolver,
    get_external_transition as external_get_transition,
)


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_job_id() -> str:
    """Resolve a job id from environment or fallback to timestamp."""
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

def main():
    parser = argparse.ArgumentParser(description="Train GRPO/MAGRPO for ClassEval module completion")
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join(REPO_ROOT, "configs", "config.yaml"),
        help="Path to YAML config",
    )
    parser.add_argument("--override", type=str, default=None, help="key1=val1,key2=val2 overrides")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    # Simple inline overrides: key.path=value, comma separated
    if args.override:
        for kv in str(args.override).split(","):
            if not kv.strip() or "=" not in kv:
                continue
            k, v = kv.split("=", 1)
            # Only support top-level or one-level nested overrides for simplicity
            k = k.strip()
            v = v.strip()
            # Try to cast to number/bool where sensible
            if v.lower() in ("true", "false"):
                vv: Any = (v.lower() == "true")
            else:
                try:
                    vv = int(v) if v.isdigit() else float(v)
                except Exception:
                    vv = v
            # Assign into dict
            cur = cfg
            parts = k.split(".")
            for p in parts[:-1]:
                cur = cur.setdefault(p, {})
            cur[parts[-1]] = vv

    # Read configuration sections
    model_cfg = cfg.get("model", {})
    data_cfg = cfg.get("data", {})
    collab_cfg = cfg.get("collab", {})
    output_cfg = cfg.get("output", {})
    seed = int(cfg.get("seed", 42))
    # Optional: randomize seed when fixed_seed is false
    fixed_seed_val = cfg.get("fixed_seed", True)
    try:
        fixed_seed = bool(fixed_seed_val)
    except Exception:
        fixed_seed = True
    if not fixed_seed:
        try:
            import secrets  # stdlib
            seed = int(secrets.randbits(32))
        except Exception:
            try:
                seed = int(abs(hash(f"{time.time_ns()}_{os.getpid()}")) % (2**31 - 1))
            except Exception:
                seed = int(time.time()) & 0x7FFFFFFF

    dataset_name = data_cfg.get("dataset_name", "FudanSELab/ClassEval")
    split_ratio = float(data_cfg.get("split_ratio", 0.8))

    collab_mode = str(collab_cfg.get("mode", "ONE")).upper()
    num_agents = int(collab_cfg.get("num_agents", 1 if collab_mode == "ONE" else 2))
    if collab_mode == "ONE":
        num_agents = 1

    # Load dataset (single split then random split by ratio)
    try:
        ds_all = load_dataset(dataset_name)
    except Exception as e:
        print(f"Failed to load dataset {dataset_name}: {e}")
        return

    train_ds, eval_ds = dataset_train_eval_split(ds_all, split_ratio=split_ratio, seed=seed)
    # Tag datasets with phase so reward logger can distinguish eval vs. train
    try:
        train_ds = train_ds.map(lambda _: {"phase": "train"})
        eval_ds = eval_ds.map(lambda _: {"phase": "eval"})
    except Exception:
        pass

    # Optional: set temp base dir and keep flag for unit test runner
    tmp_base = None
    try:
        tmp_base = output_cfg.get("tmp_base_dir")
    except Exception:
        tmp_base = None
    if tmp_base:
        os.environ["CLASSEVAL_TMP_BASE"] = _expand_jobid_placeholder(str(tmp_base))
    # keep_tmp can be bool or str
    keep_tmp_val = None
    try:
        keep_tmp_val = output_cfg.get("keep_tmp", None)
    except Exception:
        keep_tmp_val = None
    if keep_tmp_val is not None:
        keep_flag = str(keep_tmp_val).strip().lower() in ("1", "true", "yes", "on")
        os.environ["CLASSEVAL_KEEP_TMP"] = "1" if keep_flag else "0"

    # Prepare tokenizer and agents
    model_name = model_cfg.get("name", "Qwen/Qwen2.5-3B")
    tokenizer_kwargs = model_cfg.get("tokenizer_kwargs", {})
    model_kwargs = model_cfg.get("model_kwargs", {})

    # Memory-optimized defaults: prefer bf16 when available
    # Allow users to set model.dtype or model.torch_dtype: "bf16" | "fp16" | "float16" | "bfloat16" | "float32"
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
        # Default to bf16 on modern GPUs; fall back to None (model default)
        try:
            if torch.cuda.is_available() and torch.cuda.get_device_capability(0)[0] >= 8:
                torch_dtype = torch.bfloat16
        except Exception:
            torch_dtype = None

    if torch_dtype is not None and "torch_dtype" not in model_kwargs:
        model_kwargs["torch_dtype"] = torch_dtype

    # Additional memory savers
    model_kwargs.setdefault("low_cpu_mem_usage", True)
    model_kwargs.setdefault("attn_implementation", "sdpa")

    tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    agents = []
    for idx in range(num_agents):
        agent = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        # Disable cache during training to save memory
        try:
            if hasattr(agent, "config"):
                agent.config.use_cache = False
        except Exception:
            pass
        # Enable gradient checkpointing when requested (default True)
        if bool(model_cfg.get("gradient_checkpointing", True)):
            try:
                agent.gradient_checkpointing_enable()
            except Exception:
                pass
        agents.append(agent)

    # Collaboration strategy
    strategy = get_strategy(collab_mode, num_agents=num_agents, seed=seed)

    # Trainer arguments and formatter/reward
    magrpo_args = get_trainer_args(cfg)
    # Debug-print to verify PPO options are threaded into MAGRPOConfig
    try:
        na = getattr(magrpo_args, "normalize_advantage", None)
        ec = getattr(magrpo_args, "epsilon_clip", None)
        lr = getattr(magrpo_args, "learning_rate", None)
        print(f"[train] MAGRPOConfig opts: normalize_advantage={na} epsilon_clip={ec} learning_rate={lr}")
    except Exception:
        pass
    formatters = build_agent_formatters(strategy)
    reward_func = get_reward_function(strategy=strategy, num_agents=num_agents)

    # Optional reward processing: shift/scale
    reward_processor = None
    rp_cfg = cfg.get("reward_processor", {})
    if rp_cfg.get("enabled", False):
        scale = rp_cfg.get("scale_factor", None)
        shift = rp_cfg.get("shift", None)
        if scale is not None:
            reward_processor = RewardProcessors.scale(factor=float(scale))
        if shift is not None:
            shift_proc = RewardProcessors.shift(value=float(shift))
            if reward_processor is None:
                reward_processor = shift_proc
            else:
                prev = reward_processor
                reward_processor = (lambda p=prev, s=shift_proc: (lambda x: s(p(x))))()

    wandb_cfg = cfg.get("wandb", None)
    wandb_config = None
    if isinstance(wandb_cfg, dict) and wandb_cfg.get("enabled", False):
        model_short = model_name.split("/")[-1]
        # Support both `wandb.dir` and `wandb.output_dir` (the latter mapped to W&B dir)
        dir_val = wandb_cfg.get("dir") or wandb_cfg.get("output_dir")
        if dir_val:
            try:
                dir_val = _expand_jobid_placeholder(str(dir_val))
            except Exception:
                dir_val = str(dir_val)
        # Force a concise, informative run name: CE_[num_agents]agents_[strategy]
        run_name = f"CE_{num_agents}agents_{collab_mode}"
        wandb_config = {
            "project": wandb_cfg.get("project", "classeval"),
            "entity": wandb_cfg.get("entity", None),
            "name": run_name,
            "dir": dir_val,
            "tags": ["classeval", collab_mode.lower(), f"agents_{num_agents}"],
        }
        # Best-effort: also set WANDB_DIR env to keep local files out of repo when dir is set
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
        "dataset_type": "classeval",
    }
    if reward_processor is not None:
        trainer_kwargs["reward_processor"] = reward_processor

    # Apply in-repo patches (no external file changes)
    apply_default_patches(cfg)

    # Multi-turn: register external transition when num_turns > 1
    is_multi_turn = False
    try:
        is_multi_turn = int(getattr(magrpo_args, "num_turns", 1)) > 1
    except Exception:
        is_multi_turn = False

    external_cfg = cfg.get("external", {})

    if is_multi_turn:
        # Build a context map from per-agent initial prompts to dataset context
        # We pre-materialize prompts for each split to avoid ambiguity.
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
                    # Partition once per example; build assigned lists per agent
                    try:
                        part = strategy.partition(example)
                    except Exception:
                        part = {}
                    assignments: Dict[int, List[str]] = {i: [] for i in range(num_agents)}
                    if part:
                        for m, aid in part.items():
                            if 0 <= int(aid) < num_agents:
                                assignments[int(aid)].append(m)

                    # Build per-agent prompts and register all to the same context payload
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
                        "tests_sandbox": test_code,  # same by default for ClassEval
                        "method_names": method_names,
                        "assignments": assignments,
                    }
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

        # Wire external transition into trainer
        external_mode = str(external_cfg.get("mode", "level_feedback"))

        def external_transition_wrapper(prompt, agent_completions, num_agents=None, **_kwargs):
            original_prompt_flag = external_cfg.get("original_prompt", True)
            previous_response_flag = external_cfg.get("previous_response", True)
            return external_get_transition(
                prompt=prompt,
                agent_completions=agent_completions,
                num_agents=(num_agents if num_agents is not None else num_agents),
                mode=external_mode,
                original_prompt=original_prompt_flag,
                previous_response=previous_response_flag,
            )

        trainer_kwargs["external_transition"] = external_transition_wrapper

    trainer = MAGRPOTrainer(**trainer_kwargs)
    trainer.train()

    # Optional save
    out_cfg = cfg.get("output", {})
    if bool(out_cfg.get("save_final_model", False)):
        save_path = out_cfg.get("save_path") or os.path.join(
            os.path.abspath(magrpo_args.output_dir), "final_model"
        )
        trainer.save_model(save_path)
        print(f"Model saved to: {save_path}")


if __name__ == "__main__":
    main()
