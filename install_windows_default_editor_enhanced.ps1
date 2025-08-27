# Enhanced Windows File Association Installer
# Run as Administrator for best results
$ErrorActionPreference = 'Stop'

Write-Host "Anora Editor - Windows File Association Installer" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Resolve paths
$python = (Get-Command python.exe -ErrorAction SilentlyContinue)?.Source
if (-not $python) { $python = (Get-Command python3.exe -ErrorAction SilentlyContinue)?.Source }
if (-not $python) { throw "Python not found in PATH. Please install Python or add it to PATH." }

$scriptPath = (Resolve-Path "anora_editor.py").Path
$cmd = '"' + $python + '" "' + $scriptPath + '" "%1"'

Write-Host "Python: $python" -ForegroundColor Yellow
Write-Host "Script: $scriptPath" -ForegroundColor Yellow
Write-Host "Command: $cmd" -ForegroundColor Yellow

# ProgID
$progId = 'Anora.Editor'
$description = 'Anora Editor - Lightweight Professional Code Editor'

Write-Host "`nCreating file associations..." -ForegroundColor Cyan

# Create ProgID under HKCU
New-Item -Path "HKCU:\Software\Classes\$progId" -Force | Out-Null
New-Item -Path "HKCU:\Software\Classes\$progId\shell\open\command" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId" -Name '(Default)' -Value $description
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId\shell\open\command" -Name '(Default)' -Value $cmd

# Add icon (if available)
$iconPath = Join-Path (Get-Location) "anora_icon.ico"
if (Test-Path $iconPath) {
    New-Item -Path "HKCU:\Software\Classes\$progId\DefaultIcon" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\$progId\DefaultIcon" -Name '(Default)' -Value $iconPath
}

# Associate extensions
$exts = @('.txt', '.py', '.cs', '.js', '.html', '.css', '.json', '.c', '.cpp', '.h', '.xml', '.md')
foreach ($ext in $exts) {
    Write-Host "  Registering $ext" -ForegroundColor Gray
    New-Item -Path "HKCU:\Software\Classes\$ext" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\$ext" -Name '(Default)' -Value $progId
}

# Context menu: Open with Anora Editor
$menuPath = "HKCU:\Software\Classes\*\shell\OpenWithAnora"
New-Item -Path $menuPath -Force | Out-Null
Set-ItemProperty -Path $menuPath -Name '(Default)' -Value 'Open with Anora Editor'
New-Item -Path "$menuPath\command" -Force | Out-Null
Set-ItemProperty -Path "$menuPath\command" -Name '(Default)' -Value $cmd

# Set as default for text files
Write-Host "`nSetting as default editor..." -ForegroundColor Cyan
$textProgId = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.txt\UserChoice"
if (Test-Path $textProgId) {
    Set-ItemProperty -Path $textProgId -Name "Progid" -Value $progId -Force
    Write-Host "  Set as default for .txt files" -ForegroundColor Gray
}

# Force Windows to recognize the changes
Write-Host "`nRefreshing Windows associations..." -ForegroundColor Cyan
try {
    # Refresh shell
    $shell = New-Object -ComObject Shell.Application
    $shell.RefreshDesktop()
    Write-Host "  Desktop refreshed" -ForegroundColor Gray
} catch {
    Write-Host "  Could not refresh desktop (this is normal)" -ForegroundColor Yellow
}

Write-Host "`n✅ Installation Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Restart File Explorer (or log out/in)" -ForegroundColor White
Write-Host "2. Right-click any .py, .cs, .js file and select 'Open with Anora Editor'" -ForegroundColor White
Write-Host "3. Or double-click files to open them directly" -ForegroundColor White
Write-Host "4. Drag and drop files onto the Anora Editor window" -ForegroundColor White

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")