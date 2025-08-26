#!/usr/bin/env python3
"""
Nova Explorer - Professional File Manager with Built-in Editor
The Ultimate Combination of Windows Explorer + Visual Studio Code
Perfect for Unity Development and Professional File Management
STABLE VERSION - No compatibility issues
"""

import os
import sys
import json
import shutil
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Kivy imports - Only essential ones to avoid conflicts
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty

# Set window size and title
Window.size = (1400, 900)
Window.minimum_width = 1000
Window.minimum_height = 700

# Professional color scheme
COLORS = {
    'dark_bg': (0.12, 0.12, 0.14, 1),
    'darker_bg': (0.08, 0.08, 0.10, 1),
    'panel_bg': (0.16, 0.16, 0.18, 1),
    'accent': (0.00, 0.47, 0.84, 1),
    'accent_hover': (0.00, 0.55, 0.95, 1),
    'success': (0.13, 0.59, 0.13, 1),
    'warning': (0.85, 0.65, 0.13, 1),
    'error': (0.80, 0.20, 0.20, 1),
    'text_primary': (0.90, 0.90, 0.90, 1),
    'text_secondary': (0.70, 0.70, 0.70, 1),
    'text_muted': (0.50, 0.50, 0.50, 1),
    'border': (0.25, 0.25, 0.27, 1),
    'selection': (0.26, 0.47, 0.78, 1),
    'editor_bg': (0.10, 0.10, 0.12, 1),
    'editor_line': (0.15, 0.15, 0.17, 1)
}

class ProfessionalButton(Button):
    """Professional styled button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLORS['accent']
        self.color = COLORS['text_primary']
        self.font_size = dp(12)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(32)
        self.padding = dp(10)

class ProfessionalLabel(Label):
    """Professional styled label"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = COLORS['text_primary']
        self.font_size = dp(12)

