#!/usr/bin/env bash
# Submit a SLURM job to run single-turn evaluation on ClassEval.
# This version matches resources similar to:
#   srun --partition=gpu-interactive --nodes=1 --pty \
#        --gres=gpu:h200:1 --ntasks=1 --mem=100GB --time=2:00:00 /bin/bash

set -euo pipefail

# Defaults (override via *_OVERRIDE env vars below)
PARTITION="gpu"
GPU_TYPE="h200"
GPUS=1
MEM="100G"
TIME="08:00:00"

# Resolve repo root from this script path (baseline/..)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="baseline/config.yaml"
MAIN_REL="baseline/main.py"

# Allow overrides via env vars
PARTITION="${PARTITION_OVERRIDE:-$PARTITION}"
GPU_TYPE="${GPU_TYPE_OVERRIDE:-$GPU_TYPE}"
GPUS="${GPUS_OVERRIDE:-$GPUS}"
MEM="${MEM_OVERRIDE:-$MEM}"
TIME="${TIME_OVERRIDE:-$TIME}"
LIMIT_ARG="${LIMIT_OVERRIDE:-}"

WRAP_CMD="cd ${REPO_DIR} \
&& source \$(conda info --base)/etc/profile.d/conda.sh \
&& source ~/.bashrc \
&& conda activate comlrl \
&& export PYTHONPATH=\"\${PYTHONPATH}:\$(pwd)\" \
&& python3 -u ${MAIN_REL} --config ${CONFIG_REL} ${LIMIT_ARG:+--limit ${LIMIT_ARG}}"

# Ensure output directory exists for logs
mkdir -p "${SCRIPT_DIR}/output"

sbatch \
  --partition="${PARTITION}" \
  --nodes=1 \
  --ntasks=1 \
  --mem="${MEM}" \
  --time="${TIME}" \
  --gres="gpu:${GPU_TYPE}:${GPUS}" \
  --output="${SCRIPT_DIR}/output/eval2_%j.out" \
  --error="${SCRIPT_DIR}/output/eval2_%j.err" \
  --wrap="${WRAP_CMD}"

echo "Submitted eval job (GPU=${GPU_TYPE}x${GPUS}, MEM=${MEM}, TIME=${TIME}) with config: ${REPO_DIR}/${CONFIG_REL}"
echo "Partition=${PARTITION} (override with PARTITION_OVERRIDE=...)"
