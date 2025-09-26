#!/usr/bin/env bash
# Run evaluation locally (no SLURM). Assumes current machine has the env.

set -euo pipefail

# Resolve repo root from this script path (baseline/..)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="baseline/config.yaml"
MAIN_REL="baseline/main.py"
LIMIT_ARG="${LIMIT_OVERRIDE:-}"

cd "${REPO_DIR}"
source $(conda info --base)/etc/profile.d/conda.sh || true
source ~/.bashrc || true
conda activate comlrl || { echo "[ERROR] conda env 'comlrl' not found"; exit 1; }

export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -u "${MAIN_REL}" --config "${CONFIG_REL}" ${LIMIT_ARG:+--limit ${LIMIT_ARG}}
