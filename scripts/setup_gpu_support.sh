#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ -n "${CONDA_PREFIX:-}" ]; then
  echo "Installing optional GPU packages into active conda environment..."
  pip install -r gpu-requirements.txt
else
  echo "No active conda environment detected. Installing GPU packages into the current Python environment..."
  pip install -r gpu-requirements.txt
fi

echo "GPU support packages installed. Set QISKIT_AER_CUDA=1 before running GPU workloads."
