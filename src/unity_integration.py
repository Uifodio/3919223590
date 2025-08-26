import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
from PyQt6.QtWidgets import QMessageBox
import sys

# Import winreg only on Windows
try:
    import winreg
except ImportError:
    winreg = None

from .utils import config_manager, SystemUtils

class UnityIntegration:
    """Unity integration manager"""
    
    def __init__(self):
        self.unity_path = config_manager.get("unity_integration.unity_path", "")
        self.auto_detect = config_manager.get("unity_integration.auto_detect", True)
    
    def setup_as_default_editor(self) -> bool:
        """Setup this application as Unity's default script editor"""
        try:
            # Get Unity installations
            unity_installations = SystemUtils.get_unity_installations()
            
            if not unity_installations:
                QMessageBox.warning(None, "Unity Not Found", 
                                  "No Unity installations found.\n"
                                  "Please install Unity or specify the path manually.")
                return False
            
            # Use the first Unity installation found
            unity_path = unity_installations[0]
            
            # Get the path to this executable
            current_exe = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            
            # Set registry key for Unity external script editor
            self._set_unity_external_editor(unity_path, current_exe)
            
            QMessageBox.information(None, "Success", 
                                  "Unity integration setup complete!\n"
                                  "This file manager is now set as Unity's default script editor.")
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to setup Unity integration: {e}")
            return False
    
    def _set_unity_external_editor(self, unity_path: str, editor_path: str):
        """Set external script editor in Unity registry"""
        if winreg is None:
            raise Exception("Registry access not available on this platform")
            
        try:
            # Unity stores external editor settings in registry
            registry_key = r"SOFTWARE\Unity Technologies\Unity Editor 5.x\External Script Editor"
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_key) as key:
                winreg.SetValueEx(key, "External Script Editor", 0, winreg.REG_SZ, editor_path)
                winreg.SetValueEx(key, "External Script Editor Args", 0, winreg.REG_SZ, "")
                
        except Exception as e:
            raise Exception(f"Failed to set registry key: {e}")
    
    def open_unity_project(self, project_path: str) -> bool:
        """Open Unity project"""
        try:
            if not os.path.exists(project_path):
                return False
            
            # Find Unity executable
            unity_exe = self._find_unity_executable(project_path)
            if not unity_exe:
                return False
            
            # Open project with Unity
            subprocess.Popen([unity_exe, "-projectPath", project_path])
            return True
            
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to open Unity project: {e}")
            return False
    
    def _find_unity_executable(self, project_path: str) -> Optional[str]:
        """Find appropriate Unity executable for project"""
        try:
            # Check project version
            project_version = self._get_project_version(project_path)
            
            # Find matching Unity installation
            unity_installations = SystemUtils.get_unity_installations()
            
            for unity_path in unity_installations:
                if project_version in unity_path:
                    return os.path.join(unity_path, "Editor", "Unity.exe")
            
            # If no exact match, use the latest version
            if unity_installations:
                return os.path.join(unity_installations[0], "Editor", "Unity.exe")
                
        except Exception:
            pass
        
        return None
    
    def _get_project_version(self, project_path: str) -> str:
        """Get Unity version from project"""
        try:
            version_file = os.path.join(project_path, "ProjectSettings", "ProjectVersion.txt")
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    for line in f:
                        if line.startswith("m_EditorVersion:"):
                            return line.split(":")[1].strip()
        except Exception:
            pass
        
        return ""
    
    def create_unity_project(self, project_name: str, project_path: str, template: str = "3D") -> bool:
        """Create new Unity project"""
        try:
            # Find Unity executable
            unity_installations = SystemUtils.get_unity_installations()
            if not unity_installations:
                return False
            
            unity_exe = os.path.join(unity_installations[0], "Editor", "Unity.exe")
            
            # Create project
            cmd = [
                unity_exe,
                "-createProject", project_path,
                "-projectName", project_name
            ]
            
            if template:
                cmd.extend(["-template", template])
            
            subprocess.Popen(cmd)
            return True
            
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to create Unity project: {e}")
            return False
    
    def build_unity_project(self, project_path: str, build_target: str = "StandaloneWindows64") -> bool:
        """Build Unity project"""
        try:
            # Find Unity executable
            unity_installations = SystemUtils.get_unity_installations()
            if not unity_installations:
                return False
            
            unity_exe = os.path.join(unity_installations[0], "Editor", "Unity.exe")
            
            # Build project
            cmd = [
                unity_exe,
                "-batchmode",
                "-quit",
                "-projectPath", project_path,
                "-buildTarget", build_target,
                "-executeMethod", "BuildScript.BuildGame"
            ]
            
            subprocess.run(cmd, check=True)
            return True
            
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to build Unity project: {e}")
            return False
    
    def get_unity_projects(self) -> List[Dict[str, str]]:
        """Get list of recent Unity projects"""
        projects = []
        
        try:
            # Check Unity Hub projects
            hub_projects_path = os.path.expanduser("~/AppData/Roaming/UnityHub/projects.json")
            if os.path.exists(hub_projects_path):
                with open(hub_projects_path, 'r') as f:
                    hub_data = json.load(f)
                    for project in hub_data:
                        if os.path.exists(project.get('path', '')):
                            projects.append({
                                'name': project.get('name', ''),
                                'path': project.get('path', ''),
                                'version': project.get('version', '')
                            })
            
            # Check Unity Editor recent projects
            if winreg is not None:
                registry_key = r"SOFTWARE\Unity Technologies\Unity Editor 5.x\RecentlyUsedProjectPaths"
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key) as key:
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                if os.path.exists(value):
                                    projects.append({
                                        'name': os.path.basename(value),
                                        'path': value,
                                        'version': ''
                                    })
                                i += 1
                            except WindowsError:
                                break
                except:
                    pass
                
        except Exception:
            pass
        
        return projects
    
    def is_unity_project(self, path: str) -> bool:
        """Check if path is a Unity project"""
        try:
            # Check for Unity project files
            unity_files = [
                "ProjectSettings/ProjectVersion.txt",
                "Assets",
                "Library",
                "Packages"
            ]
            
            for file in unity_files:
                if not os.path.exists(os.path.join(path, file)):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_project_info(self, project_path: str) -> Dict[str, str]:
        """Get Unity project information"""
        info = {
            'name': os.path.basename(project_path),
            'path': project_path,
            'version': '',
            'target_platform': '',
            'scripting_backend': ''
        }
        
        try:
            # Get version
            version_file = os.path.join(project_path, "ProjectSettings", "ProjectVersion.txt")
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    for line in f:
                        if line.startswith("m_EditorVersion:"):
                            info['version'] = line.split(":")[1].strip()
            
            # Get project settings
            settings_file = os.path.join(project_path, "ProjectSettings", "ProjectSettings.asset")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    content = f.read()
                    # Parse Unity YAML-like format
                    # This is a simplified parser
                    if "m_TargetPlatform: 19" in content:
                        info['target_platform'] = "StandaloneWindows64"
                    elif "m_TargetPlatform: 13" in content:
                        info['target_platform'] = "Android"
                    elif "m_TargetPlatform: 9" in content:
                        info['target_platform'] = "iOS"
                    
                    if "m_ScriptingBackend: 1" in content:
                        info['scripting_backend'] = "Mono"
                    elif "m_ScriptingBackend: 2" in content:
                        info['scripting_backend'] = "IL2CPP"
                        
        except Exception:
            pass
        
        return info

# Global instance
unity_integration = UnityIntegration()