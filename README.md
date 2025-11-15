# LLM Collaboration - Code Completion

This repo provides the extended environments for [**CoMLRL**](https://github.com/OpenMLRL/CoMLRL).

## Installation

Install [**CoMLRL**](https://github.com/OpenMLRL/CoMLRL):

```bash
pip install comlrl
# Install PyTorch compatible with your device
```

Or via conda-forge:

```bash
conda install -c conda-forge comlrl
# Install PyTorch compatible with your device
```

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

## Settings

Key sections in `configs/config.yaml`:

- `model`: base checkpoint (`Qwen/Qwen2.5-Coder-3B-Instruct` by default), tokenizer/model
  kwargs, and device mapping.
- `data`: dataset name and split ratio; customize when experimenting with different ClassEval
  sub-splits or local mirrors.
- `collab`: choose `ONE` or `TAKE_JOB` and set `num_agents` (for TAKE_JOB).
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
