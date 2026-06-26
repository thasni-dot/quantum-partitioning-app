# Qiskit Development Kernel

Production-ready Python 3.11 environment for quantum research, Jupyter integration, IBM Runtime access, Aer simulator tuning, GPU/CUDA support, debugging tooling, and reproducible package management.

## Features

- Python 3.11 development environment
- Qiskit core, Aer, IBM Runtime, and visualization libraries
- JupyterLab + kernel integration for notebooks
- GPU/CUDA compatibility guide and optional GPU stack
- Debugging tools: `debugpy`, VS Code remote debugging support
- Reproducible setup with `environment.yml` and pinned requirements
- Setup scripts for Windows PowerShell and POSIX shells

## Quick start

### 1. Create the environment

PowerShell:

```powershell
.\scripts\setup_env.ps1
```

Bash / WSL / macOS:

```bash
./scripts/setup_env.sh
```

### 2. Register the Jupyter kernel

PowerShell:

```powershell
.\scripts\install_kernel.ps1
```

Bash:

```bash
./scripts/install_kernel.sh
```

### 3. Verify the installation

Run a quick check by launching a Jupyter notebook and running one of the example notebooks in the `notebooks/` directory (for example, open `notebooks/bruteforce_cut.ipynb` and run the first cells). This validates the environment, Qiskit, and kernels are working.

## Environment configuration

- `environment.yml` contains the canonical conda environment definition.
- `requirements.txt` pins production dependencies.
- `requirements-dev.txt` pins development tooling and test dependencies.
- `gpu-requirements.txt` contains optional CUDA-GPU packages for Qiskit Aer.
- `.env.example` defines runtime configuration for IBM Runtime and local debugging.

## GPU / CUDA support

1. Install the base environment.
2. Install optional GPU support:

PowerShell:

```powershell
pip install -r gpu-requirements.txt
```

Bash:

```bash
pip install -r gpu-requirements.txt
```

3. Set `QISKIT_AER_CUDA=1` in `.env` or your shell before running GPU workloads.

## IBM Runtime support

Copy `.env.example` to `.env` and update the following values:

- `IBM_TOKEN`
- `IBM_SERVICE_INSTANCE_ID`
- `IBM_REGION`

Use `qiskit_ibm_runtime` or `QiskitRuntimeService` in notebooks and Python scripts.

## Jupyter integration

The kernel scripts install a dedicated kernel named `qiskit-dev` and an optional `qiskit-gpu` kernel.

## Debugging and tooling

- `debugpy` enables VS Code Python debugging and breakpoint attachment.
- `black`, `isort`, `pre-commit`, and `mypy` support production quality and static analysis.
- `pytest` + `pytest-xdist` enable parallel testing.

## Reproducible package management

- Use `environment.yml` for conda-driven reproducible environments.
- Use `requirements.txt` and `requirements-dev.txt` for pip installs.
- If you add or update packages, pin versions explicitly to maintain reproducibility.

## Notes

- On Windows, use PowerShell scripts and `conda` when available.
- On Linux/macOS, use Bash scripts and `conda` or venv.
- GPU support is optional and depends on NVIDIA drivers, CUDA runtime, and hardware availability.