class ProfessionalTextInput(TextInput):
    """Professional styled text input"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = COLORS['panel_bg']
        self.foreground_color = COLORS['text_primary']
        self.cursor_color = COLORS['accent']
        self.selection_color = COLORS['selection']
        self.font_size = dp(12)
        self.padding = dp(8)

class FileItem(BoxLayout):
    """Professional file/folder item - STABLE VERSION"""
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
        self.height = dp(36)
        self.padding = dp(8)
        self.spacing = dp(12)
        self.background_color = COLORS['panel_bg']
        
        self.update_info()
        self._create_widgets()
    
    def _create_widgets(self):
        """Create professional widget layout"""
        # Icon (folder or file)
        icon_text = "📁" if self.is_folder else "📄"
        self.icon_label = ProfessionalLabel(
            text=icon_text,
            size_hint_x=0.05,
            halign='center',
            valign='middle'
        )
        
        # Name label
        self.name_label = ProfessionalLabel(
            text=self.name,
            size_hint_x=0.45,
            halign='left',
            valign='middle'
        )
        
        # Size label
        self.size_label = ProfessionalLabel(
            text=self.size,
            size_hint_x=0.15,
            halign='center',
            valign='middle',
            color=COLORS['text_secondary']
        )
        
        # Type label
        self.type_label = ProfessionalLabel(
            text=self.get_file_type(),
            size_hint_x=0.15,
            halign='center',
            valign='middle',
            color=COLORS['text_secondary']
        )
        
        # Modified label
        self.modified_label = ProfessionalLabel(
            text=self.modified,
            size_hint_x=0.20,
            halign='center',
            valign='middle',
            color=COLORS['text_secondary']
        )
        
        self.add_widget(self.icon_label)
        self.add_widget(self.name_label)
        self.add_widget(self.size_label)
        self.add_widget(self.type_label)
        self.add_widget(self.modified_label)
    
    def get_file_type(self):
        """Get file type extension"""
        if self.is_folder:
            return "Folder"
        ext = Path(self.file_path).suffix.lower()
        if ext:
            return ext[1:].upper() + " File"
        return "File"
    
    def update_info(self):
        """Update file information"""
        try:
            stat = os.stat(self.file_path)
            self.name = os.path.basename(self.file_path)
            self.is_folder = os.path.isdir(self.file_path)
            
            if self.is_folder:
                self.size = "<DIR>"
            else:
                size_bytes = stat.st_size
                if size_bytes < 1024:
                    self.size = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    self.size = f"{size_bytes // 1024} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    self.size = f"{size_bytes // (1024 * 1024)} MB"
                else:
                    self.size = f"{size_bytes // (1024 * 1024 * 1024)} GB"
            
            self.modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            
            # Update labels
            if hasattr(self, 'name_label'):
                self.name_label.text = self.name
            if hasattr(self, 'size_label'):
                self.size_label.text = self.size
            if hasattr(self, 'modified_label'):
                self.modified_label.text = self.modified
            if hasattr(self, 'type_label'):
                self.type_label.text = self.get_file_type()
                
        except Exception as e:
            print(f"Error updating file info: {e}")

class FileList(ScrollView):
    """Professional file list with selection support - STABLE VERSION"""
    selected_files = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use simple BoxLayout to avoid any layout issues
        self.layout = BoxLayout(orientation='vertical', spacing=dp(1), size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
        self.current_path = os.path.expanduser('~')
        
        # Professional styling
        self.background_color = COLORS['dark_bg']
        self.bar_color = COLORS['accent']
        self.bar_inactive_color = COLORS['border']
        
        self.refresh_files()
    
    def refresh_files(self):
        """Refresh the file list"""
        self.layout.clear_widgets()
        self.selected_files.clear()
        
        try:
            # Add header
            header = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(32),
                padding=dp(8),
                spacing=dp(12)
            )
            header.background_color = COLORS['darker_bg']
            
            header.add_widget(ProfessionalLabel(text="Name", size_hint_x=0.50, halign='left'))
            header.add_widget(ProfessionalLabel(text="Size", size_hint_x=0.15, halign='center'))
            header.add_widget(ProfessionalLabel(text="Type", size_hint_x=0.15, halign='center'))
            header.add_widget(ProfessionalLabel(text="Modified", size_hint_x=0.20, halign='center'))
            
            self.layout.add_widget(header)
            
            # Add parent directory option
            if self.current_path != os.path.dirname(self.current_path):
                # Create a simple button for parent directory
                parent_btn = Button(
                    text='📂 ..',
                    size_hint_y=None,
                    height=dp(36),
                    background_color=COLORS['panel_bg'],
                    color=COLORS['text_primary'],
                    font_size=dp(12)
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
            error_label = ProfessionalLabel(text=f"Error loading directory: {e}")
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
            if hasattr(child, 'background_color'):
                child.background_color = COLORS['panel_bg']
        
        file_item.background_color = COLORS['selection']
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
    """Professional address bar"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.padding = dp(8)
        self.spacing = dp(8)
        self.background_color = COLORS['panel_bg']
        
        # Path input
        self.path_input = ProfessionalTextInput(
            multiline=False,
            size_hint_x=0.8
        )
        self.path_input.bind(on_text_validate=self.navigate)
        
        # Go button
        self.go_button = ProfessionalButton(
            text='Go',
            size_hint_x=0.1,
            background_color=COLORS['accent']
        )
        self.go_button.bind(on_press=self.navigate)
        
        # Refresh button
        self.refresh_button = ProfessionalButton(
            text='⟳',
            size_hint_x=0.1,
            background_color=COLORS['success']
        )
        self.refresh_button.bind(on_press=self.refresh)
        
        self.add_widget(self.path_input)
        self.add_widget(self.go_button)
        self.add_widget(self.refresh_button)
    
    def navigate(self, instance):
        """Navigate to the entered path"""
        path = self.path_input.text.strip()
        if os.path.exists(path):
            app = App.get_running_app()
            app.navigate_to(path)
    
    def refresh(self, instance):
        """Refresh current directory"""
        app = App.get_running_app()
        app.refresh_current_directory()
    
    def update_path(self, path):
        """Update the displayed path"""
        self.path_input.text = path

