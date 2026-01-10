# LLM Collaboration - Code Completion

This repo provides the extended environments for [**CoMLRL**](https://github.com/OpenMLRL/CoMLRL).

<img src="./demo_cc.gif" alt="Code generation demo" width="600px">

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
- **Splitting**: `train/train_magrpo.py` loads explicit HF slices from
  `dataset.train_split` and `dataset.eval_split` (e.g., `test[:50]` and `test[50:]`).
- **Subsetting**: if a split name is missing (e.g., ClassEval only has `test`),
  the loader falls back to the first available split before slicing.
- **Prompting**: prompts include the sanitized class skeleton plus per-agent method
  assignments. The default strategy assigns 1-parameter methods to agent 0 and all other
  methods to agent 1.
- **Testing**: reward code merges agent completions back into the skeleton and runs the
  provided unit tests inside a temporary directory to isolate state.

## Settings

Key sections in `configs/magrpo_classeval_config.yaml`:

- `model`: base checkpoint (`Qwen/Qwen2.5-Coder-3B-Instruct` by default), tokenizer/model
  kwargs, and device mapping.
- `dataset`: dataset name and split strings (`train_split`, `eval_split`) for
  ClassEval sub-slices or local mirrors.
- `external`: determines the feedback mode. `token_report` summarizes syntax/tests at each
  turn; other modes replicate the options documented in the code-generation README
  (`plain`, `level_feedback`, `group_feedback`, `personal_feedback`, `personal_detailed_feedback`,
  `passed`, `level_passed`).
- `magrpo`: forwarded to `comlrl.trainers.magrpo.MAGRPOTrainer`. Includes collaboration
  (`num_agents`, param-count assignment), sampling settings (`num_generations`, `num_turns`,
  temperature/top_p), rollout buffering (`rollout_buffer_size`), optimization
  hyperparameters, and IO controls.
- `output`: persistence knobs (save final model, keep tmp dirs); environment variables such
  as `CLASSEVAL_TMP_BASE` are derived from this section to colocate temp files per job.

## Rewards, Logging, and Evaluation

- `rewards/CE_reward.py` computes structured rewards:
  - `lv1`: syntax bonus.
  - `lv2`: unit-test bonus based on pass rate (passed/total).
  - `lv3`: overlap penalty normalized by total methods (range [-1, 0]).
- Tests execute inside per-sample temporary directories to avoid polluted state and are
  automatically truncated on timeout.
- Loggers are inherited from CoMLRL. Enable Weights & Biases by filling `wandb.entity`
  or disable it for offline debugging.
