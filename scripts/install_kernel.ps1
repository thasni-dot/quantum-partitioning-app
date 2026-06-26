Param()

$Root = Split-Path -Path $PSScriptRoot -Parent
Set-Location $Root

python -m ipykernel install --user --name qiskit-dev --display-name 'Qiskit 3.11 (qiskit-dev)'
python -m ipykernel install --user --name qiskit-gpu --display-name 'Qiskit 3.11 (qiskit-gpu)'
jupyter kernelspec list
