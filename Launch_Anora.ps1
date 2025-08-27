param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Args
)

$ErrorActionPreference = 'Stop'

function Write-Log([string]$Message) {
  $global:LogFile = Join-Path $PSScriptRoot 'anora_launcher.log'
  $timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
  $line = "[$timestamp] $Message"
  Add-Content -Path $global:LogFile -Value $line -Encoding UTF8
  Write-Host $line
}

Set-Location $PSScriptRoot
$venvDir = Join-Path $PSScriptRoot '.venv'
$venvPy  = Join-Path $venvDir 'Scripts\python.exe'

Write-Log 'Starting Launch_Anora.ps1'

# Find a Python to create venv
$sysPy = $null
try { & py -3 -V *> $null; if ($LASTEXITCODE -eq 0) { $sysPy = 'py -3' } } catch {}
if (-not $sysPy) {
  try { & py -V *> $null; if ($LASTEXITCODE -eq 0) { $sysPy = 'py' } } catch {}
}
if (-not $sysPy) {
  try { $p = (Get-Command python -ErrorAction Stop).Source; if ($p) { $sysPy = 'python' } } catch {}
}
if (-not $sysPy) { Write-Log 'Python not found. Install Python 3.10+.'; throw 'Python not found' }

# Create venv
if (-not (Test-Path $venvDir)) {
  Write-Log 'Creating venv...'
  & $sysPy -m venv $venvDir | Out-Null
}
if (-not (Test-Path $venvPy)) { Write-Log "venv python missing: $venvPy"; throw 'venv missing' }

# Upgrade pip
Write-Log 'Upgrading pip/setuptools/wheel...'
& $venvPy -m pip install -U pip setuptools wheel | Out-Null

# Install wxPython with retries
Write-Log 'Installing wxPython (attempt 1 with extras wheels)'
& $venvPy -m pip install -U "wxPython>=4.2.1" -f https://extras.wxpython.org/wxPython4/extras/index.html | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Log 'Installing wxPython (attempt 2 without extras)'
  & $venvPy -m pip install -U "wxPython>=4.2.1" | Out-Null
}

# Optional packages
Write-Log 'Installing optional packages (pywin32, pygments)'
& $venvPy -m pip install -U pywin32 pygments | Out-Null

# Verify
Write-Log 'Verifying wx imports in venv'
& $venvPy -c "import wx, wx.stc, wx.aui, wx.adv, wx.html, wx.grid, wx.richtext; print('wx OK')" | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Log 'wx import failed'; throw 'wx import failed' }

# Launch
Write-Log 'Launching launcher via venv'
& $venvPy "$PSScriptRoot\launch_anora.py" @Args
if ($LASTEXITCODE -ne 0) {
  Write-Log 'Launcher non-zero, launching editor directly'
  & $venvPy "$PSScriptRoot\anora_editor.py" @Args
}

Write-Log 'Launch_Anora.ps1 finished'