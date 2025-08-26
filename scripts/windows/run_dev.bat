@echo off
setlocal
CALL %~dp0setup_venv.bat
CALL .venv\Scripts\activate.bat
python main.py
endlocal
