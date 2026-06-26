Param()

$Root = Split-Path -Path $PSScriptRoot -Parent
Set-Location $Root

$pythonCode = @'
import sys
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import qiskit_ibm_runtime as ibm_runtime

print(f"Python {sys.version}")
print(f"Qiskit {__import__('qiskit').__version__}")
print(f"Qiskit IBM Runtime {ibm_runtime.__version__}")

sim = AerSimulator(method='statevector')
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure_all()
compiled = transpile(qc, sim)
result = sim.run(compiled, shots=10).result()
print('Aer result counts:', result.get_counts())
print('IBM Runtime service class available:', hasattr(ibm_runtime, 'QiskitRuntimeService'))
'@

$pythonFile = [System.IO.Path]::Combine($Root, 'verify_install_temp.py')
Set-Content -Path $pythonFile -Value $pythonCode -Encoding UTF8
python $pythonFile
Remove-Item -Path $pythonFile -Force

Write-Host 'Verification completed successfully.'
