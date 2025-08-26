@echo off
setlocal
set ROOT=%~dp0
if exist "%ROOT%dist\AAAFileManager\AAAFileManager.exe" (
  echo Starting AAA File Manager from dist...
  start "" "%ROOT%dist\AAAFileManager\AAAFileManager.exe"
  exit /b 0
)
echo No built app found. Publishing self-contained win-x64 build...
call "%ROOT%scripts\publish_win64.bat"
if exist "%ROOT%dist\AAAFileManager\AAAFileManager.exe" (
  echo Launching AAA File Manager...
  start "" "%ROOT%dist\AAAFileManager\AAAFileManager.exe"
) else (
  echo Failed to build. Ensure .NET 8 SDK is installed.
)
exit /b 0