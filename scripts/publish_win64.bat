@echo off
setlocal
set ROOT=%~dp0..
set SRC=%ROOT%\src\AAAFileManager
set OUT=%ROOT%\dist\AAAFileManager
if not exist "%OUT%" mkdir "%OUT%"
dotnet publish "%SRC%\AAAFileManager.csproj" -c Release -r win-x64 -f net9.0-windows10.0.19041.0 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o "%OUT%"
exit /b %ERRORLEVEL%