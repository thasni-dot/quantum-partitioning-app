Param()

$Root = Split-Path -Path $PSScriptRoot -Parent
Set-Location $Root

if (Get-Command conda -ErrorAction SilentlyContinue) {
    Write-Host 'Creating conda environment from environment.yml...'
    conda env create --file environment.yml -y | Out-Null
    Write-Host 'Installing development requirements into qiskit-dev...'
    conda run -n qiskit-dev python -m pip install -r requirements-dev.txt
    Write-Host 'Registering the qiskit-dev Jupyter kernel...'
    conda run -n qiskit-dev python -m ipykernel install --user --name qiskit-dev --display-name 'Qiskit 3.11 (qiskit-dev)'
    Write-Host 'Environment created. Use: conda activate qiskit-dev'
}
else {
    Write-Host 'Conda was not found. Creating Python venv at .venv...'
    python -m venv .venv
    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    python -m ipykernel install --user --name qiskit-dev --display-name 'Qiskit 3.11 (qiskit-dev)'
    Write-Host 'Virtual environment created. Use: . .\.venv\Scripts\Activate.ps1'
}

Write-Host 'Setup complete. Run .\scripts\verify_install.ps1 to validate the installation.'
