# Windows File Manager Pro - Build Script (Hardened)
# PowerShell version

param(
	[string]$LogPath = ""
)

function Ensure-Admin {
	$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
	$principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
	if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
		Write-Host "Relaunching as Administrator..." -ForegroundColor Yellow
		$args = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -LogPath `"$LogPath`""
		Start-Process -FilePath "powershell.exe" -Verb RunAs -ArgumentList $args
		exit
	}
}

function Always-PauseAndExit($code = 0) {
	try { Stop-Transcript | Out-Null } catch {}
	Write-Host ""; Read-Host "Press Enter to close..." | Out-Null
	exit $code
}

try {
	if ([string]::IsNullOrWhiteSpace($LogPath)) {
		$LogPath = Join-Path $env:TEMP ("wfmp_build_" + (Get-Date -Format yyyyMMdd_HHmmss) + ".log")
	}
	Start-Transcript -Path $LogPath -Force | Out-Null
	Write-Host "Logging to: $LogPath" -ForegroundColor DarkGray
} catch {}

Ensure-Admin

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$root = Split-Path -Parent $PSCommandPath
Set-Location $root

function Fail($msg) {
	Write-Host "ERROR: $msg" -ForegroundColor Red
	Write-Host "Log: $LogPath" -ForegroundColor DarkGray
	Always-PauseAndExit 1
}

# Check Node.js + npm
try {
	$nodeV = (node -v)
	$npmV = (npm -v)
	Write-Host "Node: $nodeV | npm: $npmV" -ForegroundColor Green
} catch {
	Write-Host "Node.js not found. Please install Node >= 18 from https://nodejs.org/ and re-run." -ForegroundColor Red
	Start-Process "https://nodejs.org/"
	Always-PauseAndExit 1
}

# Quiet npm
try { npm config set fund false | Out-Null; npm config set audit false | Out-Null } catch { }

# Install deps with retries
$installAttempts = 0
$maxAttempts = 3
while ($true) {
	$installAttempts++
	try {
		Write-Host "`nInstalling dependencies (attempt $installAttempts) [--legacy-peer-deps]..." -ForegroundColor Cyan
		npm install --legacy-peer-deps
		break
	} catch {
		if ($installAttempts -ge $maxAttempts) { Fail "Dependency install failed after $maxAttempts attempts." }
		Write-Host "Install failed. Cleaning cache and retrying..." -ForegroundColor Yellow
		try { npm cache clean --force } catch {}
		Start-Sleep -Seconds 2
	}
}

# Optional: rebuild native deps if present
try { npx --yes electron-builder install-app-deps | Out-Null } catch { }

# Build renderer (Vite)
try {
	Write-Host "`nBuilding renderer (Vite)..." -ForegroundColor Cyan
	npm run build
} catch { Fail "Renderer build failed." }

# Package Electron
try {
	Write-Host "`nPackaging Electron app..." -ForegroundColor Cyan
	npm run electron:build
} catch { Fail "Electron packaging failed." }

# Locate output and launch (prefer 'release', fallback to 'dist-electron')
$releaseDir = Join-Path $root "release"
$distElectronDir = Join-Path $root "dist-electron"

$outDir = $null
if (Test-Path $releaseDir) { $outDir = $releaseDir }
elseif (Test-Path $distElectronDir) { $outDir = $distElectronDir }
else { Fail "Build output folder not found: $releaseDir or $distElectronDir" }

try { Start-Process explorer.exe $outDir } catch {}

$latestExe = Get-ChildItem -Path $outDir -Filter *.exe -Recurse -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($null -eq $latestExe) { Fail "No .exe found in $outDir" }

Write-Host "`nLaunching installer: $($latestExe.FullName)" -ForegroundColor Green
try { Start-Process -FilePath $latestExe.FullName } catch { Fail "Failed to launch EXE: $($_.Exception.Message)" }

Write-Host "`nSuccess. Log: $LogPath" -ForegroundColor Green
Always-PauseAndExit 0