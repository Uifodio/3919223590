#!/usr/bin/env python3
"""
Perfect File Manager for Windows 11
Main application entry point
"""

import sys
import os
import json
import logging
import traceback
from pathlib import Path

# Add extensive error handling and debugging
def setup_debug_logging():
    """Setup comprehensive debug logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app_debug.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log system info
    logger = logging.getLogger(__name__)
    logger.info("=== Application Startup ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    return logger

def check_dependencies():
    """Check and log all required dependencies"""
    logger = logging.getLogger(__name__)
    required_modules = [
        'PySide6', 'PIL', 'win32api', 'psutil', 
        'watchdog', 'pyperclip', 'send2trash'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
                logger.info(f"✓ {module} version: {PIL.__version__}")
            elif module == 'PySide6':
                import PySide6
                logger.info(f"✓ {module} version: {PySide6.__version__}")
            elif module == 'win32api':
                import win32api
                logger.info(f"✓ {module} available")
            elif module == 'psutil':
                import psutil
                logger.info(f"✓ {module} version: {psutil.__version__}")
            elif module == 'watchdog':
                import watchdog
                logger.info(f"✓ {module} available")
            elif module == 'pyperclip':
                import pyperclip
                logger.info(f"✓ {module} available")
            elif module == 'send2trash':
                import send2trash
                logger.info(f"✓ {module} available")
        except ImportError as e:
            logger.error(f"✗ {module} missing: {e}")
            missing_modules.append(module)
        except Exception as e:
            logger.warning(f"? {module} error: {e}")
    
    if missing_modules:
        logger.error(f"Missing modules: {missing_modules}")
        return False
    
    return True

def main():
    """Main application entry point with comprehensive error handling"""
    
    # Setup debug logging first
    logger = setup_debug_logging()
    
    try:
        logger.info("Starting application initialization...")
        
        # Check dependencies
        if not check_dependencies():
            logger.error("Critical dependencies missing. Please install requirements.")
            input("Press Enter to exit...")
            return 1
        
        # Import PySide6 with error handling
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt, QSettings
            from PySide6.QtGui import QIcon
            logger.info("✓ PySide6 imports successful")
        except ImportError as e:
            logger.error(f"Failed to import PySide6: {e}")
            logger.error("Please install PySide6: pip install PySide6==6.6.1")
            input("Press Enter to exit...")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error importing PySide6: {e}")
            input("Press Enter to exit...")
            return 1
        
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            logger.info(f"Added src path: {src_path}")
        
        # Import application modules with error handling
        try:
            from src.main_window import MainWindow
            from src.utils.config_manager import ConfigManager
            from src.utils.logger import setup_logger
            logger.info("✓ Application modules imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import application modules: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error importing application modules: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            return 1
        
        # Create application
        try:
            app = QApplication(sys.argv)
            app.setApplicationName("Perfect File Manager")
            app.setApplicationVersion("1.0.0")
            app.setOrganizationName("Perfect File Manager")
            logger.info("✓ QApplication created successfully")
        except Exception as e:
            logger.error(f"Failed to create QApplication: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            return 1
        
        # Set application icon
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
                logger.info(f"✓ Application icon set: {icon_path}")
            else:
                logger.info("No icon file found, using default")
        except Exception as e:
            logger.warning(f"Failed to set application icon: {e}")
        
        # Setup logging
        try:
            setup_logger()
            logger.info("✓ Logger setup completed")
        except Exception as e:
            logger.warning(f"Failed to setup logger: {e}")
        
        # Load configuration
        try:
            config_manager = ConfigManager()
            config = config_manager.load_config()
            logger.info("✓ Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Use default config
            config = {
                'theme': 'dark',
                'font_size': 12,
                'auto_save': True,
                'show_hidden': False,
                'recent_files': [],
                'recent_folders': []
            }
            logger.info("Using default configuration")
        
        # Apply theme
        try:
            if config.get('theme', 'dark') == 'dark':
                app.setStyleSheet("""
                    QApplication {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                """)
                logger.info("✓ Dark theme applied")
        except Exception as e:
            logger.warning(f"Failed to apply theme: {e}")
        
        # Create and show main window
        try:
            main_window = MainWindow(config)
            logger.info("✓ Main window created successfully")
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            return 1
        
        try:
            main_window.show()
            logger.info("✓ Main window displayed successfully")
        except Exception as e:
            logger.error(f"Failed to show main window: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            return 1
        
        # Restore window position if saved
        try:
            settings = QSettings()
            geometry = settings.value('main_window_geometry')
            if geometry:
                main_window.restoreGeometry(geometry)
                logger.info("✓ Window geometry restored")
        except Exception as e:
            logger.warning(f"Failed to restore window geometry: {e}")
        
        # Run application
        logger.info("Starting application event loop...")
        try:
            exit_code = app.exec()
            logger.info(f"Application exiting with code: {exit_code}")
            
            # Save window position
            try:
                settings.setValue('main_window_geometry', main_window.saveGeometry())
                logger.info("✓ Window geometry saved")
            except Exception as e:
                logger.warning(f"Failed to save window geometry: {e}")
            
            return exit_code
        except Exception as e:
            logger.error(f"Application error during execution: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            return 1
            
    except Exception as e:
        logger.error(f"Critical application error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"\nCritical error: {e}")
        print("Check the debug log for details: logs/app_debug.log")
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    # Ensure we're in the correct directory
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except Exception as e:
        print(f"Failed to change directory: {e}")
    
    # Create necessary directories
    try:
        for directory in ['logs', 'config', 'assets', 'temp']:
            Path(directory).mkdir(exist_ok=True)
    except Exception as e:
        print(f"Failed to create directories: {e}")
    
    # Run the application
    sys.exit(main())