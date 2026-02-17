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
- **Subsetting**: ClassEval exposes only `test`, so use slice strings on `test`
  (e.g., `test[:50]` and `test[50:]`). Missing or invalid splits will error.
- **Prompting**: prompts include the sanitized class skeleton plus per-agent method
  assignments. The default strategy assigns 1-parameter methods to agent 0 and all other
  methods to agent 1.
- **Testing**: reward code merges agent completions back into the skeleton and runs the
  provided unit tests inside a temporary directory to isolate state.

## Settings

Key sections in `configs/magrpo_classeval_config.yaml`:

- `agent_model`: base checkpoint (`Qwen/Qwen2.5-Coder-3B-Instruct` by default), tokenizer
  kwargs, and device mapping. Use top-level `agents` to provide a list of model names for
  heterogeneous teams.
- `dataset`: dataset name and split strings (`train_split`, `eval_split`) for
  ClassEval sub-slices or local mirrors.
- `external`: feedback configuration (use `code_feedback` for syntax/test diagnostics).
- `magrpo`: forwarded to `comlrl.trainers.reinforce.MAGRPOTrainer`. Includes collaboration
  (`num_agents`, param-count assignment), rollout settings (`num_generations`, `num_turns`),
  rollout buffering (`rollout_buffer_size`), optimization
  hyperparameters, and IO controls.
- Sampling knobs (`temperature`, `top_p`, `top_k`) are configured in `agent_model` and passed
  to trainer args at runtime.
- `reward_processor`: optional post-processing for rewards (scale, shift).
- `output`: persistence knobs (save final model, output paths, verbose debug prints).

## Rewards, Logging, and Evaluation

- `rewards/CE_reward.py` computes structured rewards:
  - `lv1`: syntax score proportional to valid method outputs (range [0, 2]).
  - `lv2`: unit-test bonus based on pass rate (passed/total), scaled to [0, 4].
  - `lv3`: overlap penalty normalized by total methods (range [-1, 0]).
  - reward shift: optional post-processing shift via `reward_processor.shift`.
- Tests execute inside per-sample temporary directories to avoid polluted state and are
  automatically truncated on timeout.
- Loggers are inherited from CoMLRL. Enable Weights & Biases by filling `wandb.entity`
  or disable it for offline debugging.
