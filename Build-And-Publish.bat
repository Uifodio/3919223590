@echo off
setlocal
set LOG=%TEMP%\wfmp_build_%RANDOM%.log
echo Logging to %LOG%
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-And-Publish.ps1" -LogPath "%LOG%"
if errorlevel 1 (
  echo.
  echo Build script reported errors. Log: %LOG%
  pause
  endlocal & exit /b 1
) else (
  echo.
  echo Build completed successfully. Log: %LOG%
  pause
  endlocal & exit /b 0
)