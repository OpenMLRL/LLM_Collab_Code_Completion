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

from comlrl.trainers.magrpo import MAGRPOConfig, MAGRPOTrainer  # type: ignore
from comlrl.utils.reward_processor import RewardProcessors  # type: ignore

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
    run_unittests_with_details,
)
from LLM_Collab_Module_Completion.collaborations import (
    get_strategy,
    build_agent_formatters,
)


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_trainer_args(cfg: Dict[str, Any]) -> MAGRPOConfig:
    tr = cfg.get("trainer", {})
    # Temperature / top_p optionally fall back to model defaults
    return MAGRPOConfig(
        output_dir=tr.get("output_dir", os.path.join(REPO_ROOT, "runs")),
        num_train_epochs=tr.get("num_train_epochs", 3),
        per_device_train_batch_size=tr.get("per_device_train_batch_size", 1),
        learning_rate=tr.get("learning_rate", 3e-5),
        logging_steps=tr.get("logging_steps", 50),
        save_steps=tr.get("save_steps", 200),
        num_generations=tr.get("num_generations", 4),
        max_new_tokens=tr.get("max_new_tokens", 512),
        temperature=tr.get("temperature", 0.2),
        top_p=tr.get("top_p", 0.95),
        num_turns=tr.get("num_turns", 1),  # single-turn by default
        # GRPO-style advantage parameters if present
        normalize_advantage=tr.get("normalize_advantage", False),
        epsilon_clip=tr.get("epsilon_clip", None),
    )


def get_reward_function(
    strategy,
    num_agents: int,
) -> Callable[..., List[float]]:
    """Create a reward function that merges multi-agent completions, runs tests,
    and computes ClassEval reward with collaboration term.

    Signature: reward_func(*agent_completions, batch_items=None, prompts=None) -> List[float]
    Where agent_completions is a tuple of lists (one list per agent), each of length batch_size.
    """

    def reward_wrapper(*agent_completions, batch_items=None, prompts=None):
        # agent_completions: tuple of [batch_size] lists.
        # Prepare outputs as list of floats.
        if not agent_completions:
            return []
        batch_size = len(agent_completions[0])
        rewards: List[float] = []

        for i in range(batch_size):
            try:
                example = batch_items[i] if batch_items is not None else {}
            except Exception:
                example = {}
            skeleton: str = example.get("skeleton", "")
            test_code: str = example.get("test", "")
            class_name = extract_class_name(skeleton) or ""
            method_names = extract_incomplete_methods(skeleton)
            # Partition via collaboration strategy
            partition = strategy.partition(example)

            # Collect each agent's completion, parse to function snippets
            method_to_code: Dict[str, str] = {}
            for agent_idx in range(num_agents):
                comp_text = ""
                try:
                    comp_text = agent_completions[agent_idx][i]
                except Exception:
                    comp_text = ""
                assigned = [m for m, a in partition.items() if a == agent_idx]
                snippets = extract_method_snippets(comp_text or "", allowed_methods=set(assigned))
                method_to_code.update(snippets)

            # Merge snippets into skeleton
            combined_code = merge_methods_into_skeleton(
                skeleton=skeleton,
                class_name=class_name,
                method_to_code=method_to_code,
            )

            # Prepare per-test method usage (heuristic via AST on test code)
            per_test_methods = methods_called_per_test(
                test_code=test_code,
                candidate_methods=set(method_names),
                class_name=class_name,
            )

            # Compute x per test using partition
            per_test_x: Dict[str, int] = {}
            for tname, used in per_test_methods.items():
                if not used:
                    per_test_x[tname] = 0
                else:
                    agents_involved = {partition.get(m, -1) for m in used if m in partition}
                    agents_involved.discard(-1)
                    per_test_x[tname] = len(agents_involved)

            # Run tests in subprocess and collect detailed per-test results
            run_res = run_unittests_with_details(combined_code, test_code)
            # Syntax correctness: if combined code compiles
            syntax_ok = bool(run_res.get("syntax_ok", False))
            syntax_score = 3.0 if syntax_ok else 0.0

            # Pass ratio r
            tests_run = int(run_res.get("testsRun", 0) or 0)
            passed = int(run_res.get("passed", 0) or 0)
            r = (passed / tests_run) if tests_run > 0 else 0.0
            pass_score = 5.0 * r

            # Collaboration score
            test_results = run_res.get("test_results", []) or []
            num_x_total = 0
            num_x_passed = 0
            for tr in test_results:
                t_id = str(tr.get("id", ""))
                outcome = str(tr.get("outcome", ""))
                x = per_test_x.get(t_id, 0)
                if x > 0:
                    num_x_total += x
                    if outcome == "passed":
                        num_x_passed += x
            collab = (2.0 * (num_x_passed / num_x_total)) if num_x_total > 0 else 0.0

            rewards.append(float(syntax_score + pass_score + collab))

        return rewards

    return reward_wrapper


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
    seed = int(cfg.get("seed", 42))

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

    # Prepare tokenizer and agents
    model_name = model_cfg.get("name", "Qwen/Qwen3-8B")
    tokenizer_kwargs = model_cfg.get("tokenizer_kwargs", {})
    model_kwargs = model_cfg.get("model_kwargs", {})

    tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    agents = [
        AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
        for _ in range(num_agents)
    ]

    # Collaboration strategy
    strategy = get_strategy(collab_mode, num_agents=num_agents, seed=seed)

    # Trainer arguments and formatter/reward
    magrpo_args = get_trainer_args(cfg)
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
        wandb_config = {
            "project": wandb_cfg.get("project", "classeval"),
            "entity": wandb_cfg.get("entity", None),
            "name": wandb_cfg.get("name", f"classeval_{collab_mode}_{model_short}"),
            "dir": wandb_cfg.get("dir", None),
            "tags": ["classeval", collab_mode.lower(), f"agents_{num_agents}"],
        }

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
