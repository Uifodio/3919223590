# Anora Editor - Windows File Association Installer
# Run this script as Administrator to register Anora Editor as default editor

param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AnoraPath = Join-Path $ScriptDir "anora_editor.py"
$PythonPath = "python"

# Check if Python is available
try {
    $null = & $PythonPath --version
} catch {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.7+ and try again."
    exit 1
}

# Check if Anora Editor exists
if (-not (Test-Path $AnoraPath)) {
    Write-Error "Anora Editor not found at: $AnoraPath"
    exit 1
}

# File extensions to register
$Extensions = @(
    ".py", ".cs", ".js", ".html", ".css", ".json", ".txt", ".c", ".cpp", ".h"
)

if ($Uninstall) {
    Write-Host "Uninstalling Anora Editor file associations..."
    
    foreach ($ext in $Extensions) {
        try {
            # Remove file association
            $ProgId = "AnoraEditor$ext"
            Remove-Item "HKCR:$ProgId" -Recurse -Force -ErrorAction SilentlyContinue
            Remove-Item "HKCR:$ext" -Force -ErrorAction SilentlyContinue
            
            Write-Host "Removed association for $ext"
        } catch {
            Write-Warning "Could not remove association for $ext : $($_.Exception.Message)"
        }
    }
    
    Write-Host "Uninstallation complete!"
} else {
    Write-Host "Installing Anora Editor as default editor..."
    
    foreach ($ext in $Extensions) {
        try {
            # Create ProgID
            $ProgId = "AnoraEditor$ext"
            
            # Register the application
            New-Item "HKCR:$ProgId" -Force | Out-Null
            New-Item "HKCR:$ProgId\shell" -Force | Out-Null
            New-Item "HKCR:$ProgId\shell\open" -Force | Out-Null
            New-Item "HKCR:$ProgId\shell\open\command" -Force | Out-Null
            
            # Set the command
            $Command = "`"$PythonPath`" `"$AnoraPath`" `"%1`""
            Set-ItemProperty "HKCR:$ProgId\shell\open\command" -Name "(Default)" -Value $Command
            
            # Set friendly name
            Set-ItemProperty "HKCR:$ProgId" -Name "(Default)" -Value "Anora Editor Document"
            
            # Associate file extension with ProgID
            New-Item "HKCR:$ext" -Force | Out-Null
            Set-ItemProperty "HKCR:$ext" -Name "(Default)" -Value $ProgId
            
            Write-Host "Registered $ext with Anora Editor"
        } catch {
            Write-Warning "Could not register $ext : $($_.Exception.Message)"
        }
    }
    
    Write-Host "Installation complete!"
    Write-Host "You can now double-click files to open them in Anora Editor."
    Write-Host "To uninstall, run: .\install_windows_default_editor.ps1 -Uninstall"
}