#!/usr/bin/env python3
"""
Nova Explorer - Simplified Version
Advanced File Manager with Built-in Editor
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
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.graphics import Color, Rectangle

# Set window size and title
Window.size = (1200, 800)
Window.minimum_width = 800
Window.minimum_height = 600

# Simple separator widget
class Separator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

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
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # Set background color based on selection
        with self.canvas.before:
            Color(0.2, 0.4, 0.8, 1) if self.is_selected else Color(0.3, 0.3, 0.3, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg, is_selected=self._update_bg)
        
        self.update_info()
        self._create_widgets()
    
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        if hasattr(self, 'bg_rect'):
            with self.canvas.before:
                Color(0.2, 0.4, 0.8, 1) if self.is_selected else Color(0.3, 0.3, 0.3, 1)
    
    def _create_widgets(self):
        """Create the widget layout"""
        # Name label
        self.name_label = Label(
            text=self.name,
            size_hint_x=0.5,
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        
        # Size label
        self.size_label = Label(
            text=self.size,
            size_hint_x=0.2,
            halign='center',
            valign='middle',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.size_label.bind(size=self.size_label.setter('text_size'))
        
        # Modified label
        self.modified_label = Label(
            text=self.modified,
            size_hint_x=0.3,
            halign='center',
            valign='middle',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.modified_label.bind(size=self.modified_label.setter('text_size'))
        
        self.add_widget(self.name_label)
        self.add_widget(self.size_label)
        self.add_widget(self.modified_label)
    
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
            
            # Update labels
            if hasattr(self, 'name_label'):
                self.name_label.text = self.name
            if hasattr(self, 'size_label'):
                self.size_label.text = self.size
            if hasattr(self, 'modified_label'):
                self.modified_label.text = self.modified
                
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
        
        # Set background color
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.refresh_files()
    
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
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
        
        # Set background color
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
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
    
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
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
        
        # Set background color
        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
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
    
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
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
        
        # Set background color
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
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
    
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def update_status(self, text: str):
        """Update status text"""
        self.status_label.text = text
    
    def update_info(self, text: str):
        """Update info text"""
        self.info_label.text = text

class SimpleEditor(BoxLayout):
    """Simple text editor widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(5)
        self.spacing = dp(5)
        
        # Editor toolbar
        toolbar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )
        
        # File info label
        self.file_label = Label(
            text='No file open',
            size_hint_x=0.6,
            halign='left'
        )
        
        # Save button
        self.save_btn = Button(
            text='Save',
            size_hint_x=0.2,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.save_btn.bind(on_press=self.save_file)
        
        # Close button
        self.close_btn = Button(
            text='Close',
            size_hint_x=0.2,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.close_btn.bind(on_press=self.close_editor)
        
        toolbar.add_widget(self.file_label)
        toolbar.add_widget(self.save_btn)
        toolbar.add_widget(self.close_btn)
        
        # Text editor
        self.text_input = TextInput(
            multiline=True,
            font_size=dp(14),
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            cursor_color=(1, 1, 1, 1),
            selection_color=(0.2, 0.4, 0.8, 1),
            write_tab=False,
            tab_width=4
        )
        
        # Scroll view for text editor
        scroll_view = ScrollView()
        scroll_view.add_widget(self.text_input)
        
        self.add_widget(toolbar)
        self.add_widget(scroll_view)
        
        self.current_file = ''
    
    def load_file(self, file_path: str, content: str = None):
        """Load a file into the editor"""
        try:
            self.current_file = file_path
            self.file_label.text = f'Editing: {os.path.basename(file_path)}'
            
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            self.text_input.text = content
            
        except Exception as e:
            print(f"Error loading file: {e}")
    
    def save_file(self, instance=None):
        """Save the current file"""
        if not self.current_file:
            return
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.text_input.text)
            
            self.file_label.text = f'Editing: {os.path.basename(self.current_file)} (Saved)'
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def close_editor(self, instance=None):
        """Close the editor"""
        self.size_hint_x = 0
        self.current_file = ''
        self.text_input.text = ''

class NovaExplorerApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Nova Explorer'
        self.current_path = os.path.expanduser('~')
        self.history = []
        self.history_index = -1
        
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
        self.editor = SimpleEditor()
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