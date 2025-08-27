param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
$venv='.venv'; $py=Join-Path $venv 'Scripts\python.exe'
if(!(Test-Path $venv)){ & py -3 -m venv $venv }
& $py -m pip install -U pip setuptools wheel
& $py -m pip install -U dearpygui pygments
& $py "$PSScriptRoot\run_aegis.py" @Args