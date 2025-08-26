#!/usr/bin/env python3
"""
Unity File Manager Pro
A powerful file manager with built-in code editor for Unity developers

Main entry point for the application.
"""

import sys
import os
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QIcon, QPixmap

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_window import MainWindow
from src.utils import config_manager, SystemUtils

def setup_application():
    """Setup the QApplication with proper configuration"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Unity File Manager Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Unity File Manager Team")
    app.setOrganizationDomain("unityfilemanager.com")
    
    # Set application icon (if available)
    icon_path = os.path.join("resources", "icons", "app.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Enable high DPI support
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set application style
    app.setStyle("Fusion")
    
    return app

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        import pygments
    except ImportError:
        missing_deps.append("pygments")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        error_msg = f"Missing required dependencies: {', '.join(missing_deps)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += "pip install -r requirements.txt"
        
        QMessageBox.critical(None, "Missing Dependencies", error_msg)
        return False
    
    return True

def check_system_compatibility():
    """Check if the system is compatible"""
    system_info = SystemUtils.get_system_info()
    
    if system_info['os'] != 'Windows':
        QMessageBox.warning(None, "System Compatibility", 
                          "This application is designed for Windows.\n"
                          "Some features may not work on other operating systems.")
    
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "resources/config",
        "resources/icons", 
        "resources/themes"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle Ctrl+C gracefully
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Show error dialog
    QMessageBox.critical(None, "Application Error", 
                        f"An unexpected error occurred:\n\n{error_msg}\n\n"
                        "Please report this issue to the developers.")

def main():
    """Main application entry point"""
    try:
        # Create necessary directories
        create_directories()
        
        # Setup application
        app = setup_application()
        
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Check system compatibility
        if not check_system_compatibility():
            return 1
        
        # Set up exception handling
        sys.excepthook = handle_exception
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            # If a file path is provided, open it
            file_path = sys.argv[1]
            if os.path.exists(file_path):
                main_window.open_in_editor(file_path)
        
        # Start the application
        return app.exec()
        
    except Exception as e:
        # Handle any startup errors
        error_msg = f"Failed to start application: {str(e)}\n\n"
        error_msg += "Traceback:\n"
        error_msg += traceback.format_exc()
        
        QMessageBox.critical(None, "Startup Error", error_msg)
        return 1

if __name__ == "__main__":
    sys.exit(main())