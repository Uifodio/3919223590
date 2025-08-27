#!/usr/bin/env python3
"""
Windows Installer for Anora Editor
Registers the application for file associations and makes it a recognized editor
"""

import os
import sys
import subprocess
import winreg
import ctypes
from pathlib import Path

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_windows_installer():
    """Create a Windows installer that registers file associations"""
    
    print("🔧 Creating Windows Installer for Anora Editor...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, "dist_windows", "AnoraEditor_Windows", "AnoraEditor_Windows.exe")
    
    if not os.path.exists(exe_path):
        print("❌ Executable not found. Please build the application first:")
        print("   python3 build_windows.py")
        return False
    
    # Create installer script
    installer_content = f'''@echo off
echo ========================================
echo    Anora Editor - Windows Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - OK
) else (
    echo ERROR: This installer must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Installing Anora Editor...

REM Create program directory
set "PROGRAM_DIR=%PROGRAMFILES%\\AnoraEditor"
if not exist "%PROGRAM_DIR%" mkdir "%PROGRAM_DIR%"

REM Copy files
echo Copying files...
xcopy /E /I /Y "{os.path.dirname(exe_path)}" "%PROGRAM_DIR%"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Anora Editor.lnk'); $Shortcut.TargetPath = '%PROGRAM_DIR%\\AnoraEditor_Windows.exe'; $Shortcut.WorkingDirectory = '%PROGRAM_DIR%'; $Shortcut.Description = 'Professional Code Editor for Unity'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
set "START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Anora Editor"
if not exist "%START_MENU%" mkdir "%START_MENU%"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\\Anora Editor.lnk'); $Shortcut.TargetPath = '%PROGRAM_DIR%\\AnoraEditor_Windows.exe'; $Shortcut.WorkingDirectory = '%PROGRAM_DIR%'; $Shortcut.Description = 'Professional Code Editor for Unity'; $Shortcut.Save()"

REM Register file associations
echo Registering file associations...
python "{os.path.join(current_dir, 'register_associations.py')}"

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Anora Editor has been installed to: %PROGRAM_DIR%
echo Desktop shortcut created
echo Start menu shortcut created
echo File associations registered
echo.
echo You can now:
echo - Double-click any code file to open with Anora Editor
echo - Right-click files and select "Open with Anora Editor"
echo - Set Anora Editor as default for code files
echo.
pause
'''
    
    installer_path = os.path.join(current_dir, "install_anora_windows.bat")
    with open(installer_path, 'w') as f:
        f.write(installer_content)
    
    print(f"✅ Windows installer created: {installer_path}")
    return True

def create_registry_script():
    """Create a script to register file associations in Windows registry"""
    
    print("🔧 Creating registry association script...")
    
    # File associations to register
    associations = {
        '.py': 'Python File',
        '.cs': 'C# File',
        '.js': 'JavaScript File',
        '.cpp': 'C++ File',
        '.c': 'C File',
        '.h': 'Header File',
        '.html': 'HTML File',
        '.css': 'CSS File',
        '.json': 'JSON File',
        '.xml': 'XML File',
        '.sh': 'Shell Script',
        '.bat': 'Batch File',
        '.ps1': 'PowerShell Script',
        '.php': 'PHP File',
        '.rb': 'Ruby File',
        '.java': 'Java File',
        '.kt': 'Kotlin File',
        '.swift': 'Swift File',
        '.go': 'Go File',
        '.rs': 'Rust File',
        '.sql': 'SQL File',
        '.md': 'Markdown File',
        '.yml': 'YAML File',
        '.yaml': 'YAML File',
        '.toml': 'TOML File',
        '.ini': 'INI File',
        '.cfg': 'Config File',
        '.conf': 'Config File'
    }
    
    registry_script = '''import winreg
import os
import sys

def register_file_association(extension, description):
    """Register a file association for Anora Editor"""
    try:
        # Get the path to Anora Editor
        program_dir = os.path.join(os.environ['PROGRAMFILES'], 'AnoraEditor')
        exe_path = os.path.join(program_dir, 'AnoraEditor_Windows.exe')
        
        if not os.path.exists(exe_path):
            print(f"❌ Anora Editor not found at: {exe_path}")
            return False
        
        # Create the file type key
        file_type_key = f"AnoraEditor{extension.replace('.', '')}"
        
        # Register the file type
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, file_type_key)
        
        # Register the file type description
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, file_type_key) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"Anora Editor - {description}")
            
            # Register the shell command
            with winreg.CreateKey(key, "shell\\open\\command") as cmd_key:
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            
            # Register the default icon
            with winreg.CreateKey(key, "DefaultIcon") as icon_key:
                winreg.SetValue(icon_key, "", winreg.REG_SZ, f'"{exe_path}",0')
        
        print(f"✅ Registered {extension} ({description})")
        return True
        
    except Exception as e:
        print(f"❌ Failed to register {extension}: {e}")
        return False

def main():
    """Register all file associations"""
    print("🔧 Registering file associations for Anora Editor...")
    
    associations = {
        '.py': 'Python File',
        '.cs': 'C# File',
        '.js': 'JavaScript File',
        '.cpp': 'C++ File',
        '.c': 'C File',
        '.h': 'Header File',
        '.html': 'HTML File',
        '.css': 'CSS File',
        '.json': 'JSON File',
        '.xml': 'XML File',
        '.sh': 'Shell Script',
        '.bat': 'Batch File',
        '.ps1': 'PowerShell Script',
        '.php': 'PHP File',
        '.rb': 'Ruby File',
        '.java': 'Java File',
        '.kt': 'Kotlin File',
        '.swift': 'Swift File',
        '.go': 'Go File',
        '.rs': 'Rust File',
        '.sql': 'SQL File',
        '.md': 'Markdown File',
        '.yml': 'YAML File',
        '.yaml': 'YAML File',
        '.toml': 'TOML File',
        '.ini': 'INI File',
        '.cfg': 'Config File',
        '.conf': 'Config File'
    }
    
    success_count = 0
    total_count = len(associations)
    
    for extension, description in associations.items():
        if register_file_association(extension, description):
            success_count += 1
    
    print(f"\\n📊 Registration complete: {success_count}/{total_count} file types registered")
    
    if success_count > 0:
        print("\\n🎉 Anora Editor is now registered as a recognized application!")
        print("You can now:")
        print("- Double-click any code file to open with Anora Editor")
        print("- Right-click files and select 'Open with Anora Editor'")
        print("- Set Anora Editor as default for code files")
    else:
        print("\\n❌ No file associations were registered. Please run as Administrator.")

if __name__ == "__main__":
    main()
'''
    
    registry_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "register_associations.py")
    with open(registry_path, 'w') as f:
        f.write(registry_script)
    
    print(f"✅ Registry script created: {registry_path}")
    return True

