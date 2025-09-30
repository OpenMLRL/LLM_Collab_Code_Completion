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

# WandB settings
WAND_PROJECT="${WAND_PROJECT:-CE}"
WAND_ENTITY="${WAND_ENTITY:-2478906339-null}"
WAND_DIR="${WAND_DIR:-/projects/llpr/tenshi/output}"

# Collaboration overrides
MODE="${MODE:-RAND_PARTITION}"         # ONE | RAND_PARTITION
NUM_AGENTS="${NUM_AGENTS:-2}"

# Optional: path to config.yaml
CONFIG="${CONFIG:-${REPO_ROOT}/configs/config.yaml}"

PY_CMD="python -u ${REPO_ROOT}/train/train_grpo.py --config ${CONFIG} \n  --override \"wandb.enabled=true,wandb.project=${WAND_PROJECT},wandb.entity=${WAND_ENTITY},wandb.dir=${WAND_DIR},collab.mode=${MODE},collab.num_agents=${NUM_AGENTS}\""

echo "Submitting sbatch job..."
echo "Partition=${PARTITION} Nodes=${NODES} GRES=${GRES} Time=${TIME}"
echo "W&B project=${WAND_PROJECT} entity=${WAND_ENTITY} dir=${WAND_DIR}"
echo "Collab mode=${MODE} num_agents=${NUM_AGENTS}"

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

