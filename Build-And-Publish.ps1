# Windows File Manager Pro - Build Script
# PowerShell version

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

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$root = Split-Path -Parent $PSCommandPath
Set-Location $root

function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; Pause; exit 1 }

try {
	$nodeV = (node -v)
	$npmV = (npm -v)
	Write-Host "Node: $nodeV | npm: $npmV" -ForegroundColor Green
} catch {
	Write-Host "Node.js not found. Please install Node >= 18 from https://nodejs.org/ and re-run." -ForegroundColor Red
	Start-Process "https://nodejs.org/"
	Pause
	exit 1
}

try { npm config set fund false | Out-Null; npm config set audit false | Out-Null } catch { }

try {
	Write-Host "`nInstalling dependencies (with --legacy-peer-deps)..." -ForegroundColor Cyan
	npm install --legacy-peer-deps
} catch {
	Write-Host "Install failed. Cleaning npm cache and retrying..." -ForegroundColor Yellow
	try {
		npm cache clean --force
		npm install --legacy-peer-deps
	} catch { Fail "Dependency install failed. See output above." }
}

try {
	Write-Host "`nBuilding renderer (Vite)..." -ForegroundColor Cyan
	npm run build
} catch { Fail "Renderer build failed." }

try {
	Write-Host "`nPackaging Electron app..." -ForegroundColor Cyan
	npm run electron:build
} catch { Fail "Electron packaging failed." }

$dist = Join-Path $root "dist-electron"
if (-not (Test-Path $dist)) { Fail "Build output folder not found: $dist" }

Start-Process explorer.exe $dist

$latestExe = Get-ChildItem -Path $dist -Filter *.exe -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $latestExe) { Fail "No .exe found in $dist" }

Write-Host "`nLaunching installer: $($latestExe.FullName)" -ForegroundColor Green
Start-Process -FilePath $latestExe.FullName

Write-Host "`nDone." -ForegroundColor Green