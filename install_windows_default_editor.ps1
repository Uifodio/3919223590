# Anora Editor - Windows Default Editor Installation Script
# This script sets Anora Editor as the default editor for various file types
# Run as Administrator

param(
    [switch]$Force
)

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator. Please run PowerShell as Administrator and try again."
    exit 1
}

Write-Host "Installing Anora Editor as default editor..." -ForegroundColor Green

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppDir = Split-Path -Parent $ScriptDir

# Define file associations
$FileAssociations = @(
    @{ Extension = ".py"; FileType = "Python.File"; Description = "Python File" },
    @{ Extension = ".cs"; FileType = "CSharp.File"; Description = "C# File" },
    @{ Extension = ".js"; FileType = "JavaScript.File"; Description = "JavaScript File" },
    @{ Extension = ".jsx"; FileType = "JSX.File"; Description = "JSX File" },
    @{ Extension = ".ts"; FileType = "TypeScript.File"; Description = "TypeScript File" },
    @{ Extension = ".tsx"; FileType = "TSX.File"; Description = "TSX File" },
    @{ Extension = ".html"; FileType = "HTML.File"; Description = "HTML File" },
    @{ Extension = ".htm"; FileType = "HTM.File"; Description = "HTM File" },
    @{ Extension = ".css"; FileType = "CSS.File"; Description = "CSS File" },
    @{ Extension = ".json"; FileType = "JSON.File"; Description = "JSON File" },
    @{ Extension = ".c"; FileType = "C.File"; Description = "C File" },
    @{ Extension = ".cpp"; FileType = "CPP.File"; Description = "C++ File" },
    @{ Extension = ".h"; FileType = "Header.File"; Description = "Header File" },
    @{ Extension = ".hpp"; FileType = "HPP.File"; Description = "HPP File" },
    @{ Extension = ".txt"; FileType = "Text.File"; Description = "Text File" }
)

# Create registry entries for each file type
foreach ($Association in $FileAssociations) {
    $Extension = $Association.Extension
    $FileType = $Association.FileType
    $Description = $Association.Description
    
    Write-Host "Setting up association for $Extension files..." -ForegroundColor Yellow
    
    # Create file type key
    $FileTypeKey = "HKCR:\$FileType"
    if (!(Test-Path $FileTypeKey)) {
        New-Item -Path $FileTypeKey -Force | Out-Null
    }
    
    # Set description
    Set-ItemProperty -Path $FileTypeKey -Name "(Default)" -Value $Description
    
    # Create shell/open/command key
    $CommandKey = "$FileTypeKey\shell\open\command"
    if (!(Test-Path $CommandKey)) {
        New-Item -Path $CommandKey -Force | Out-Null
    }
    
    # Set command
    $Command = "`"$AppDir\dist_electron\win-unpacked\Anora Editor.exe`" `"%1`""
    Set-ItemProperty -Path $CommandKey -Name "(Default)" -Value $Command
    
    # Create shell/edit/command key
    $EditCommandKey = "$FileTypeKey\shell\edit\command"
    if (!(Test-Path $EditCommandKey)) {
        New-Item -Path $EditCommandKey -Force | Out-Null
    }
    
    # Set edit command
    Set-ItemProperty -Path $EditCommandKey -Name "(Default)" -Value $Command
    
    # Set default program
    $ProgIdKey = "HKCR:\$FileType"
    $UserChoiceKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\$Extension\UserChoice"
    
    if (!(Test-Path $UserChoiceKey)) {
        New-Item -Path $UserChoiceKey -Force | Out-Null
    }
    
    Set-ItemProperty -Path $UserChoiceKey -Name "Progid" -Value $FileType
}

# Create application registration
$AppKey = "HKCR:\Applications\AnoraEditor.exe"
if (!(Test-Path $AppKey)) {
    New-Item -Path $AppKey -Force | Out-Null
}

# Set application properties
Set-ItemProperty -Path $AppKey -Name "FriendlyAppName" -Value "Anora Editor"
Set-ItemProperty -Path $AppKey -Name "ApplicationCompany" -Value "Anora Editor Team"
Set-ItemProperty -Path $AppKey -Name "ApplicationDescription" -Value "Professional Unity Code Editor"

# Create shell/open/command for application
$AppCommandKey = "$AppKey\shell\open\command"
if (!(Test-Path $AppCommandKey)) {
    New-Item -Path $AppCommandKey -Force | Out-Null
}

$AppCommand = "`"$AppDir\dist_electron\win-unpacked\Anora Editor.exe`" `"%1`""
Set-ItemProperty -Path $AppCommandKey -Name "(Default)" -Value $AppCommand

Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Anora Editor is now set as the default editor for:" -ForegroundColor Cyan
foreach ($Association in $FileAssociations) {
    Write-Host "  - $($Association.Extension) ($($Association.Description))" -ForegroundColor White
}
Write-Host ""
Write-Host "You may need to restart Windows Explorer for changes to take effect." -ForegroundColor Yellow
Write-Host "Registry entries created in HKEY_CLASSES_ROOT and HKEY_CURRENT_USER" -ForegroundColor Yellow

# Refresh shell
Write-Host "Refreshing shell..." -ForegroundColor Yellow
Stop-Process -Name "explorer" -Force -ErrorAction SilentlyContinue
Start-Process "explorer"

Write-Host "Installation script completed successfully!" -ForegroundColor Green