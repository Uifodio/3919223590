# Anora Editor - Professional Windows Installation
# Run as Administrator for full functionality
param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

# Professional header
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    ANORA EDITOR INSTALLER                   ║" -ForegroundColor Cyan
Write-Host "║              Professional Code Editor for Unity             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "   Some features may not work properly" -ForegroundColor Yellow
    Write-Host ""
}

# Resolve Python and script paths
Write-Host "🔍 Detecting Python installation..." -ForegroundColor Green
$python = (Get-Command python.exe -ErrorAction SilentlyContinue)?.Source
if (-not $python) { 
    $python = (Get-Command python3.exe -ErrorAction SilentlyContinue)?.Source 
}
if (-not $python) { 
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    Write-Host "   Please install Python and add it to PATH" -ForegroundColor Red
    exit 1
}

$scriptPath = (Resolve-Path "anora_editor.py").Path
if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ anora_editor.py not found in current directory" -ForegroundColor Red
    exit 1
}

$cmd = '"' + $python + '" "' + $scriptPath + '" "%1"'

Write-Host "✅ Python: $python" -ForegroundColor Green
Write-Host "✅ Script: $scriptPath" -ForegroundColor Green
Write-Host ""

# Application registration
Write-Host "📝 Registering Anora Editor as Windows application..." -ForegroundColor Green

$progId = 'Anora.Editor'
$description = 'Anora Editor - Professional Code Editor for Unity'
$appName = 'Anora Editor'

# Create application registration
New-Item -Path "HKCU:\Software\Classes\$progId" -Force | Out-Null
New-Item -Path "HKCU:\Software\Classes\$progId\shell\open\command" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId" -Name '(Default)' -Value $description
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId\shell\open\command" -Name '(Default)' -Value $cmd

# Add application info
New-Item -Path "HKCU:\Software\Classes\$progId\shell\open" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\Classes\$progId\shell\open" -Name 'FriendlyAppName' -Value $appName

# Add icon if available
$iconPath = Join-Path (Get-Location) "anora_icon.ico"
if (Test-Path $iconPath) {
    New-Item -Path "HKCU:\Software\Classes\$progId\DefaultIcon" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\$progId\DefaultIcon" -Name '(Default)' -Value $iconPath
    Write-Host "✅ Custom icon registered" -ForegroundColor Green
}

# File associations
Write-Host "📁 Registering file associations..." -ForegroundColor Green
$extensions = @{
    '.txt' = 'Text Document'
    '.py' = 'Python File'
    '.cs' = 'C# Source File'
    '.js' = 'JavaScript File'
    '.html' = 'HTML Document'
    '.css' = 'CSS File'
    '.json' = 'JSON File'
    '.c' = 'C Source File'
    '.cpp' = 'C++ Source File'
    '.h' = 'C/C++ Header File'
    '.xml' = 'XML Document'
    '.md' = 'Markdown Document'
    '.php' = 'PHP File'
    '.java' = 'Java Source File'
    '.rb' = 'Ruby File'
    '.sql' = 'SQL File'
    '.sh' = 'Shell Script'
    '.bat' = 'Batch File'
    '.ps1' = 'PowerShell Script'
}

foreach ($ext in $extensions.Keys) {
    $desc = $extensions[$ext]
    Write-Host "  Registering $ext ($desc)" -ForegroundColor Gray
    
    # Create extension registration
    New-Item -Path "HKCU:\Software\Classes\$ext" -Force | Out-Null
    Set-ItemProperty -Path "HKCU:\Software\Classes\$ext" -Name '(Default)' -Value $progId
    
    # Add description
    Set-ItemProperty -Path "HKCU:\Software\Classes\$ext" -Name 'Content Type' -Value 'text/plain'
}

# Context menu integration
Write-Host "🖱️  Adding context menu integration..." -ForegroundColor Green

# "Open with Anora Editor" for all files
$menuPath = "HKCU:\Software\Classes\*\shell\OpenWithAnora"
New-Item -Path $menuPath -Force | Out-Null
Set-ItemProperty -Path $menuPath -Name '(Default)' -Value 'Open with Anora Editor'
Set-ItemProperty -Path $menuPath -Name 'Icon' -Value $cmd
New-Item -Path "$menuPath\command" -Force | Out-Null
Set-ItemProperty -Path "$menuPath\command" -Name '(Default)' -Value $cmd

# "Edit with Anora Editor" for text files
$editMenuPath = "HKCU:\Software\Classes\*\shell\EditWithAnora"
New-Item -Path $editMenuPath -Force | Out-Null
Set-ItemProperty -Path $editMenuPath -Name '(Default)' -Value 'Edit with Anora Editor'
Set-ItemProperty -Path $editMenuPath -Name 'Icon' -Value $cmd
New-Item -Path "$editMenuPath\command" -Force | Out-Null
Set-ItemProperty -Path "$editMenuPath\command" -Name '(Default)' -Value $cmd

# Set as default for common text files
Write-Host "⭐ Setting as default editor..." -ForegroundColor Green

$defaultExts = @('.txt', '.py', '.cs', '.js', '.html', '.css', '.json')
foreach ($ext in $defaultExts) {
    $userChoicePath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$ext\UserChoice"
    if (Test-Path $userChoicePath) {
        Set-ItemProperty -Path $userChoicePath -Name "Progid" -Value $progId -Force
        Write-Host "  Set as default for $ext" -ForegroundColor Gray
    }
}

# Refresh Windows shell
Write-Host "🔄 Refreshing Windows shell..." -ForegroundColor Green
try {
    $shell = New-Object -ComObject Shell.Application
    $shell.RefreshDesktop()
    Write-Host "✅ Desktop refreshed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not refresh desktop (this is normal)" -ForegroundColor Yellow
}

# Create desktop shortcut
Write-Host "🖥️  Creating desktop shortcut..." -ForegroundColor Green
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Anora Editor.lnk"

try {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $python
    $Shortcut.Arguments = "`"$scriptPath`""
    $Shortcut.WorkingDirectory = (Get-Location)
    $Shortcut.Description = "Anora Editor - Professional Code Editor for Unity"
    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = $iconPath
    }
    $Shortcut.Save()
    Write-Host "✅ Desktop shortcut created" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not create desktop shortcut" -ForegroundColor Yellow
}

# Installation complete
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    INSTALLATION COMPLETE!                   ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🎉 Anora Editor is now registered as a professional Windows application!" -ForegroundColor Green
Write-Host ""

Write-Host "📋 What you can now do:" -ForegroundColor Yellow
Write-Host "  • Double-click any code file to open in Anora Editor" -ForegroundColor White
Write-Host "  • Right-click files → 'Open with Anora Editor'" -ForegroundColor White
Write-Host "  • Drag and drop files onto Anora Editor window" -ForegroundColor White
Write-Host "  • Use 'Anora Editor' desktop shortcut" -ForegroundColor White
Write-Host "  • Command line: anora_editor.py file.py" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  Important:" -ForegroundColor Yellow
Write-Host "  • Restart File Explorer or log out/in for all changes to take effect" -ForegroundColor White
Write-Host "  • If files don't open, right-click → 'Open with' → 'Choose another app' → 'Anora Editor'" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")