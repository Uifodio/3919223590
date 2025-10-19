#!/usr/bin/env python3
"""
Futuristic Web Server Application
A professional, modern web server with sleek UI and advanced features
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QProgressBar, QSlider, QCheckBox, QComboBox, QSpinBox, QGroupBox, QSplitter, QFrame, QScrollArea
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon, QLinearGradient, QBrush
from PyQt6.QtWebEngineWidgets import QWebEngineView
from server_manager import WebServerManager
import logging

class ModernButton(QPushButton):
    """Custom modern button with hover effects"""
    def __init__(self, text, color="#2196F3"):
        super().__init__(text)
        self.color = color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 24px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
        """)
    
    def darken_color(self, color, factor=0.2):
        """Darken a hex color"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"

class ServerStatusWidget(QWidget):
    """Widget to display server status and controls"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Server 1 Controls
        server1_group = QGroupBox("Server 1")
        server1_layout = QVBoxLayout()
        
        self.server1_port = QLineEdit()
        self.server1_port.setPlaceholderText("Port (e.g., 8080)")
        self.server1_port.setText("8080")
        
        self.server1_path = QLineEdit()
        self.server1_path.setPlaceholderText("Directory path")
        self.server1_path.setText(str(Path.home()))
        
        self.server1_browse = ModernButton("Browse", "#4CAF50")
        self.server1_browse.clicked.connect(self.browse_directory1)
        
        self.server1_start = ModernButton("Start Server", "#2196F3")
        self.server1_stop = ModernButton("Stop Server", "#F44336")
        self.server1_status = QLabel("Status: Stopped")
        self.server1_status.setStyleSheet("color: #F44336; font-weight: bold;")
        
        server1_layout.addWidget(QLabel("Port:"))
        server1_layout.addWidget(self.server1_port)
        server1_layout.addWidget(QLabel("Directory:"))
        server1_layout.addWidget(self.server1_path)
        server1_layout.addWidget(self.server1_browse)
        server1_layout.addWidget(self.server1_start)
        server1_layout.addWidget(self.server1_stop)
        server1_layout.addWidget(self.server1_status)
        
        server1_group.setLayout(server1_layout)
        
        # Server 2 Controls
        server2_group = QGroupBox("Server 2")
        server2_layout = QVBoxLayout()
        
        self.server2_port = QLineEdit()
        self.server2_port.setPlaceholderText("Port (e.g., 8081)")
        self.server2_port.setText("8081")
        
        self.server2_path = QLineEdit()
        self.server2_path.setPlaceholderText("Directory path")
        self.server2_path.setText(str(Path.home() / "Documents"))
        
        self.server2_browse = ModernButton("Browse", "#4CAF50")
        self.server2_browse.clicked.connect(self.browse_directory2)
        
        self.server2_start = ModernButton("Start Server", "#2196F3")
        self.server2_stop = ModernButton("Stop Server", "#F44336")
        self.server2_status = QLabel("Status: Stopped")
        self.server2_status.setStyleSheet("color: #F44336; font-weight: bold;")
        
        server2_layout.addWidget(QLabel("Port:"))
        server2_layout.addWidget(self.server2_port)
        server2_layout.addWidget(QLabel("Directory:"))
        server2_layout.addWidget(self.server2_path)
        server2_layout.addWidget(self.server2_browse)
        server2_layout.addWidget(self.server2_start)
        server2_layout.addWidget(self.server2_stop)
        server2_layout.addWidget(self.server2_status)
        
        server2_group.setLayout(server2_layout)
        
        layout.addWidget(server1_group)
        layout.addWidget(server2_group)
        self.setLayout(layout)
    
    def browse_directory1(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.server1_path.setText(directory)
    
    def browse_directory2(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.server2_path.setText(directory)

class FileManagerWidget(QWidget):
    """Widget for file management features"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # File upload section
        upload_group = QGroupBox("File Upload")
        upload_layout = QVBoxLayout()
        
        self.upload_button = ModernButton("Upload Files", "#FF9800")
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.upload_progress)
        upload_group.setLayout(upload_layout)
        
        # File browser
        browser_group = QGroupBox("File Browser")
        browser_layout = QVBoxLayout()
        
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["Name", "Size", "Type", "Modified"])
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        browser_layout.addWidget(self.file_table)
        browser_group.setLayout(browser_layout)
        
        layout.addWidget(upload_group)
        layout.addWidget(browser_group)
        self.setLayout(layout)

class LogViewerWidget(QWidget):
    """Widget for viewing server logs"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Log controls
        controls_layout = QHBoxLayout()
        self.clear_logs = ModernButton("Clear Logs", "#F44336")
        self.refresh_logs = ModernButton("Refresh", "#2196F3")
        
        controls_layout.addWidget(self.clear_logs)
        controls_layout.addWidget(self.refresh_logs)
        controls_layout.addStretch()
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #333;
                border-radius: 4px;
            }
        """)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.log_display)
        self.setLayout(layout)

class FuturisticWebServerApp(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.server_manager = WebServerManager()
        self.init_ui()
        self.setup_connections()
        self.setup_logging()
    
    def init_ui(self):
        self.setWindowTitle("Futuristic Web Server - Professional Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
            }
            QTabBar::tab:hover {
                background-color: #404040;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create title
        title = QLabel("🚀 Futuristic Web Server")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
            margin: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Server Control Tab
        self.server_widget = ServerStatusWidget()
        self.tab_widget.addTab(self.server_widget, "Server Control")
        
        # File Manager Tab
        self.file_widget = FileManagerWidget()
        self.tab_widget.addTab(self.file_widget, "File Manager")
        
        # Log Viewer Tab
        self.log_widget = LogViewerWidget()
        self.tab_widget.addTab(self.log_widget, "Logs")
        
        # Web Preview Tab
        self.web_widget = QWebEngineView()
        self.tab_widget.addTab(self.web_widget, "Web Preview")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready to start servers")
    
    def setup_connections(self):
        """Setup signal connections"""
        # Server 1 connections
        self.server_widget.server1_start.clicked.connect(self.start_server1)
        self.server_widget.server1_stop.clicked.connect(self.stop_server1)
        
        # Server 2 connections
        self.server_widget.server2_start.clicked.connect(self.start_server2)
        self.server_widget.server2_stop.clicked.connect(self.stop_server2)
        
        # File manager connections
        self.file_widget.upload_button.clicked.connect(self.upload_files)
        
        # Log viewer connections
        self.log_widget.clear_logs.clicked.connect(self.clear_logs)
        self.log_widget.refresh_logs.clicked.connect(self.refresh_logs)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start_server1(self):
        """Start server 1"""
        try:
            port = int(self.server_widget.server1_port.text())
            path = self.server_widget.server1_path.text()
            
            if self.server_manager.start_server(1, port, path):
                self.server_widget.server1_status.setText("Status: Running")
                self.server_widget.server1_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                self.statusBar().showMessage(f"Server 1 started on port {port}")
                self.logger.info(f"Server 1 started on port {port} serving {path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to start server 1")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid port number")
    
    def stop_server1(self):
        """Stop server 1"""
        if self.server_manager.stop_server(1):
            self.server_widget.server1_status.setText("Status: Stopped")
            self.server_widget.server1_status.setStyleSheet("color: #F44336; font-weight: bold;")
            self.statusBar().showMessage("Server 1 stopped")
            self.logger.info("Server 1 stopped")
    
    def start_server2(self):
        """Start server 2"""
        try:
            port = int(self.server_widget.server2_port.text())
            path = self.server_widget.server2_path.text()
            
            if self.server_manager.start_server(2, port, path):
                self.server_widget.server2_status.setText("Status: Running")
                self.server_widget.server2_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                self.statusBar().showMessage(f"Server 2 started on port {port}")
                self.logger.info(f"Server 2 started on port {port} serving {path}")
            else:
                QMessageBox.warning(self, "Error", "Failed to start server 2")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid port number")
    
    def stop_server2(self):
        """Stop server 2"""
        if self.server_manager.stop_server(2):
            self.server_widget.server2_status.setText("Status: Stopped")
            self.server_widget.server2_status.setStyleSheet("color: #F44336; font-weight: bold;")
            self.statusBar().showMessage("Server 2 stopped")
            self.logger.info("Server 2 stopped")
    
    def upload_files(self):
        """Handle file upload"""
        files, _ = QFileDialog.getOpenFileNames(self, "Select files to upload")
        if files:
            self.file_widget.upload_progress.setVisible(True)
            self.file_widget.upload_progress.setMaximum(len(files))
            
            for i, file_path in enumerate(files):
                # Simulate upload process
                self.file_widget.upload_progress.setValue(i + 1)
                QApplication.processEvents()
                time.sleep(0.1)  # Simulate upload time
            
            self.file_widget.upload_progress.setVisible(False)
            self.statusBar().showMessage(f"Uploaded {len(files)} files")
            self.logger.info(f"Uploaded {len(files)} files")
    
    def clear_logs(self):
        """Clear log display"""
        self.log_widget.log_display.clear()
    
    def refresh_logs(self):
        """Refresh log display"""
        try:
            with open('logs/server.log', 'r') as f:
                logs = f.read()
                self.log_widget.log_display.setPlainText(logs)
        except FileNotFoundError:
            self.log_widget.log_display.setPlainText("No logs available")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Futuristic Web Server")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Futuristic Software")
    
    # Create and show main window
    window = FuturisticWebServerApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()