class ToolBar(BoxLayout):
    """Professional toolbar - STABLE VERSION"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = dp(8)
        self.spacing = dp(8)
        self.background_color = COLORS['panel_bg']
        
        # Navigation buttons
        self.back_btn = ProfessionalButton(
            text='← Back',
            size_hint_x=None,
            width=dp(80),
            background_color=COLORS['accent']
        )
        self.back_btn.bind(on_press=self.go_back)
        
        self.forward_btn = ProfessionalButton(
            text='Forward →',
            size_hint_x=None,
            width=dp(80),
            background_color=COLORS['accent']
        )
        self.forward_btn.bind(on_press=self.go_forward)
        
        self.up_btn = ProfessionalButton(
            text='↑ Up',
            size_hint_x=None,
            width=dp(60),
            background_color=COLORS['accent']
        )
        self.up_btn.bind(on_press=self.go_up)
        
        # Action buttons
        self.new_folder_btn = ProfessionalButton(
            text='📁 New Folder',
            size_hint_x=None,
            width=dp(120),
            background_color=COLORS['success']
        )
        self.new_folder_btn.bind(on_press=self.new_folder)
        
        self.new_file_btn = ProfessionalButton(
            text='📄 New File',
            size_hint_x=None,
            width=dp(120),
            background_color=COLORS['success']
        )
        self.new_file_btn.bind(on_press=self.new_file)
        
        self.copy_btn = ProfessionalButton(
            text='📋 Copy',
            size_hint_x=None,
            width=dp(80),
            background_color=COLORS['warning']
        )
        self.copy_btn.bind(on_press=self.copy_files)
        
        self.delete_btn = ProfessionalButton(
            text='🗑️ Delete',
            size_hint_x=None,
            width=dp(80),
            background_color=COLORS['error']
        )
        self.delete_btn.bind(on_press=self.delete_files)
        
        # Add widgets
        self.add_widget(self.back_btn)
        self.add_widget(self.forward_btn)
        self.add_widget(self.up_btn)
        
        # Add separator using a simple label
        separator_label = Label(text='|', size_hint_x=None, width=dp(20), color=COLORS['border'])
        self.add_widget(separator_label)
        
        self.add_widget(self.new_folder_btn)
        self.add_widget(self.new_file_btn)
        
        # Add another separator
        separator_label2 = Label(text='|', size_hint_x=None, width=dp(20), color=COLORS['border'])
        self.add_widget(separator_label2)
        
        self.add_widget(self.copy_btn)
        self.add_widget(self.delete_btn)
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
    
    def new_folder(self, instance):
        """Create new folder"""
        app = App.get_running_app()
        app.create_new_folder()
    
    def new_file(self, instance):
        """Create new file"""
        app = App.get_running_app()
        app.create_new_file()
    
    def copy_files(self, instance):
        """Copy selected files"""
        app = App.get_running_app()
        app.copy_selected_files()
    
    def delete_files(self, instance):
        """Delete selected files"""
        app = App.get_running_app()
        app.delete_selected_files()

class StatusBar(BoxLayout):
    """Professional status bar"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(32)
        self.padding = dp(8)
        self.spacing = dp(16)
        self.background_color = COLORS['darker_bg']
        
        self.status_label = ProfessionalLabel(
            text='Ready',
            size_hint_x=0.4,
            halign='left'
        )
        
        self.path_label = ProfessionalLabel(
            text='',
            size_hint_x=0.4,
            halign='center',
            color=COLORS['text_secondary']
        )
        
        self.info_label = ProfessionalLabel(
            text='0 items selected',
            size_hint_x=0.2,
            halign='right',
            color=COLORS['text_secondary']
        )
        
        self.add_widget(self.status_label)
        self.add_widget(self.path_label)
        self.add_widget(self.info_label)
    
    def update_status(self, text: str):
        """Update status text"""
        self.status_label.text = text
    
    def update_path(self, text: str):
        """Update path text"""
        self.path_label.text = text
    
    def update_info(self, text: str):
        """Update info text"""
        self.info_label.text = text

