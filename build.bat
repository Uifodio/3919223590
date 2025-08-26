@echo off
echo ========================================
echo Windows File Manager Pro - Build Script
echo ========================================
echo.

REM Check if .NET 9.0 is installed
echo Checking .NET 9.0 installation...
dotnet --version 2>nul
if errorlevel 1 (
    echo ERROR: .NET 9.0 is not installed or not in PATH
    echo Please install .NET 9.0 Desktop Runtime from:
    echo https://dotnet.microsoft.com/download/dotnet/9.0
    pause
    exit /b 1
)

echo .NET version found: 
dotnet --version
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "bin" rmdir /s /q "bin"
if exist "obj" rmdir /s /q "obj"
echo Cleaned.
echo.

REM Restore packages
echo Restoring NuGet packages...
dotnet restore
if errorlevel 1 (
    echo ERROR: Failed to restore packages
    pause
    exit /b 1
)
echo Packages restored successfully.
echo.

REM Build in Release mode
echo Building in Release mode...
dotnet build -c Release --no-restore
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo Build completed successfully.
echo.

REM Publish single file
echo Publishing single file executable...
dotnet publish -c Release -r win-x64 --self-contained false -p:PublishSingleFile=true -p:PublishTrimmed=false --no-restore
if errorlevel 1 (
    echo ERROR: Publish failed
    pause
    exit /b 1
)
echo Publish completed successfully.
echo.

REM Show results
echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Output location: bin\Release\net9.0-windows\win-x64\publish\
echo Executable: WindowsFileManagerPro.exe
echo.
echo You can now run the application from the publish folder.
echo.

REM Open output folder
echo Opening output folder...
start "" "bin\Release\net9.0-windows\win-x64\publish\"
echo.

pause