#!/usr/bin/env python3
"""
Nova Explorer - Advanced File Manager with Built-in Editor
Built with Kivy for maximum reliability and simplicity
"""

import os
import sys
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.separator import Separator
from kivy.uix.progressbar import ProgressBar
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.lang import Builder

# File operations
import fs_operations
import editor_widget
import settings_manager

# Set window size and title
Window.size = (1200, 800)
Window.minimum_width = 800
Window.minimum_height = 600

# Load KV language file
Builder.load_file('nova_explorer.kv')

class FileItem(BoxLayout):
    """Individual file/folder item in the file list"""
    name = StringProperty('')
    size = StringProperty('')
    modified = StringProperty('')
    is_folder = BooleanProperty(False)
    is_selected = BooleanProperty(False)
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.update_info()
    
    def update_info(self):
        """Update file information"""
        try:
            stat = os.stat(self.file_path)
            self.name = os.path.basename(self.file_path)
            self.is_folder = os.path.isdir(self.file_path)
            
            if self.is_folder:
                self.size = '<DIR>'
            else:
                size_bytes = stat.st_size
                if size_bytes < 1024:
                    self.size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    self.size = f"{size_bytes // 1024} KB"
                else:
                    self.size = f"{size_bytes // (1024 * 1024)} MB"
            
            self.modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        except Exception as e:
            print(f"Error updating file info: {e}")