def create_uninstaller():
    """Create an uninstaller script"""
    
    print("🔧 Creating uninstaller...")
    
    uninstaller_content = '''@echo off
echo ========================================
echo    Anora Editor - Uninstaller
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - OK
) else (
    echo ERROR: This uninstaller must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Uninstalling Anora Editor...

REM Remove program directory
set "PROGRAM_DIR=%PROGRAMFILES%\\AnoraEditor"
if exist "%PROGRAM_DIR%" (
    echo Removing program files...
    rmdir /S /Q "%PROGRAM_DIR%"
)

REM Remove desktop shortcut
if exist "%USERPROFILE%\\Desktop\\Anora Editor.lnk" (
    echo Removing desktop shortcut...
    del "%USERPROFILE%\\Desktop\\Anora Editor.lnk"
)

REM Remove start menu shortcut
set "START_MENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Anora Editor"
if exist "%START_MENU%" (
    echo Removing start menu shortcuts...
    rmdir /S /Q "%START_MENU%"
)

REM Remove file associations
echo Removing file associations...
python "unregister_associations.py"

echo.
echo ========================================
echo    Uninstallation Complete!
echo ========================================
echo.
echo Anora Editor has been removed from your system.
echo.
pause
'''
    
    uninstaller_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uninstall_anora.bat")
    with open(uninstaller_path, 'w') as f:
        f.write(uninstaller_content)
    
    print(f"✅ Uninstaller created: {uninstaller_path}")
    return True

def create_unregister_script():
    """Create a script to unregister file associations"""
    
    print("🔧 Creating unregister script...")
    
    unregister_script = '''import winreg
import os

def unregister_file_association(extension):
    """Unregister a file association"""
    try:
        file_type_key = f"AnoraEditor{extension.replace('.', '')}"
        
        # Remove the file type registration
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, file_type_key)
        except:
            pass
        
        # Remove the extension association
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, extension)
        except:
            pass
        
        print(f"✅ Unregistered {extension}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to unregister {extension}: {e}")
        return False

def main():
    """Unregister all file associations"""
    print("🔧 Unregistering file associations for Anora Editor...")
    
    extensions = [
        '.py', '.cs', '.js', '.cpp', '.c', '.h', '.html', '.css', '.json', '.xml',
        '.sh', '.bat', '.ps1', '.php', '.rb', '.java', '.kt', '.swift', '.go', '.rs',
        '.sql', '.md', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf'
    ]
    
    success_count = 0
    total_count = len(extensions)
    
    for extension in extensions:
        if unregister_file_association(extension):
            success_count += 1
    
    print(f"\\n📊 Unregistration complete: {success_count}/{total_count} file types unregistered")

if __name__ == "__main__":
    main()
'''
    
    unregister_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "unregister_associations.py")
    with open(unregister_path, 'w') as f:
        f.write(unregister_script)
    
    print(f"✅ Unregister script created: {unregister_path}")
    return True

def main():
    """Main installer creation process"""
    
    print("=" * 60)
    print("🔧 Anora Editor - Windows Installer Creator")
    print("=" * 60)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ This script is designed for Windows systems")
        return
    
    # Create all installer components
    print("\n🔧 Creating installer components...")
    
    if create_windows_installer():
        print("✅ Windows installer created")
    
    if create_registry_script():
        print("✅ Registry association script created")
    
    if create_uninstaller():
        print("✅ Uninstaller created")
    
    if create_unregister_script():
        print("✅ Unregister script created")
    
    print("\n" + "=" * 60)
    print("🎉 Installer Creation Complete!")
    print("=" * 60)
    print("📁 Files created:")
    print("   - install_anora_windows.bat (Windows installer)")
    print("   - register_associations.py (Registry registration)")
    print("   - uninstall_anora.bat (Uninstaller)")
    print("   - unregister_associations.py (Registry cleanup)")
    print("\n🚀 To install Anora Editor:")
    print("   1. Build the application: python3 build_windows.py")
    print("   2. Run install_anora_windows.bat as Administrator")
    print("   3. Anora Editor will be registered for all code files")
    print("\n💡 After installation:")
    print("   - Double-click any code file to open with Anora Editor")
    print("   - Right-click files and select 'Open with Anora Editor'")
    print("   - Set Anora Editor as default for code files")

if __name__ == "__main__":
    main()