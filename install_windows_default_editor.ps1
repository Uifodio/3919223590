# Nexus Editor Windows Installation Script
# This script registers file types and creates file associations
# Run as Administrator for best results

param(
    [switch]$Force,
    [string]$InstallPath = $PSScriptRoot
)

# Set execution policy to allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

Write-Host "Nexus Editor Windows Installation" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "For best results, run this script as Administrator." -ForegroundColor Yellow
    Write-Host ""
}

# Check if the app directory exists
if (-not (Test-Path $InstallPath)) {
    Write-Host "Error: Install directory not found at $InstallPath" -ForegroundColor Red
    exit 1
}

# Check if the executable exists
$exePath = Join-Path $InstallPath "nexus-editor.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "Warning: Nexus Editor executable not found. Please build the app first." -ForegroundColor Yellow
    Write-Host "Run: npm run dist" -ForegroundColor Yellow
    Write-Host ""
}

# File extensions to register
$fileExtensions = @(
    ".cs",    # C#
    ".js",    # JavaScript
    ".jsx",   # JSX
    ".ts",    # TypeScript
    ".tsx",   # TSX
    ".py",    # Python
    ".html",  # HTML
    ".htm",   # HTML
    ".css",   # CSS
    ".json",  # JSON
    ".c",     # C
    ".cpp",   # C++
    ".h",     # Header
    ".hpp",   # C++ Header
    ".txt"    # Text
)

# MIME types for each extension
$mimeTypes = @{
    ".cs" = "text/x-csharp"
    ".js" = "text/javascript"
    ".jsx" = "text/javascript"
    ".ts" = "text/typescript"
    ".tsx" = "text/typescript"
    ".py" = "text/x-python"
    ".html" = "text/html"
    ".htm" = "text/html"
    ".css" = "text/css"
    ".json" = "application/json"
    ".c" = "text/x-c"
    ".cpp" = "text/x-c++"
    ".h" = "text/x-c"
    ".hpp" = "text/x-c++"
    ".txt" = "text/plain"
}

Write-Host "Registering file associations..." -ForegroundColor Cyan

foreach ($ext in $fileExtensions) {
    try {
        # Get the MIME type
        $mimeType = $mimeTypes[$ext]
        
        # Create ProgID
        $progId = "NexusEditor$ext"
        
        # Register the file extension
        $regPath = "HKCR:\$ext"
        if (-not (Test-Path $regPath)) {
            New-Item -Path $regPath -Force | Out-Null
        }
        
        # Set the default value to our ProgID
        Set-ItemProperty -Path $regPath -Name "(Default)" -Value $progId
        
        # Create ProgID key
        $progIdPath = "HKCR:\$progId"
        if (-not (Test-Path $progIdPath)) {
            New-Item -Path $progIdPath -Force | Out-Null
        }
        
        # Set friendly name
        Set-ItemProperty -Path $progIdPath -Name "(Default)" -Value "Nexus Editor Document"
        
        # Create shell\open\command
        $shellPath = "$progIdPath\shell\open\command"
        if (-not (Test-Path $shellPath)) {
            New-Item -Path $shellPath -Force | Out-Null
        }
        
        # Set the command to open with Nexus Editor
        $command = "`"$exePath`" `"%1`""
        Set-ItemProperty -Path $shellPath -Name "(Default)" -Value $command
        
        # Create shell\open\ddeexec
        $ddePath = "$progIdPath\shell\open\ddeexec"
        if (-not (Test-Path $ddePath)) {
            New-Item -Path $ddePath -Force | Out-Null
        }
        
        # Set DDE command
        Set-ItemProperty -Path $ddePath -Name "(Default)" -Value "[rem `"$command`"]"
        
        # Create shell\open\ddeexec\application
        $ddeAppPath = "$ddePath\application"
        if (-not (Test-Path $ddeAppPath)) {
            New-Item -Path $ddeAppPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $ddeAppPath -Name "(Default)" -Value "nexus-editor"
        
        # Create shell\open\ddeexec\topic
        $ddeTopicPath = "$ddePath\topic"
        if (-not (Test-Path $ddeTopicPath)) {
            New-Item -Path $ddeTopicPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $ddeTopicPath -Name "(Default)" -Value "system"
        
        # Set MIME type if available
        if ($mimeType) {
            $mimePath = "$progIdPath\Content Type"
            if (-not (Test-Path $mimePath)) {
                New-Item -Path $mimePath -Force | Out-Null
            }
            Set-ItemProperty -Path $mimePath -Name "(Default)" -Value $mimeType
        }
        
        Write-Host "  ✓ Registered $ext" -ForegroundColor Green
        
    } catch {
        Write-Host "  ✗ Failed to register $ext : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Register application in App Paths
Write-Host "Registering application in App Paths..." -ForegroundColor Cyan

try {
    $appPaths = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\nexus-editor.exe"
    if (-not (Test-Path $appPaths)) {
        New-Item -Path $appPaths -Force | Out-Null
    }
    
    Set-ItemProperty -Path $appPaths -Name "(Default)" -Value $exePath
    Set-ItemProperty -Path $appPaths -Name "Path" -Value $InstallPath
    
    Write-Host "  ✓ Registered in App Paths" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to register in App Paths: $($_.Exception.Message)" -ForegroundColor Red
}

# Create file type associations in Windows 10/11
Write-Host "Creating file type associations..." -ForegroundColor Cyan

try {
    foreach ($ext in $fileExtensions) {
        $assocCmd = "assoc $ext=NexusEditor$ext"
        cmd /c $assocCmd 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Associated $ext" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Associated $ext (may require admin)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  ✗ Failed to create file associations: $($_.Exception.Message)" -ForegroundColor Red
}

# Create Start Menu shortcut
Write-Host "Creating Start Menu shortcut..." -ForegroundColor Cyan

try {
    $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Nexus Editor"
    if (-not (Test-Path $startMenuPath)) {
        New-Item -Path $startMenuPath -ItemType Directory -Force | Out-Null
    }
    
    $shortcutPath = "$startMenuPath\Nexus Editor.lnk"
    $WshShell = New-Object -ComObject WScript.Shell
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $exePath
    $shortcut.WorkingDirectory = $InstallPath
    $shortcut.Description = "Professional code editor for Unity development"
    $shortcut.Save()
    
    Write-Host "  ✓ Start Menu shortcut created" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create Start Menu shortcut: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Nexus Editor has been installed with the following features:" -ForegroundColor White
Write-Host "✓ File associations registered for common development file types" -ForegroundColor White
Write-Host "✓ Application registered in Windows App Paths" -ForegroundColor White
Write-Host "✓ Start Menu shortcut created" -ForegroundColor White
Write-Host ""
Write-Host "You can now:" -ForegroundColor White
Write-Host "- Launch Nexus Editor from the Start Menu" -ForegroundColor White
Write-Host "- Double-click on code files to open them in Nexus Editor" -ForegroundColor White
Write-Host "- Right-click on files and select 'Open with > Nexus Editor'" -ForegroundColor White
Write-Host ""
Write-Host "Note: Some file associations may require a system restart to take full effect." -ForegroundColor Yellow
Write-Host ""
Write-Host "To uninstall, you can:" -ForegroundColor White
Write-Host "1. Remove the Start Menu shortcut" -ForegroundColor White
Write-Host "2. Run this script with -Force to remove registry entries" -ForegroundColor White
Write-Host "3. Delete the application directory" -ForegroundColor White