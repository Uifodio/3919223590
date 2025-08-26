@echo off
echo Building Windows File Manager Pro...
echo.

REM Check if .NET 6.0 is installed
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: .NET 6.0 is not installed or not in PATH
    echo Please install .NET 6.0 Desktop Runtime from: https://dotnet.microsoft.com/download/dotnet/6.0
    pause
    exit /b 1
)

echo .NET version:
dotnet --version
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "bin" rmdir /s /q "bin"
if exist "obj" rmdir /s /q "obj"
echo.

REM Restore packages
echo Restoring NuGet packages...
dotnet restore
if %errorlevel% neq 0 (
    echo ERROR: Failed to restore packages
    pause
    exit /b 1
)
echo.

REM Build project
echo Building project...
dotnet build --configuration Release --no-restore
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo.

REM Publish application
echo Publishing application...
dotnet publish --configuration Release --output "bin\Release\publish" --self-contained false --runtime win-x64
if %errorlevel% neq 0 (
    echo ERROR: Publish failed
    pause
    exit /b 1
)
echo.

echo Build completed successfully!
echo.
echo Output location: bin\Release\publish\
echo Executable: bin\Release\publish\WindowsFileManagerPro.exe
echo.

REM Create ZIP archive
echo Creating ZIP archive...
powershell -command "Compress-Archive -Path 'bin\Release\publish\*' -DestinationPath 'WindowsFileManagerPro-Release.zip' -Force"
if %errorlevel% equ 0 (
    echo ZIP archive created: WindowsFileManagerPro-Release.zip
) else (
    echo Warning: Failed to create ZIP archive
)
echo.

echo Build process completed!
pause