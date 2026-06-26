#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

python -m ipykernel install --user --name qiskit-dev --display-name "Qiskit 3.11 (qiskit-dev)"
python -m ipykernel install --user --name qiskit-gpu --display-name "Qiskit 3.11 (qiskit-gpu)"
jupyter kernelspec list
