#!/usr/bin/env bash
# Submit a SLURM job to run single-turn evaluation on ClassEval.

set -euo pipefail

ACCOUNT="bevi-dtai-gh"
PARTITION="ghx4"
GPUS=1
CPUS=64
MEM=100g
TIME="12:00:00"

# Resolve repo root from this script path (baseline/..)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="baseline/config.yaml"
MAIN_REL="baseline/main.py"

# Allow overrides via env vars
ACCOUNT="${ACCOUNT_OVERRIDE:-$ACCOUNT}"
PARTITION="${PARTITION_OVERRIDE:-$PARTITION}"
GPUS="${GPUS_OVERRIDE:-$GPUS}"
CPUS="${CPUS_OVERRIDE:-$CPUS}"
MEM="${MEM_OVERRIDE:-$MEM}"
TIME="${TIME_OVERRIDE:-$TIME}"
LIMIT_ARG="${LIMIT_OVERRIDE:-}"

WRAP_CMD="cd ${REPO_DIR} \
&& source \$(conda info --base)/etc/profile.d/conda.sh \
&& source ~/.bashrc \
&& conda activate comlrl \
&& export PYTHONPATH=\"\${PYTHONPATH}:\$(pwd)\" \
&& python3 -u ${MAIN_REL} --config ${CONFIG_REL} ${LIMIT_ARG:+--limit ${LIMIT_ARG}}"

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

echo "Submitted eval job with config: ${REPO_DIR}/${CONFIG_REL}"
