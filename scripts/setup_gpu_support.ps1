Param()

$Root = Split-Path -Path $PSScriptRoot -Parent
Set-Location $Root

Write-Host 'Installing optional GPU packages...'
pip install -r gpu-requirements.txt

Write-Host 'GPU support packages installed. Set QISKIT_AER_CUDA=1 before running GPU workloads.'
