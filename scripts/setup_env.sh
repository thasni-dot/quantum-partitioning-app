#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if command -v conda >/dev/null 2>&1; then
  echo "Creating or updating conda environment from environment.yml..."
  conda env create --file environment.yml --name qiskit-dev -y || conda env update --name qiskit-dev --file environment.yml --prune -y
  echo "Installing development requirements into conda env qiskit-dev..."
  conda run -n qiskit-dev python -m pip install -r requirements-dev.txt
  echo "Registering Jupyter kernel for qiskit-dev..."
  conda run -n qiskit-dev python -m ipykernel install --user --name qiskit-dev --display-name "Qiskit 3.11 (qiskit-dev)"
  echo "Environment created. Activate with: conda activate qiskit-dev"
else
  echo "Conda not found. Creating Python venv at .venv..."
  python3.11 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  python -m ipykernel install --user --name qiskit-dev --display-name "Qiskit 3.11 (qiskit-dev)"
  echo "Virtual environment created. Activate with: source .venv/bin/activate"
fi

echo "Setup complete."
