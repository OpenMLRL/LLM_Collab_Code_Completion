#!/usr/bin/env bash
set -euo pipefail

# Simple sbatch wrapper for GRPO training on ClassEval.
# You can override any of the environment variables below when invoking this script, e.g.:
#   MODE=ONE NUM_AGENTS=1 ./train_grpo_sbatch.sh
#   WAND_PROJECT=CE WAND_ENTITY=2478906339-null ./train_grpo_sbatch.sh

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

# Slurm settings (overridable via env)
PARTITION="${PARTITION:-gpu}"
NODES="${NODES:-1}"
NTASKS="${NTASKS:-1}"
GRES="${GRES:-gpu:h200:1}"
CPUS="${CPUS:-4}"
MEM="${MEM:-100GB}"
TIME="${TIME:-08:00:00}"

# Output/log dir (for slurm logs)
OUT_DIR="${OUT_DIR:-/projects/llpr/tenshi/output}"
mkdir -p "${OUT_DIR}"

# WandB settings (only applied if set)
WAND_ENABLED="${WAND_ENABLED:-}"
WAND_PROJECT="${WAND_PROJECT:-}"
WAND_ENTITY="${WAND_ENTITY:-}"
WAND_DIR="${WAND_DIR:-}"

# Collaboration overrides (optional). If unset, YAML takes precedence.
MODE="${MODE:-}"
NUM_AGENTS="${NUM_AGENTS:-}"

# Optional: path to config.yaml
CONFIG="${CONFIG:-${REPO_ROOT}/configs/config.yaml}"

# Build override string: include wandb.* and collab.* only when explicitly provided
OVERRIDE=""
if [[ -n "${WAND_ENABLED}" ]]; then
  OVERRIDE="wandb.enabled=${WAND_ENABLED}"
fi
if [[ -n "${WAND_PROJECT}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}wandb.project=${WAND_PROJECT}"
fi
if [[ -n "${WAND_ENTITY}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}wandb.entity=${WAND_ENTITY}"
fi
if [[ -n "${WAND_DIR}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}wandb.dir=${WAND_DIR}"
fi
if [[ -n "${MODE}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}collab.mode=${MODE}"
fi
if [[ -n "${NUM_AGENTS}" ]]; then
  OVERRIDE="${OVERRIDE:+${OVERRIDE},}collab.num_agents=${NUM_AGENTS}"
fi

PY_CMD="python -u ${REPO_ROOT}/train/train_grpo.py --config ${CONFIG} \n  --override \"${OVERRIDE}\""

echo "Submitting sbatch job..."
echo "Partition=${PARTITION} Nodes=${NODES} GRES=${GRES} Time=${TIME}"
echo "W&B enabled=${WAND_ENABLED:-yaml} project=${WAND_PROJECT:-yaml} entity=${WAND_ENTITY:-yaml} dir=${WAND_DIR:-yaml}"
echo "Collab mode=${MODE:-yaml} num_agents=${NUM_AGENTS:-yaml}"

sbatch \
  --partition="${PARTITION}" \
  --nodes="${NODES}" \
  --ntasks="${NTASKS}" \
  --gres="${GRES}" \
  --cpus-per-task="${CPUS}" \
  --mem="${MEM}" \
  --time="${TIME}" \
  -o "${OUT_DIR}/slurm-%j.out" \
  -e "${OUT_DIR}/slurm-%j.err" \
  --open-mode=append \
  --wrap="${PY_CMD}"
