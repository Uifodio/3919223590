# Requires: Run in PowerShell (preferably as Administrator)
$ErrorActionPreference = 'Stop'

# Resolve paths
$python = (Get-Command python.exe -ErrorAction SilentlyContinue)?.Source
if (-not $python) { $python = (Get-Command python3.exe -ErrorAction SilentlyContinue)?.Source }
if (-not $python) { throw "Python not found in PATH. Please install Python or add it to PATH." }

$scriptPath = (Resolve-Path "anora_editor.py").Path
$cmd = '"' + $python + '" "' + $scriptPath + '" "%1"'

# ProgID
$progId = 'Anora.Editor'
$description = 'Anora Editor - Lightweight Professional Code Editor'

# Create ProgID under HKCU
New-Item -Path "HKCU:\Software\Classes\$progId" -Force | Out-Null
New-Item -Path "HKCU:\Software\Classes\$progId\shell\open\command" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId" -Name '(Default)' -Value $description
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId\shell\open\command" -Name '(Default)' -Value $cmd

# Associate common extensions
$exts = @('.txt', '.py', '.cs', '.js', '.html', '.css', '.json', '.c', '.cpp', '.h')
foreach ($ext in $exts) {
  New-Item -Path "HKCU:\Software\Classes\$ext" -Force | Out-Null
  Set-ItemProperty -Path "HKCU:\Software\Classes\$ext" -Name '(Default)' -Value $progId
}

# Context menu: Open with Anora Editor
$menuPath = "HKCU:\Software\Classes\*\shell\OpenWithAnora"
New-Item -Path $menuPath -Force | Out-Null
Set-ItemProperty -Path $menuPath -Name '(Default)' -Value 'Open with Anora Editor'
New-Item -Path "$menuPath\command" -Force | Out-Null
Set-ItemProperty -Path "$menuPath\command" -Name '(Default)' -Value $cmd

Write-Host "Registered Anora Editor as default/editor option for current user."