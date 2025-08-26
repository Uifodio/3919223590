# ========================================
# Windows File Manager Pro - Build Script
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows File Manager Pro - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .NET 9.0 is installed
Write-Host "Checking .NET 9.0 installation..." -ForegroundColor Yellow
try {
    $dotnetVersion = dotnet --version
    if ($LASTEXITCODE -ne 0) {
        throw "dotnet command failed"
    }
    Write-Host ".NET version found: $dotnetVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: .NET 9.0 is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install .NET 9.0 Desktop Runtime from:" -ForegroundColor Yellow
    Write-Host "https://dotnet.microsoft.com/download/dotnet/9.0" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "bin") { Remove-Item "bin" -Recurse -Force }
if (Test-Path "obj") { Remove-Item "obj" -Recurse -Force }
Write-Host "Cleaned." -ForegroundColor Green
Write-Host ""

# Restore packages
Write-Host "Restoring NuGet packages..." -ForegroundColor Yellow
dotnet restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to restore packages" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Packages restored successfully." -ForegroundColor Green
Write-Host ""

# Build in Release mode
Write-Host "Building in Release mode..." -ForegroundColor Yellow
dotnet build -c Release --no-restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Build completed successfully." -ForegroundColor Green
Write-Host ""

# Publish single file
Write-Host "Publishing single file executable..." -ForegroundColor Yellow
dotnet publish -c Release -r win-x64 --self-contained false -p:PublishSingleFile=true -p:PublishTrimmed=false --no-restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Publish failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Publish completed successfully." -ForegroundColor Green
Write-Host ""

# Show results
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output location: bin\Release\net9.0-windows\win-x64\publish\" -ForegroundColor White
Write-Host "Executable: WindowsFileManagerPro.exe" -ForegroundColor White
Write-Host ""
Write-Host "You can now run the application from the publish folder." -ForegroundColor White
Write-Host ""

# Open output folder
Write-Host "Opening output folder..." -ForegroundColor Yellow
$outputPath = "bin\Release\net9.0-windows\win-x64\publish\"
if (Test-Path $outputPath) {
    Start-Process "explorer.exe" -ArgumentList $outputPath
    Write-Host "Output folder opened." -ForegroundColor Green
} else {
    Write-Host "Warning: Output folder not found" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"