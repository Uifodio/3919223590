#!/usr/bin/env python3
"""
Anora Editor Pro - Professional Build Script
Creates standalone executable with all dependencies
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller==6.3.0"])
        return True
    except subprocess.CalledProcessError:
        return False

def create_spec_file():
    """Create PyInstaller spec file for Anora Editor Pro"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['anora_editor_pro.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
        'pygments.styles',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'psutil',
        'git',
        'gitpython'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnoraEditorPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('anora_editor_pro.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created PyInstaller spec file")

def create_icon():
    """Create a simple icon for the application"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a 256x256 icon
        size = 256
        img = Image.new('RGBA', (size, size), (30, 30, 30, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple "A" logo
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        # Draw the "A" in the center
        text = "A"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        # Draw text with professional colors
        draw.text((x, y), text, fill=(212, 212, 212, 255), font=font)
        
        # Save as ICO
        img.save('icon.ico', format='ICO')
        print("✅ Created application icon")
        
    except Exception as e:
        print(f"⚠️ Could not create icon: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building Anora Editor Pro executable...")
    
    try:
        # Run PyInstaller
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--onefile",
            "--windowed",
            "--name=AnoraEditorPro",
            "anora_editor_pro.py"
        ])
        
        print("✅ Build completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer_script():
    """Create installer script for easy setup"""
    if platform.system() == "Windows":
        installer_content = '''@echo off
echo Installing Anora Editor Pro...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - good!
) else (
    echo Please run this script as administrator for full installation.
    pause
    exit /b 1
)

REM Copy executable to Program Files
set "INSTALL_DIR=C:\\Program Files\\Anora Editor Pro"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

copy "dist\\AnoraEditorPro.exe" "%INSTALL_DIR%\\"
if exist "icon.ico" copy "icon.ico" "%INSTALL_DIR%\\"

REM Create desktop shortcut
set "DESKTOP=%USERPROFILE%\\Desktop"
set "SHORTCUT=%DESKTOP%\\Anora Editor Pro.lnk"

echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\AnoraEditorPro.exe'; $Shortcut.Save()"

REM Register file associations
echo Registering file associations...
for %%f in (.cs .py .js .html .css .json .xml .txt .md) do (
    reg add "HKEY_CURRENT_USER\\Software\\Classes\\%%f" /ve /d "AnoraEditor%%f" /f
    reg add "HKEY_CURRENT_USER\\Software\\Classes\\AnoraEditor%%f\\shell\\open\\command" /ve /d "\\"%INSTALL_DIR%\\AnoraEditorPro.exe\\" \\"%%1\\"" /f
)

echo.
echo Installation completed!
echo Anora Editor Pro has been installed to: %INSTALL_DIR%
echo Desktop shortcut created.
echo File associations registered.
echo.
pause
'''
        
        with open('install_anora_pro.bat', 'w') as f:
            f.write(installer_content)
        
        print("✅ Created Windows installer script")
    
    elif platform.system() == "Linux":
        installer_content = '''#!/bin/bash
echo "Installing Anora Editor Pro..."

# Create installation directory
INSTALL_DIR="/opt/anora-editor-pro"
sudo mkdir -p "$INSTALL_DIR"

# Copy executable
sudo cp "dist/AnoraEditorPro" "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/AnoraEditorPro"

# Create desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/anora-editor-pro.desktop"
mkdir -p "$(dirname "$DESKTOP_ENTRY")"

cat > "$DESKTOP_ENTRY" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Anora Editor Pro
Comment=Professional Code Editor for Unity
Exec=$INSTALL_DIR/AnoraEditorPro %F
Icon=$INSTALL_DIR/icon.png
Terminal=false
Categories=Development;IDE;
MimeType=text/plain;text/x-csharp;text/x-python;text/x-javascript;text/html;text/css;application/json;
EOF

# Create desktop shortcut
cp "$DESKTOP_ENTRY" "$HOME/Desktop/"

echo "Installation completed!"
echo "Anora Editor Pro has been installed to: $INSTALL_DIR"
'''
        
        with open('install_anora_pro.sh', 'w') as f:
            f.write(installer_content)
        
        os.chmod('install_anora_pro.sh', 0o755)
        print("✅ Created Linux installer script")

def create_readme():
    """Create comprehensive README for the build"""
    readme_content = '''# Anora Editor Pro - Professional Build

## 🎯 What's New in the Professional Version

### ✨ Major Improvements
- **Fixed Drag & Drop** - Native implementation without external dependencies
- **Professional UI** - VS Code-inspired dark theme with modern design
- **Enhanced Features** - Auto-completion, bracket matching, advanced search
- **Unity Integration** - Automatic Unity project detection and integration
- **File Associations** - Set as default editor for code files
- **Performance Optimized** - Faster syntax highlighting and better memory management

### 🚀 New Features Added
- **Project Explorer** - File tree sidebar with project navigation
- **Enhanced Search** - Regex support, case sensitivity, whole word matching
- **Auto-save** - Intelligent file saving every 30 seconds
- **Session Management** - Remember open files and window state
- **Status Bar** - File info, line/column position, file size, encoding
- **Unity Detection** - Automatic Unity project detection
- **Professional Toolbar** - Icons and quick access to common actions

### 🎮 Unity-Specific Features
- **Unity Project Detection** - Automatically detects Unity projects
- **Unity Integration Script** - Creates Unity editor integration
- **C# Support** - Enhanced C# syntax highlighting for Unity scripts
- **Unity API Reference** - Built-in Unity documentation access
- **Script Templates** - Quick Unity script creation

### 🔧 Technical Improvements
- **Removed Problematic Dependencies** - No more tkinterdnd2 issues
- **Better Error Handling** - Robust error recovery and user feedback
- **Memory Optimization** - Better resource management
- **Cross-Platform** - Works on Windows, Linux, and macOS
- **Standalone Executable** - No Python installation required

## 📦 Installation

### Quick Install
1. Run the installer script for your platform:
   - Windows: `install_anora_pro.bat` (run as administrator)
   - Linux: `./install_anora_pro.sh`

### Manual Install
1. Copy `AnoraEditorPro.exe` (Windows) or `AnoraEditorPro` (Linux) to your preferred location
2. Create desktop shortcuts
3. Set file associations manually if needed

## 🎯 Usage

### Basic Usage
- **Launch**: Double-click the executable or use the launcher script
- **Open Files**: File menu, drag & drop, or double-click files
- **Save**: Ctrl+S or File menu
- **Search**: Ctrl+F for find, Ctrl+H for replace

### Unity Integration
1. Place the editor in your Unity project directory
2. Run the launcher to create Unity integration scripts
3. Use "Tools > Anora Editor Pro" in Unity to open scripts
4. Set as default editor for .cs files

### Keyboard Shortcuts
- `Ctrl+N` - New file
- `Ctrl+O` - Open file
- `Ctrl+S` - Save
- `Ctrl+Shift+S` - Save as
- `Ctrl+F` - Find
- `Ctrl+H` - Replace
- `Ctrl+G` - Go to line
- `F3` - Find next
- `Shift+F3` - Find previous
- `Ctrl+A` - Select all
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo

## 🔧 Building from Source

### Requirements
- Python 3.7+
- PyInstaller
- Required packages (see requirements.txt)

### Build Steps
1. Install dependencies: `pip install -r requirements.txt`
2. Run build script: `python build_anora_pro.py`
3. Find executable in `dist/` folder

## 🐛 Troubleshooting

### Common Issues
1. **Drag & Drop Not Working**: Ensure you're using the Pro version
2. **Unity Integration Issues**: Check that the editor is in the Unity project directory
3. **File Associations**: Run installer as administrator on Windows
4. **Performance Issues**: Close unnecessary tabs and files

### Support
For issues and feature requests, please check the project documentation or create an issue in the repository.

## 📄 License
This project is open source and available under the MIT License.

---
*Anora Editor Pro - Professional Code Editor for Unity Development*
'''
    
    with open('README_PRO_BUILD.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created comprehensive README")

def main():
    """Main build function"""
    print("🔨 Anora Editor Pro - Professional Build Script")
    print("=" * 50)
    
    # Check if PyInstaller is available
    if not check_pyinstaller():
        print("📦 PyInstaller not found. Installing...")
        if not install_pyinstaller():
            print("❌ Failed to install PyInstaller!")
            return
    
    # Create icon
    print("\n🎨 Creating application icon...")
    create_icon()
    
    # Create spec file
    print("\n📋 Creating PyInstaller spec file...")
    create_spec_file()
    
    # Build executable
    print("\n🔨 Building executable...")
    if not build_executable():
        print("❌ Build failed!")
        return
    
    # Create installer scripts
    print("\n📦 Creating installer scripts...")
    create_installer_script()
    
    # Create README
    print("\n📄 Creating documentation...")
    create_readme()
    
    print("\n🎉 Build completed successfully!")
    print("\n📁 Files created:")
    print("  - dist/AnoraEditorPro.exe (Windows) or AnoraEditorPro (Linux)")
    print("  - install_anora_pro.bat (Windows installer)")
    print("  - install_anora_pro.sh (Linux installer)")
    print("  - README_PRO_BUILD.md (Documentation)")
    print("\n🚀 Ready to install and use!")

if __name__ == "__main__":
    main()