@echo off
setlocal
CALL %~dp0build_exe.bat

REM Create MSI using WiX if available, else zip the folder
where candle.exe >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
  echo WiX not found. Creating zip instead...
  powershell -Command "Compress-Archive -Path 'dist/NovaExplorer/*' -DestinationPath 'dist/NovaExplorer-portable.zip' -Force"
  goto :eof
)

echo MSI creation not fully implemented in this script. Please use WiX toolset.
endlocal
