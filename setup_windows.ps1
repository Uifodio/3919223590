# Windows PowerShell Setup Script for Workspace Server
# Run as Administrator for best results

Write-Host "Setting up Windows-Compatible Workspace Server..." -ForegroundColor Green
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator. Some features may not work properly." -ForegroundColor Yellow
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js installation
Write-Host "Checking Node.js installation..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js not found. Installing Node.js..." -ForegroundColor Yellow
    
    # Download and install Node.js
    $nodeUrl = "https://nodejs.org/dist/latest-v18.x/node-v18.19.0-x64.msi"
    $nodeInstaller = "$env:TEMP\nodejs-installer.msi"
    
    try {
        Write-Host "Downloading Node.js installer..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller
        
        Write-Host "Installing Node.js..." -ForegroundColor Cyan
        Start-Process msiexec.exe -Wait -ArgumentList "/i $nodeInstaller /quiet"
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        # Verify installation
        $nodeVersion = node --version 2>&1
        Write-Host "Node.js installed: $nodeVersion" -ForegroundColor Green
        
        # Clean up
        Remove-Item $nodeInstaller -Force
    } catch {
        Write-Host "Failed to install Node.js automatically. Please install manually from https://nodejs.org" -ForegroundColor Red
    }
}

# Check PHP installation
Write-Host "Checking PHP installation..." -ForegroundColor Cyan
try {
    $phpVersion = php --version 2>&1
    Write-Host "Found: $phpVersion" -ForegroundColor Green
} catch {
    Write-Host "PHP not found. Installing PHP..." -ForegroundColor Yellow
    
    # Download and install PHP
    $phpUrl = "https://windows.php.net/downloads/releases/php-8.2.14-Win32-vs16-x64.zip"
    $phpZip = "$env:TEMP\php.zip"
    $phpDir = "C:\php"
    
    try {
        Write-Host "Downloading PHP..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $phpUrl -OutFile $phpZip
        
        Write-Host "Extracting PHP..." -ForegroundColor Cyan
        Expand-Archive -Path $phpZip -DestinationPath $phpDir -Force
        
        # Add PHP to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
        if ($currentPath -notlike "*$phpDir*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$phpDir", "Machine")
            $env:PATH += ";$phpDir"
        }
        
        # Copy php.ini
        Copy-Item "$phpDir\php.ini-development" "$phpDir\php.ini"
        
        # Verify installation
        $phpVersion = php --version 2>&1
        Write-Host "PHP installed: $phpVersion" -ForegroundColor Green
        
        # Clean up
        Remove-Item $phpZip -Force
    } catch {
        Write-Host "Failed to install PHP automatically. Please install manually from https://php.net" -ForegroundColor Red
    }
}

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv") {
    Remove-Item "venv" -Recurse -Force
}
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install flask requests psutil

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Cyan
$directories = @("projects", "logs", "templates", "static", "static\css", "static\js")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Create requirements.txt
Write-Host "Creating requirements.txt..." -ForegroundColor Cyan
@"
flask>=3.0.0
requests>=2.32.0
psutil>=5.9.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Create desktop shortcut
Write-Host "Creating desktop shortcut..." -ForegroundColor Cyan
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Workspace Server.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-Command `"cd '$PWD'; .\start_server.bat`""
$Shortcut.WorkingDirectory = $PWD
$Shortcut.Description = "Windows-Compatible Workspace Server"
$Shortcut.Save()

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "You can now run start_server.bat to start the server" -ForegroundColor Cyan
Write-Host "Or double-click the 'Workspace Server' shortcut on your desktop" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"