class FileList(ScrollView):
    """Scrollable file list with selection support"""
    selected_files = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, spacing=dp(2), size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self.current_path = os.path.expanduser('~')
        self.refresh_files()
    
    def refresh_files(self):
        """Refresh the file list"""
        self.layout.clear_widgets()
        self.selected_files.clear()
        
        try:
            # Add parent directory option
            if self.current_path != os.path.dirname(self.current_path):
                parent_btn = Button(
                    text='..',
                    size_hint_y=None,
                    height=dp(40),
                    background_color=(0.3, 0.3, 0.3, 1)
                )
                parent_btn.bind(on_press=self.go_up)
                self.layout.add_widget(parent_btn)
            
            # Get files and folders
            items = []
            for item in os.listdir(self.current_path):
                item_path = os.path.join(self.current_path, item)
                if os.path.exists(item_path):
                    items.append(item_path)
            
            # Sort: folders first, then files
            items.sort(key=lambda x: (not os.path.isdir(x), os.path.basename(x).lower()))
            
            # Add items to layout
            for item_path in items:
                file_item = FileItem(item_path)
                file_item.bind(on_touch_down=self.on_file_touch)
                self.layout.add_widget(file_item)
                
        except Exception as e:
            error_label = Label(text=f"Error loading directory: {e}")
            self.layout.add_widget(error_label)
    
    def on_file_touch(self, instance, touch):
        """Handle file selection"""
        if instance.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.open_file(instance.file_path)
            else:
                self.select_file(instance)
    
    def select_file(self, file_item):
        """Select a file item"""
        # Clear previous selection
        for child in self.layout.children:
            if hasattr(child, 'is_selected'):
                child.is_selected = False
        
        file_item.is_selected = True
        self.selected_files = [file_item.file_path]
    
    def open_file(self, file_path):
        """Open a file or folder"""
        if os.path.isdir(file_path):
            self.current_path = file_path
            self.refresh_files()
        else:
            # Open file in editor
            app = App.get_running_app()
            app.open_file_in_editor(file_path)
    
    def go_up(self, instance):
        """Go to parent directory"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self.refresh_files()

class AddressBar(BoxLayout):
    """Address bar for navigation"""
    current_path = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        
        # Path input
        self.path_input = TextInput(
            multiline=False,
            size_hint_x=0.8,
            font_size=dp(14)
        )
        self.path_input.bind(on_text_validate=self.navigate)
        
        # Go button
        self.go_button = Button(
            text='Go',
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 1, 1)
        )
        self.go_button.bind(on_press=self.navigate)
        
        self.add_widget(self.path_input)
        self.add_widget(self.go_button)
    
    def navigate(self, instance):
        """Navigate to the entered path"""
        path = self.path_input.text.strip()
        if os.path.exists(path):
            app = App.get_running_app()
            app.navigate_to(path)
    
    def update_path(self, path):
        """Update the displayed path"""
        self.current_path = path
        self.path_input.text = path

class ToolBar(BoxLayout):
    """Toolbar with navigation and action buttons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = dp(5)
        self.spacing = dp(5)
        
        # Navigation buttons
        self.back_btn = Button(
            text='←',
            size_hint_x=None,
            width=dp(40),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        
        self.forward_btn = Button(
            text='→',
            size_hint_x=None,
            width=dp(40),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.forward_btn.bind(on_press=self.go_forward)
        
        self.up_btn = Button(
            text='↑',
            size_hint_x=None,
            width=dp(40),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.up_btn.bind(on_press=self.go_up)
        
        self.refresh_btn = Button(
            text='⟳',
            size_hint_x=None,
            width=dp(40),
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.refresh_btn.bind(on_press=self.refresh)
        
        # Action buttons
        self.new_folder_btn = Button(
            text='New Folder',
            size_hint_x=None,
            width=dp(100),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.new_folder_btn.bind(on_press=self.new_folder)
        
        self.new_file_btn = Button(
            text='New File',
            size_hint_x=None,
            width=dp(100),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.new_file_btn.bind(on_press=self.new_file)
        
        # Add widgets
        self.add_widget(self.back_btn)
        self.add_widget(self.forward_btn)
        self.add_widget(self.up_btn)
        self.add_widget(self.refresh_btn)
        self.add_widget(Separator())
        self.add_widget(self.new_folder_btn)
        self.add_widget(self.new_file_btn)
        self.add_widget(Label())  # Spacer
    
    def go_back(self, instance):
        """Go back in history"""
        app = App.get_running_app()
        app.go_back()
    
    def go_forward(self, instance):
        """Go forward in history"""
        app = App.get_running_app()
        app.go_forward()
    
    def go_up(self, instance):
        """Go to parent directory"""
        app = App.get_running_app()
        app.go_up()
    
    def refresh(self, instance):
        """Refresh current directory"""
        app = App.get_running_app()
        app.refresh_current_directory()
    
    def new_folder(self, instance):
        """Create new folder"""
        app = App.get_running_app()
        app.create_new_folder()
    
    def new_file(self, instance):
        """Create new file"""
        app = App.get_running_app()
        app.create_new_file()

class StatusBar(BoxLayout):
    """Status bar showing current information"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(30)
        self.padding = dp(5)
        
        self.status_label = Label(
            text='Ready',
            size_hint_x=0.7,
            halign='left'
        )
        
        self.info_label = Label(
            text='0 items selected',
            size_hint_x=0.3,
            halign='right'
        )
        
        self.add_widget(self.status_label)
        self.add_widget(self.info_label)
    
    def update_status(self, text: str):
        """Update status text"""
        self.status_label.text = text
    
    def update_info(self, text: str):
        """Update info text"""
        self.info_label.text = text

class NovaExplorerApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Nova Explorer'
        self.current_path = os.path.expanduser('~')
        self.history = []
        self.history_index = -1
        self.settings = settings_manager.SettingsManager()
        self.editor = None
        
    def build(self):
        """Build the main UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        self.toolbar = ToolBar()
        main_layout.add_widget(self.toolbar)
        
        # Address bar
        self.address_bar = AddressBar()
        main_layout.add_widget(self.address_bar)
        
        # Main content area
        content_layout = BoxLayout(orientation='horizontal')
        
        # File list
        self.file_list = FileList()
        content_layout.add_widget(self.file_list)
        
        # Editor area (initially hidden)
        self.editor_area = BoxLayout(orientation='vertical', size_hint_x=0)
        self.editor = editor_widget.EditorWidget()
        self.editor_area.add_widget(self.editor)
        content_layout.add_widget(self.editor_area)
        
        main_layout.add_widget(content_layout)
        
        # Status bar
        self.status_bar = StatusBar()
        main_layout.add_widget(self.status_bar)
        
        # Initialize
        self.navigate_to(self.current_path)
        
        return main_layout
    
    def navigate_to(self, path: str):
        """Navigate to a specific path"""
        if os.path.exists(path):
            # Add to history
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            
            self.history.append(path)
            self.history_index = len(self.history) - 1
            
            # Update UI
            self.current_path = path
            self.file_list.current_path = path
            self.file_list.refresh_files()
            self.address_bar.update_path(path)
            self.status_bar.update_status(f'Navigated to: {path}')
    
    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.current_path = path
            self.file_list.current_path = path
            self.file_list.refresh_files()
            self.address_bar.update_path(path)
            self.status_bar.update_status(f'Back to: {path}')
    
    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.current_path = path
            self.file_list.current_path = path
            self.file_list.refresh_files()
            self.address_bar.update_path(path)
            self.status_bar.update_status(f'Forward to: {path}')
    
    def go_up(self):
        """Go to parent directory"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.navigate_to(parent)
    
    def refresh_current_directory(self):
        """Refresh the current directory"""
        self.file_list.refresh_files()
        self.status_bar.update_status('Directory refreshed')
    
    def create_new_folder(self):
        """Create a new folder"""
        def create_folder(name):
            if name:
                folder_path = os.path.join(self.current_path, name)
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    self.refresh_current_directory()
                    popup.dismiss()
                except Exception as e:
                    self.show_error(f"Error creating folder: {e}")
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(Label(text='Enter folder name:'))
        
        name_input = TextInput(multiline=False)
        content.add_widget(name_input)
        
        button = Button(text='Create', size_hint_y=None, height=dp(40))
        button.bind(on_press=lambda x: create_folder(name_input.text))
        content.add_widget(button)
        
        popup = Popup(title='New Folder', content=content, size_hint=(0.8, 0.4))
        popup.open()
    
    def create_new_file(self):
        """Create a new file"""
        def create_file(name):
            if name:
                file_path = os.path.join(self.current_path, name)
                try:
                    with open(file_path, 'w') as f:
                        f.write('')
                    self.refresh_current_directory()
                    popup.dismiss()
                except Exception as e:
                    self.show_error(f"Error creating file: {e}")
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(Label(text='Enter file name:'))
        
        name_input = TextInput(multiline=False)
        content.add_widget(name_input)
        
        button = Button(text='Create', size_hint_y=None, height=dp(40))
        button.bind(on_press=lambda x: create_file(name_input.text))
        content.add_widget(button)
        
        popup = Popup(title='New File', content=content, size_hint=(0.8, 0.4))
        popup.open()
    
    def open_file_in_editor(self, file_path: str):
        """Open a file in the editor"""
        try:
            # Show editor
            self.editor_area.size_hint_x = 0.6
            self.file_list.size_hint_x = 0.4
            
            # Load file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.editor.load_file(file_path, content)
            self.status_bar.update_status(f'Opened: {os.path.basename(file_path)}')
            
        except Exception as e:
            self.show_error(f"Error opening file: {e}")
    
    def show_error(self, message: str):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(Label(text=message))
        
        button = Button(text='OK', size_hint_y=None, height=dp(40))
        button.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(button)
        
        popup = Popup(title='Error', content=content, size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    NovaExplorerApp().run()