#!/usr/bin/env bash
set -euo pipefail

# SLURM wrapper (ghx4 defaults) for GRPO training on ClassEval.
# Override any variable via *_OVERRIDE or export before running.

# Default SLURM params (retain user-style env defaults)
PARTITION="${PARTITION:-gpu}"
NODES="${NODES:-1}"
NTASKS="${NTASKS:-1}"
GRES="${GRES:-gpu:h200:1}"
CPUS="${CPUS:-4}"
MEM="${MEM:-100GB}"
TIME="${TIME:-08:00:00}"

# Resolve repo root from this script path (scripts/..)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="configs/config_neu.yaml"
TRAIN_REL="train/train_grpo.py"

# Allow overrides for non-SLURM settings via *_OVERRIDE

# W&B overrides (only applied if *_OVERRIDE is set)
WAND_ENABLED_OVERRIDE="${WAND_ENABLED_OVERRIDE:-}"
WAND_PROJECT_OVERRIDE="${WAND_PROJECT_OVERRIDE:-}"
WAND_ENTITY_OVERRIDE="${WAND_ENTITY_OVERRIDE:-}"
WAND_DIR_OVERRIDE="${WAND_DIR_OVERRIDE:-}"

# Collaboration overrides (optional). If unset, YAML takes precedence.
MODE_OVERRIDE="${MODE_OVERRIDE:-}"
NUM_AGENTS_OVERRIDE="${NUM_AGENTS_OVERRIDE:-}"

# Build override string: include wandb.* and collab.* only when explicitly provided
OVERRIDE=""
if [[ -n "${WAND_ENABLED_OVERRIDE}" ]]; then
  OVERRIDE="wandb.enabled=${WAND_ENABLED_OVERRIDE}"
fi
if [[ -n "${WAND_PROJECT_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}wandb.project=${WAND_PROJECT_OVERRIDE}"
fi
if [[ -n "${WAND_ENTITY_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}wandb.entity=${WAND_ENTITY_OVERRIDE}"
fi
if [[ -n "${WAND_DIR_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}wandb.dir=${WAND_DIR_OVERRIDE}"
fi
if [[ -n "${MODE_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}collab.mode=${MODE_OVERRIDE}"
fi
if [[ -n "${NUM_AGENTS_OVERRIDE}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}collab.num_agents=${NUM_AGENTS_OVERRIDE}"
fi

# Optional: direct override for config path
CONFIG_PATH="${CONFIG_PATH_OVERRIDE:-${REPO_DIR}/${CONFIG_REL}}"

WRAP_CMD="cd ${REPO_DIR} \
&& source \$(conda info --base)/etc/profile.d/conda.sh \
&& source ~/.bashrc \
&& conda activate comlrl \
&& export WANDB_CONSOLE=\${WANDB_CONSOLE_OVERRIDE:-off} \
&& export WANDB_SILENT=\${WANDB_SILENT_OVERRIDE:-true} \
&& export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
&& export PYTHONPATH=\"\${PYTHONPATH}:\$(pwd)\" \
&& python3 -u ${TRAIN_REL} --config ${CONFIG_PATH} \
   --override \"${OVERRIDE}\""

sbatch \
  --partition="${PARTITION}" \
  --nodes="${NODES}" \
  --ntasks="${NTASKS}" \
  --gres="${GRES}" \
  --ntasks-per-node=1 \
  --cpus-per-task="${CPUS}" \
  --mem="${MEM}" \
  --time="${TIME}" \
  --wrap="${WRAP_CMD}"

echo "Submitted GRPO training job with config: ${CONFIG_PATH}"
echo "Partition=${PARTITION} Nodes=${NODES} Tasks=${NTASKS} GRES=${GRES} CPUs=${CPUS} MEM=${MEM} TIME=${TIME}"
echo "W&B: enabled=${WAND_ENABLED_OVERRIDE:-yaml} project=${WAND_PROJECT_OVERRIDE:-yaml} entity=${WAND_ENTITY_OVERRIDE:-yaml} dir=${WAND_DIR_OVERRIDE:-yaml} | Collab: ${MODE_OVERRIDE:-yaml}/${NUM_AGENTS_OVERRIDE:-yaml}"
