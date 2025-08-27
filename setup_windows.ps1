# PowerShell script for setting up Kivy Counter App on Windows

Write-Host "Setting up Kivy Counter App for Windows..." -ForegroundColor Green
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "kivy_env") {
    Write-Host "Virtual environment already exists, removing..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "kivy_env"
}

python -m venv kivy_env
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create virtual environment!" -ForegroundColor Red
    Write-Host "Make sure python3-venv is installed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "kivy_env\Scripts\Activate.ps1"

# Install Kivy
Write-Host ""
Write-Host "Installing Kivy..." -ForegroundColor Yellow
pip install kivy>=2.3.0
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install Kivy!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install PyInstaller
Write-Host ""
Write-Host "Installing PyInstaller for compilation..." -ForegroundColor Yellow
pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to install PyInstaller!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Test installation
Write-Host ""
Write-Host "Testing installation..." -ForegroundColor Yellow
python test_installation.py

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "To run the app:" -ForegroundColor Cyan
Write-Host "1. Activate the environment: kivy_env\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Run the app: python main.py" -ForegroundColor White
Write-Host "3. To compile: pyinstaller CounterApp.spec" -ForegroundColor White

Read-Host "Press Enter to exit"