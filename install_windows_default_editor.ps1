# Anora Editor - Windows File Association Installer
# Run this script as Administrator to set Anora as default editor

param(
    [switch]$Uninstall
)

# Get the current directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EditorPath = Join-Path $ScriptDir "anora_editor.py"
$PythonPath = "python"

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script must be run as Administrator to modify file associations." -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Function to create file association
function Set-FileAssociation {
    param(
        [string]$Extension,
        [string]$Description,
        [string]$IconPath
    )
    
    $ProgId = "AnoraEditor.$Extension"
    $Command = "`"$PythonPath`" `"$EditorPath`" `"%1`""
    
    try {
        # Create ProgId
        New-Item -Path "HKLM:\SOFTWARE\Classes\$ProgId" -Force | Out-Null
        New-ItemProperty -Path "HKLM:\SOFTWARE\Classes\$ProgId" -Name "(Default)" -Value $Description -PropertyType String | Out-Null
        
        # Set icon
        if ($IconPath) {
            New-ItemProperty -Path "HKLM:\SOFTWARE\Classes\$ProgId\DefaultIcon" -Name "(Default)" -Value $IconPath -PropertyType String | Out-Null
        }
        
        # Set open command
        New-Item -Path "HKLM:\SOFTWARE\Classes\$ProgId\shell\open\command" -Force | Out-Null
        New-ItemProperty -Path "HKLM:\SOFTWARE\Classes\$ProgId\shell\open\command" -Name "(Default)" -Value $Command -PropertyType String | Out-Null
        
        # Associate extension
        New-ItemProperty -Path "HKLM:\SOFTWARE\Classes\$Extension" -Name "(Default)" -Value $ProgId -PropertyType String | Out-Null
        
        Write-Host "✓ Associated $Extension with Anora Editor" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to associate $Extension: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to remove file association
function Remove-FileAssociation {
    param(
        [string]$Extension
    )
    
    $ProgId = "AnoraEditor.$Extension"
    
    try {
        # Remove ProgId
        Remove-Item -Path "HKLM:\SOFTWARE\Classes\$ProgId" -Recurse -Force -ErrorAction SilentlyContinue
        
        # Remove extension association
        Remove-ItemProperty -Path "HKLM:\SOFTWARE\Classes\$Extension" -Name "(Default)" -ErrorAction SilentlyContinue
        
        Write-Host "✓ Removed association for $Extension" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to remove association for $Extension: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Check if editor exists
if (-not (Test-Path $EditorPath)) {
    Write-Host "Error: anora_editor.py not found in the current directory." -ForegroundColor Red
    Write-Host "Please run this script from the directory containing anora_editor.py" -ForegroundColor Yellow
    exit 1
}

# Check if Python is available
try {
    $null = & $PythonPath --version
} catch {
    Write-Host "Error: Python not found. Please ensure Python is installed and in your PATH." -ForegroundColor Red
    exit 1
}

if ($Uninstall) {
    Write-Host "Uninstalling Anora Editor file associations..." -ForegroundColor Yellow
    
    $Extensions = @(".py", ".cs", ".js", ".html", ".css", ".json", ".txt", ".c", ".cpp", ".h")
    
    foreach ($ext in $Extensions) {
        Remove-FileAssociation -Extension $ext
    }
    
    Write-Host "`nUninstallation complete!" -ForegroundColor Green
} else {
    Write-Host "Installing Anora Editor as default editor..." -ForegroundColor Yellow
    Write-Host "Editor path: $EditorPath" -ForegroundColor Cyan
    Write-Host "Python path: $PythonPath" -ForegroundColor Cyan
    Write-Host ""
    
    # File associations to create
    $Associations = @{
        ".py" = "Python File"
        ".cs" = "C# Source File"
        ".js" = "JavaScript File"
        ".html" = "HTML File"
        ".css" = "CSS File"
        ".json" = "JSON File"
        ".txt" = "Text File"
        ".c" = "C Source File"
        ".cpp" = "C++ Source File"
        ".h" = "C/C++ Header File"
    }
    
    foreach ($ext in $Associations.Keys) {
        Set-FileAssociation -Extension $ext -Description $Associations[$ext]
    }
    
    Write-Host "`nInstallation complete!" -ForegroundColor Green
    Write-Host "Anora Editor is now the default editor for supported file types." -ForegroundColor Cyan
    Write-Host "You can double-click any supported file to open it in Anora." -ForegroundColor Cyan
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")