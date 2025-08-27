# Unity Code Editor - Build Script (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Unity Code Editor - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run diagnostic
Write-Host "[1/5] Running system diagnostic..." -ForegroundColor Yellow
try {
    node diagnostic.js
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Diagnostic failed! Please fix the errors above." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Diagnostic passed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to run diagnostic: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 2: Install dependencies
Write-Host "[2/5] Installing dependencies..." -ForegroundColor Yellow
try {
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 3: Test the application
Write-Host "[3/5] Testing the application..." -ForegroundColor Yellow
Write-Host "Starting the app in test mode..." -ForegroundColor Gray
try {
    Start-Process npm -ArgumentList "start" -Wait
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Application test failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Application test passed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to test application: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 4: Build Windows executable
Write-Host "[4/5] Building Windows executable..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
try {
    npm run build-win
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✅ Build completed!" -ForegroundColor Green
} catch {
    Write-Host "❌ Build failed: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

# Step 5: Check output
Write-Host "[5/5] Checking output..." -ForegroundColor Yellow
if (Test-Path "dist\Unity Code Editor Setup.exe") {
    Write-Host "✅ Executable created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📁 Your executable is located at:" -ForegroundColor Cyan
    Write-Host "   dist\Unity Code Editor Setup.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Build process completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To install the app:" -ForegroundColor Cyan
    Write-Host "1. Double-click 'Unity Code Editor Setup.exe'" -ForegroundColor White
    Write-Host "2. Follow the installation wizard" -ForegroundColor White
    Write-Host "3. Launch from Start Menu or Desktop shortcut" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Executable not found in dist folder!" -ForegroundColor Red
    Write-Host "Please check the build output above for errors." -ForegroundColor Yellow
}

Read-Host "Press Enter to exit"