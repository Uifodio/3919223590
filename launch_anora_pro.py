#!/usr/bin/env python3
"""
Anora Editor Pro - Professional Launcher
Enhanced launcher with dependency checking and Unity integration
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    required_packages = {
        'pygments': 'pygments==2.17.2',
        'pillow': 'pillow==10.0.1',
        'requests': 'requests==2.31.0',
        'psutil': 'psutil==5.9.5',
        'gitpython': 'gitpython==3.1.40'
    }
    
    missing_packages = []
    
    print("🔍 Checking dependencies...")
    
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(install_name)
    
    if missing_packages:
        print("\n📦 Installing missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def detect_unity_project():
    """Detect Unity project in current directory"""
    current_dir = os.getcwd()
    unity_indicators = ['Assets', 'ProjectSettings', 'Packages', 'Library']
    
    for indicator in unity_indicators:
        if os.path.exists(os.path.join(current_dir, indicator)):
            return current_dir
    
    # Check parent directories
    parent_dir = os.path.dirname(current_dir)
    if parent_dir != current_dir:
        for indicator in unity_indicators:
            if os.path.exists(os.path.join(parent_dir, indicator)):
                return parent_dir
    
    return None

def setup_file_associations():
    """Setup file associations for Unity integration"""
    if platform.system() == "Windows":
        try:
            # Create registry entries for file associations
            import winreg
            
            # Get the path to the executable
            exe_path = os.path.abspath(sys.argv[0])
            if exe_path.endswith('.py'):
                # If running as Python script, create a batch file
                batch_path = os.path.join(os.path.dirname(exe_path), 'anora_editor_pro.bat')
                with open(batch_path, 'w') as f:
                    f.write(f'@echo off\npython "{exe_path}" %*\n')
                exe_path = batch_path
            
            # Register file associations
            file_types = ['.cs', '.py', '.js', '.html', '.css', '.json', '.xml', '.txt', '.md']
            
            for ext in file_types:
                try:
                    # Create file association
                    key_path = f"Software\\Classes\\{ext}"
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                        winreg.SetValue(key, "", winreg.REG_SZ, f"AnoraEditor{ext[1:].upper()}")
                    
                    # Set default program
                    prog_key_path = f"Software\\Classes\\AnoraEditor{ext[1:].upper()}\\shell\\open\\command"
                    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, prog_key_path) as key:
                        winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
                    
                    print(f"✅ Associated {ext} files with Anora Editor Pro")
                except Exception as e:
                    print(f"⚠️ Could not associate {ext} files: {e}")
                    
        except ImportError:
            print("⚠️ Could not setup file associations (winreg not available)")
    else:
        print("ℹ️ File associations setup is currently only available on Windows")

def create_unity_integration():
    """Create Unity integration scripts"""
    unity_project = detect_unity_project()
    if not unity_project:
        print("ℹ️ No Unity project detected in current directory")
        return
    
    print(f"🎮 Unity project detected: {unity_project}")
    
    # Create Unity integration script
    integration_script = os.path.join(unity_project, "Editor", "AnoraEditorIntegration.cs")
    os.makedirs(os.path.dirname(integration_script), exist_ok=True)
    
    script_content = '''using UnityEngine;
using UnityEditor;
using System.Diagnostics;
using System.IO;

public class AnoraEditorIntegration : EditorWindow
{
    [MenuItem("Tools/Anora Editor Pro/Open Script in Anora Editor")]
    public static void OpenInAnoraEditor()
    {
        if (Selection.activeObject is MonoScript script)
        {
            string scriptPath = AssetDatabase.GetAssetPath(script);
            string fullPath = Path.GetFullPath(scriptPath);
            
            // Try to find Anora Editor Pro executable
            string[] possiblePaths = {
                "anora_editor_pro.exe",
                "anora_editor_pro.py",
                Path.Combine(Application.dataPath, "..", "anora_editor_pro.exe"),
                Path.Combine(Application.dataPath, "..", "anora_editor_pro.py")
            };
            
            foreach (string path in possiblePaths)
            {
                if (File.Exists(path))
                {
                    Process.Start(path, $"\\"{fullPath}\\"");
                    return;
                }
            }
            
            UnityEngine.Debug.LogError("Anora Editor Pro not found! Please ensure it's in the project directory.");
        }
    }
    
    [MenuItem("Tools/Anora Editor Pro/Set as Default Editor")]
    public static void SetAsDefaultEditor()
    {
        // This would require more complex registry manipulation
        UnityEngine.Debug.Log("Please manually set Anora Editor Pro as the default editor for .cs files in your system settings.");
    }
}
'''
    
    try:
        with open(integration_script, 'w') as f:
            f.write(script_content)
        print("✅ Unity integration script created")
    except Exception as e:
        print(f"❌ Could not create Unity integration script: {e}")

def main():
    """Main launcher function"""
    print("🚀 Anora Editor Pro - Professional Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check and install dependencies
    if not check_and_install_dependencies():
        print("❌ Failed to install required dependencies!")
        input("Press Enter to exit...")
        return
    
    # Setup file associations
    print("\n🔗 Setting up file associations...")
    setup_file_associations()
    
    # Create Unity integration
    print("\n🎮 Setting up Unity integration...")
    create_unity_integration()
    
    # Launch the editor
    print("\n🎯 Launching Anora Editor Pro...")
    try:
        from anora_editor_pro import ProfessionalAnoraEditor
        app = ProfessionalAnoraEditor()
        app.run()
    except ImportError as e:
        print(f"❌ Error importing Anora Editor Pro: {e}")
        print("Make sure anora_editor_pro.py is in the same directory as this launcher.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error launching Anora Editor Pro: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()