# Windows File Manager Pro Build Script
# Run this script in PowerShell with execution policy: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "Building Windows File Manager Pro..." -ForegroundColor Green
Write-Host ""

# Check if .NET 6.0 is installed
try {
    $dotnetVersion = dotnet --version
    Write-Host ".NET version: $dotnetVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: .NET 6.0 is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install .NET 6.0 Desktop Runtime from: https://dotnet.microsoft.com/download/dotnet/6.0" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "bin") { Remove-Item -Path "bin" -Recurse -Force }
if (Test-Path "obj") { Remove-Item -Path "obj" -Recurse -Force }
Write-Host ""

# Restore packages
Write-Host "Restoring NuGet packages..." -ForegroundColor Yellow
dotnet restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to restore packages" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Build project
Write-Host "Building project..." -ForegroundColor Yellow
dotnet build --configuration Release --no-restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Publish application
Write-Host "Publishing application..." -ForegroundColor Yellow
dotnet publish --configuration Release --output "bin\Release\publish" --self-contained false --runtime win-x64
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Publish failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Output location: bin\Release\publish\" -ForegroundColor Cyan
Write-Host "Executable: bin\Release\publish\WindowsFileManagerPro.exe" -ForegroundColor Cyan
Write-Host ""

# Create ZIP archive
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
try {
    $publishPath = "bin\Release\publish"
    $zipPath = "WindowsFileManagerPro-Release.zip"
    
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path "$publishPath\*" -DestinationPath $zipPath -Force
    Write-Host "ZIP archive created: $zipPath" -ForegroundColor Green
} catch {
    Write-Host "Warning: Failed to create ZIP archive" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Build process completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"