class ProfessionalEditor(BoxLayout):
    """Professional text editor - STABLE VERSION"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(8)
        self.spacing = dp(8)
        self.background_color = COLORS['editor_bg']
        
        # Editor toolbar
        toolbar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
            padding=dp(4)
        )
        toolbar.background_color = COLORS['panel_bg']
        
        # File info label
        self.file_label = ProfessionalLabel(
            text='No file open',
            size_hint_x=0.5,
            halign='left'
        )
        
        # Save button
        self.save_btn = ProfessionalButton(
            text='💾 Save',
            size_hint_x=0.15,
            background_color=COLORS['success']
        )
        self.save_btn.bind(on_press=self.save_file)
        
        # Save As button
        self.save_as_btn = ProfessionalButton(
            text='💾 Save As',
            size_hint_x=0.15,
            background_color=COLORS['accent']
        )
        self.save_as_btn.bind(on_press=self.save_file_as)
        
        # Close button
        self.close_btn = ProfessionalButton(
            text='✕ Close',
            size_hint_x=0.15,
            background_color=COLORS['error']
        )
        self.close_btn.bind(on_press=self.close_editor)
        
        toolbar.add_widget(self.file_label)
        toolbar.add_widget(self.save_btn)
        toolbar.add_widget(self.save_as_btn)
        toolbar.add_widget(self.close_btn)
        
        # Text editor
        self.text_input = ProfessionalTextInput(
            multiline=True,
            font_size=dp(14),
            background_color=COLORS['editor_bg'],
            foreground_color=COLORS['text_primary'],
            cursor_color=COLORS['accent'],
            selection_color=COLORS['selection'],
            write_tab=False,
            tab_width=4
        )
        
        # Scroll view for text editor
        scroll_view = ScrollView()
        scroll_view.add_widget(self.text_input)
        scroll_view.background_color = COLORS['editor_bg']
        
        self.add_widget(toolbar)
        self.add_widget(scroll_view)
        
        self.current_file = ''
        self.is_modified = False
    
    def load_file(self, file_path: str, content: str = None):
        """Load a file into the editor"""
        try:
            self.current_file = file_path
            self.file_label.text = f'📝 {os.path.basename(file_path)}'
            
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            self.text_input.text = content
            self.is_modified = False
            
        except Exception as e:
            print(f"Error loading file: {e}")
    
    def save_file(self, instance=None):
        """Save the current file"""
        if not self.current_file:
            return
        
        try:
            # Create backup
            if os.path.exists(self.current_file):
                backup_path = self.current_file + '.bak'
                shutil.copy2(self.current_file, backup_path)
            
            # Save the file
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.text_input.text)
            
            self.is_modified = False
            self.file_label.text = f'📝 {os.path.basename(self.current_file)} (Saved)'
            
            # Schedule status reset
            Clock.schedule_once(self.reset_save_status, 2)
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def save_file_as(self, instance=None):
        """Save file as"""
        # This would open a save dialog in a full implementation
        self.save_file()
    
    def reset_save_status(self, dt):
        """Reset the save status display"""
        if self.current_file:
            self.file_label.text = f'📝 {os.path.basename(self.current_file)}'
    
    def close_editor(self, instance=None):
        """Close the editor"""
        if self.is_modified:
            # Ask user if they want to save
            self.show_save_prompt()
        else:
            self.hide_editor()
    
    def hide_editor(self):
        """Hide the editor area"""
        self.size_hint_x = 0
        self.current_file = ''
        self.text_input.text = ''
        self.is_modified = False
    
    def show_save_prompt(self):
        """Show save prompt dialog"""
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(ProfessionalLabel(
            text='Do you want to save changes before closing?',
            size_hint_y=None,
            height=dp(40)
        ))
        
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        save_btn = ProfessionalButton(text='Save', background_color=COLORS['success'])
        save_btn.bind(on_press=lambda x: self.save_and_close(popup))
        
        dont_save_btn = ProfessionalButton(text="Don't Save", background_color=COLORS['warning'])
        dont_save_btn.bind(on_press=lambda x: self.close_without_save(popup))
        
        cancel_btn = ProfessionalButton(text='Cancel', background_color=COLORS['error'])
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(dont_save_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Save Changes?',
            content=content,
            size_hint=(0.8, 0.4),
            background=COLORS['panel_bg']
        )
        popup.open()
    
    def save_and_close(self, popup):
        """Save file and close editor"""
        popup.dismiss()
        self.save_file()
        self.hide_editor()
    
    def close_without_save(self, popup):
        """Close editor without saving"""
        popup.dismiss()
        self.hide_editor()

class NovaExplorerApp(App):
    """Professional Nova Explorer Application - STABLE VERSION"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Nova Explorer - Professional File Manager'
        self.current_path = os.path.expanduser('~')
        self.history = []
        self.history_index = -1
        self.clipboard = []
        
    def build(self):
        """Build the professional UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        main_layout.background_color = COLORS['dark_bg']
        
        # Toolbar
        self.toolbar = ToolBar()
        main_layout.add_widget(self.toolbar)
        
        # Address bar
        self.address_bar = AddressBar()
        main_layout.add_widget(self.address_bar)
        
        # Main content area
        content_layout = BoxLayout(orientation='horizontal')
        content_layout.spacing = dp(8)
        content_layout.padding = dp(8)
        
        # File list
        self.file_list = FileList()
        content_layout.add_widget(self.file_list)
        
        # Editor area (initially hidden)
        self.editor_area = BoxLayout(orientation='vertical', size_hint_x=0)
        self.editor = ProfessionalEditor()
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
            self.status_bar.update_status(f'📁 Navigated to: {path}')
            self.status_bar.update_path(path)
    
    def go_back(self):
        """Go back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.current_path = path
            self.file_list.current_path = path
            self.file_list.refresh_files()
            self.address_bar.update_path(path)
            self.status_bar.update_status(f'⬅️ Back to: {path}')
    
    def go_forward(self):
        """Go forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.current_path = path
            self.file_list.current_path = path
            self.file_list.refresh_files()
            self.address_bar.update_path(path)
            self.status_bar.update_status(f'➡️ Forward to: {path}')
    
    def go_up(self):
        """Go to parent directory"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.navigate_to(parent)
    
    def refresh_current_directory(self):
        """Refresh the current directory"""
        self.file_list.refresh_files()
        self.status_bar.update_status('🔄 Directory refreshed')
    
    def create_new_folder(self):
        """Create a new folder"""
        def create_folder(name):
            if name:
                folder_path = os.path.join(self.current_path, name)
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    self.refresh_current_directory()
                    popup.dismiss()
                    self.status_bar.update_status(f'✅ Created folder: {name}')
                except Exception as e:
                    self.show_error(f"Error creating folder: {e}")
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(ProfessionalLabel(text='Enter folder name:'))
        
        name_input = ProfessionalTextInput(multiline=False)
        content.add_widget(name_input)
        
        button = ProfessionalButton(text='Create', background_color=COLORS['success'])
        button.bind(on_press=lambda x: create_folder(name_input.text))
        content.add_widget(button)
        
        popup = Popup(
            title='New Folder',
            content=content,
            size_hint=(0.8, 0.4),
            background=COLORS['panel_bg']
        )
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
                    self.status_bar.update_status(f'✅ Created file: {name}')
                except Exception as e:
                    self.show_error(f"Error creating file: {e}")
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(ProfessionalLabel(text='Enter file name:'))
        
        name_input = ProfessionalTextInput(multiline=False)
        content.add_widget(name_input)
        
        button = ProfessionalButton(text='Create', background_color=COLORS['success'])
        button.bind(on_press=lambda x: create_file(name_input.text))
        content.add_widget(button)
        
        popup = Popup(
            title='New File',
            content=content,
            size_hint=(0.8, 0.4),
            background=COLORS['panel_bg']
        )
        popup.open()
    
    def copy_selected_files(self):
        """Copy selected files to clipboard"""
        if self.file_list.selected_files:
            self.clipboard = self.file_list.selected_files.copy()
            self.status_bar.update_status(f'📋 Copied {len(self.clipboard)} items to clipboard')
        else:
            self.status_bar.update_status('⚠️ No files selected')
    
    def delete_selected_files(self):
        """Delete selected files"""
        if not self.file_list.selected_files:
            self.status_bar.update_status('⚠️ No files selected')
            return
        
        def confirm_delete(instance):
            try:
                for file_path in self.file_list.selected_files:
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                
                self.refresh_current_directory()
                popup.dismiss()
                self.status_bar.update_status(f'🗑️ Deleted {len(self.file_list.selected_files)} items')
            except Exception as e:
                self.show_error(f"Error deleting files: {e}")
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(ProfessionalLabel(
            text=f'Are you sure you want to delete {len(self.file_list.selected_files)} items?',
            size_hint_y=None,
            height=dp(40)
        ))
        
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        delete_btn = ProfessionalButton(text='Delete', background_color=COLORS['error'])
        delete_btn.bind(on_press=confirm_delete)
        
        cancel_btn = ProfessionalButton(text='Cancel', background_color=COLORS['accent'])
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(delete_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4),
            background=COLORS['panel_bg']
        )
        popup.open()
    
    def open_file_in_editor(self, file_path: str):
        """Open a file in the editor"""
        try:
            # Check if it's a text file
            text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.c', '.cpp', '.h', '.java', '.cs', '.php', '.rb', '.pl', '.sh', '.bat', '.ps1', '.sql', '.log', '.ini', '.cfg', '.conf'}
            ext = Path(file_path).suffix.lower()
            
            if ext in text_extensions or self.is_text_file(file_path):
                # Show editor
                self.editor_area.size_hint_x = 0.6
                self.file_list.size_hint_x = 0.4
                
                # Load file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.load_file(file_path, content)
                self.status_bar.update_status(f'📝 Opened: {os.path.basename(file_path)}')
            else:
                # Try to open with default application
                os.startfile(file_path)
                self.status_bar.update_status(f'🚀 Opened with default app: {os.path.basename(file_path)}')
            
        except Exception as e:
            self.show_error(f"Error opening file: {e}")
    
    def is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                try:
                    chunk.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except Exception:
            return False
    
    def show_error(self, message: str):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(ProfessionalLabel(text=message))
        
        button = ProfessionalButton(text='OK', background_color=COLORS['error'])
        button.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(button)
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, 0.4),
            background=COLORS['panel_bg']
        )
        popup.open()

if __name__ == '__main__':
    NovaExplorerApp().run()