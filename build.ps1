# Windows File Manager Pro (Python + PySide6) - Build Script
param(
	[string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSCommandPath
Set-Location $root

function Ensure-Admin {
	$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
	$principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
	if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
		Write-Host "Relaunching as Administrator..." -ForegroundColor Yellow
		$args = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
		Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $args
		exit
	}
}

Ensure-Admin

# Create venv
if (-not (Test-Path ".venv")) {
	& $PythonExe -m venv .venv
}

$env:VIRTUAL_ENV = Join-Path $root ".venv"
$venvPython = Join-Path $env:VIRTUAL_ENV "Scripts/python.exe"

# Upgrade pip and install deps
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

# Build with PyInstaller (one-folder + console off)
$dist = Join-Path $root "dist-py"
if (Test-Path $dist) { Remove-Item -Recurse -Force $dist }

& $venvPython -m PyInstaller --noconfirm --noconsole --name "Windows File Manager Pro" --distpath "$dist" --workpath "$dist\build" --specpath "$dist\spec" app/main.py

# Open dist folder
Start-Process explorer.exe $dist