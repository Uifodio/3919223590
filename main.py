#!/usr/bin/env python3
"""
Perfect File Manager for Windows 11
Main application entry point
"""

import sys
import os
import json
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_window import MainWindow
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logger

def main():
    """Main application entry point"""
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Perfect File Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Perfect File Manager")
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Setup logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting Perfect File Manager")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Apply theme
    if config.get('theme', 'dark') == 'dark':
        app.setStyleSheet("""
            QApplication {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
    
    # Create and show main window
    main_window = MainWindow(config)
    main_window.show()
    
    # Restore window position if saved
    settings = QSettings()
    geometry = settings.value('main_window_geometry')
    if geometry:
        main_window.restoreGeometry(geometry)
    
    # Run application
    try:
        exit_code = app.exec()
        logger.info("Application exiting with code: %d", exit_code)
        
        # Save window position
        settings.setValue('main_window_geometry', main_window.saveGeometry())
        
        return exit_code
    except Exception as e:
        logger.error("Application error: %s", str(e))
        return 1

if __name__ == "__main__":
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create necessary directories
    for directory in ['logs', 'config', 'assets', 'temp']:
        Path(directory).mkdir(exist_ok=True)
    
    # Run the application
    sys.exit(main())