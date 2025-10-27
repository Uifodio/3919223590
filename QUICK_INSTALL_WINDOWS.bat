@echo off
title Anora Editor - Professional Installation
color 0A

echo.
echo ========================================
echo    ANORA EDITOR - WINDOWS INSTALLER
echo ========================================
echo.

echo Installing dependencies...
pip install --user --break-system-packages -r requirements.txt

echo.
echo Running professional installer...
powershell -ExecutionPolicy Bypass -File "install_windows_professional.ps1"

echo.
echo Installation complete!
echo Please restart File Explorer or log out/in.
echo.
pause