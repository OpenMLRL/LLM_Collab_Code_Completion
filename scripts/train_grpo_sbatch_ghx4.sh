#!/usr/bin/env bash
set -euo pipefail

# SLURM wrapper (ghx4 defaults) for GRPO training on ClassEval.
# Override any variable via *_OVERRIDE or export before running.

# Default SLURM params
ACCOUNT="bevi-dtai-gh"
PARTITION="ghx4"
GPUS=1
CPUS=64
MEM="100g"
TIME="12:00:00"

# Resolve repo root from this script path (scripts/..)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="configs/config.yaml"
TRAIN_REL="train/train_grpo.py"

# Allow overrides via env vars (consistent with baseline style)
ACCOUNT="${ACCOUNT_OVERRIDE:-$ACCOUNT}"
PARTITION="${PARTITION_OVERRIDE:-$PARTITION}"
GPUS="${GPUS_OVERRIDE:-$GPUS}"
CPUS="${CPUS_OVERRIDE:-$CPUS}"
MEM="${MEM_OVERRIDE:-$MEM}"
TIME="${TIME_OVERRIDE:-$TIME}"

# W&B overrides
WAND_PROJECT="${WAND_PROJECT_OVERRIDE:-CE}"
WAND_ENTITY="${WAND_ENTITY_OVERRIDE:-2478906339-null}"
WAND_DIR="${WAND_DIR_OVERRIDE:-../../../projects/bevi/tchen19/output}"

# Collaboration overrides (optional). If unset, YAML takes precedence.
MODE_OVERRIDE="${MODE_OVERRIDE:-}"
NUM_AGENTS_OVERRIDE="${NUM_AGENTS_OVERRIDE:-}"

# Build override string: always include wandb; include collab.* only when explicitly provided
OVERRIDE="wandb.enabled=true,wandb.project=${WAND_PROJECT},wandb.entity=${WAND_ENTITY},wandb.dir=${WAND_DIR}"
if [[ -n "${MODE_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE},collab.mode=${MODE_OVERRIDE}"
fi
if [[ -n "${NUM_AGENTS_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE},collab.num_agents=${NUM_AGENTS_OVERRIDE}"
fi

# Optional: direct override for config path
CONFIG_PATH="${CONFIG_PATH_OVERRIDE:-${REPO_DIR}/${CONFIG_REL}}"

WRAP_CMD="cd ${REPO_DIR} \
&& source \$(conda info --base)/etc/profile.d/conda.sh \
&& source ~/.bashrc \
&& conda activate comlrl \
&& export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
&& export PYTHONPATH=\"\${PYTHONPATH}:\$(pwd)\" \
&& python3 -u ${TRAIN_REL} --config ${CONFIG_PATH} \
   --override \"${OVERRIDE}\""

sbatch \
  --account="${ACCOUNT}" \
  --partition="${PARTITION}" \
  --nodes=1 \
  --gpus-per-node="${GPUS}" \
  --ntasks=1 \
  --ntasks-per-node=1 \
  --cpus-per-task="${CPUS}" \
  --mem="${MEM}" \
  --time="${TIME}" \
  --wrap="${WRAP_CMD}"

echo "Submitted GRPO training job with config: ${CONFIG_PATH}"
echo "Account=${ACCOUNT} Partition=${PARTITION} GPUs=${GPUS} CPUs=${CPUS} MEM=${MEM} TIME=${TIME}"
echo "W&B: project=${WAND_PROJECT} entity=${WAND_ENTITY} dir=${WAND_DIR} | Collab: ${MODE_OVERRIDE:-yaml}/${NUM_AGENTS_OVERRIDE:-yaml}"
