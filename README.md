# LLM Collaboration - Code Completion

This repository hosts the ClassEval collaborative code-completion environment that
extends the [CoMLRL](../CoMLRL/README.md) multi-agent training library. It focuses on class-level completions instead of standalone problems.

## Overview

- **Task**: complete partially implemented Python classes from the
  [FudanSELab/ClassEval](https://huggingface.co/datasets/FudanSELab/ClassEval) dataset.
- **Agents**: any number of LLMs coordinated through CoMLRL trainers
  (GRPO/MAGRPO variants by default).
- **Collaboration styles**: single-agent, deterministic partition, and "take-your-job"
  self-selection prompts.
- **Feedback loop**: configurable `external.mode` adapters that provide per-turn
  diagnostics (token reports, level feedback, expert edits, etc.).
- **Rewards**: multi-level shaping (`CE_reward.py`) that balances coverage, efficiency,
  load balancing, syntax, and unit tests before a final reward is reported to the trainer.

## Repository Map

| Path | Description |
| --- | --- |
| `train/train_grpo.py` | Entry point that loads config, splits ClassEval, builds prompts, and launches the MAGRPO trainer from CoMLRL. |
| `configs/config.yaml` | Default hyperparameters for model, data split, collaboration mode, logging, W&B, and tmp dirs. |
| `collaborations/` | Strategies (`ONE`, `RAND_PARTITION`, `TAKE_JOB`) and per-agent prompt formatters. |
| `external/` | Multi-turn feedback adapters (`token_report`, `plain`, `level_feedback`, `group/personal_feedback`, etc.). |
| `rewards/CE_reward.py` | Reward computation + subprocess-based unittest runner. |
| `utils/` | Data sanitizers, prompt builders, merge/parsing helpers, trainer arg builders, text utilities. |
| *(reward utilities)* | Reward-surface calculators and unit tests (`pytest`) for parsing, reward curves, and utilities. |
| *(job templates)* | SLURM helper templates for launching long-running GRPO jobs on GPUs. |

## Dataset: ClassEval

- **Contents**: each sample includes a class skeleton, method stubs (with docstrings
  or `pass`), and canonical hidden tests.
- **Splitting**: `train/train_grpo.py` performs a stable random train/eval split
  (default 80/20) on top of the Hugging Face dataset; seeds are optionally randomized via
  `fixed_seed=false`.
- **Prompting**: prompts include the sanitized class skeleton, explicit method names per
  agent, and any collaboration instructions.
- **Testing**: reward code merges agent completions back into the skeleton and runs the
  provided unit tests inside a temporary directory to isolate state.

## Getting Started

1. Install [CoMLRL](../CoMLRL/README.md) (either `pip install comlrl` or an editable clone).
2. Clone this repository alongside CoMLRL so relative imports (e.g., `from comlrl...`)
   resolve without extra sys.path fiddling.
3. Prepare the environment described under **Extra requirements** below, then download
   ClassEval automatically via `datasets.load_dataset`.
4. Configure your accelerator (GPU/TPU) and authentication if you are loading gated
   Hugging Face models.

### Quick Training Run

```bash
python -m LLM_Collab_Code_Completion.train.train_grpo \
  --config LLM_Collab_Code_Completion/configs/config.yaml \
  --override collab.mode=TAKE_JOB,collab.num_agents=3,trainer.num_train_epochs=3
```

Notes:

- Pass comma-separated `key=value` pairs to `--override` to tweak individual config leaves,
  e.g., `trainer.max_new_tokens=768`.
- Output/checkpoints go to `output.save_path` (defaults expand `[jobid]` automatically).
- Set `wandb.enabled=false` when offline or running smoke tests.

### Batch/Cluster Jobs

For SLURM-based clusters, reuse the provided sbatch templates (standard or 4xH100 layouts)
and edit them to point to your conda env, node partition, and config file, mirroring the
workflow from the code-generation repo.

## Configuration Reference

Key sections in `configs/config.yaml`:

- `model`: base checkpoint (`Qwen/Qwen2.5-Coder-3B-Instruct` by default), tokenizer/model
  kwargs, and device mapping.
- `data`: dataset name and split ratio; customize when experimenting with different ClassEval
  sub-splits or local mirrors.
- `collab`: choose `ONE`, `RAND_PARTITION`, or `TAKE_JOB` and set `num_agents`.
- `external`: determines the feedback mode. `token_report` summarizes syntax/tests at each
  turn; other modes replicate the options documented in the code-generation README
  (`plain`, `level_feedback`, `group_feedback`, `personal_feedback`, `personal_detailed_feedback`,
  `passed`, `level_passed`).
- `trainer`: forwarded to `comlrl.trainers.magrpo.MAGRPOTrainer`. Includes sampling settings
  (`num_generations`, `num_turns`, temperature/top_p), optimization hyperparameters, and IO
  controls (`output_dir`, `logging_steps`, etc.).
- `reward_processor`: optional extra scaling/shift before the reward hits the trainer.
- `output`: persistence knobs (save final model, keep tmp dirs); environment variables such
  as `CLASSEVAL_TMP_BASE` are derived from this section to colocate temp files per job.

## Collaboration & Feedback Mechanics

- **Prompts** are built via `collaborations.build_agent_formatters` and
  `utils.prompting`. Partition modes list the methods each agent must complete, while
  `TAKE_JOB` supplies a self-coordination prompt where agents decide who implements what.
- **External feedback** modules (see `external/`) map test outcomes and rewards to the next
  turn’s instructions, enabling level-by-level diagnostics or agent-specific suggestions.
- **History handling**: each agent sees its entire conversation history plus the new context,
  matching the behavior documented in the CoMLRL README.

## Rewards, Logging, and Evaluation

- `rewards/CE_reward.py` computes structured rewards:
  - `lv1`: coverage of unique methods completed.
  - `lv2`: penalizes under/over-allocation of total method picks.
  - `lv3`: balance term encouraging an even workload across agents.
  - `lv4`/`lv5`: syntax + unit-test bonuses (reported for analysis; syntax/test failures
    short-circuit the run where applicable).
- Tests execute inside per-sample temporary directories to avoid polluted state and are
  automatically truncated on timeout.
- Loggers are inherited from CoMLRL. Enable Weights & Biases by filling `wandb.entity`
  or disable it for offline debugging.

## Development & Testing

- Unit tests ship with reward visualizers (run them with `pytest`). The `calc_reward_*`
  tools are handy for understanding the shaping landscape before training.
- Utility modules (parsers, mergers, prompt builders) are deterministic and covered by
  quick tests so you can modify them confidently.
- Use the same contribution practices as the CoMLRL repo (pre-commit, lint, etc.) when
  upstreaming changes.

## Resources

- [CoMLRL paper (arXiv:2508.04652)](https://arxiv.org/abs/2508.04652)
- [CoMLRL GitHub](https://github.com/OpenMLRL/CoMLRL)
- [ClassEval dataset](https://huggingface.co/datasets/FudanSELab/ClassEval)
- [LLM Collaboration - Code Generation README](../LLM_Collab_Code_Generation/README.md)

## Extra requirements

```sh
conda activate comlrl
conda install -c conda-forge pypdf2 gensim openpyxl python-docx
```

pytest
