"""
Text Editor Widget
Simple text editor with syntax highlighting support
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
import os
import fs_operations

class EditorWidget(BoxLayout):
    """Text editor widget with basic features"""
    
    current_file = StringProperty('')
    is_modified = BooleanProperty(False)
    
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
        self.text_input.bind(text=self.on_text_changed)
        
        # Scroll view for text editor
        scroll_view = ScrollView()
        scroll_view.add_widget(self.text_input)
        
        self.add_widget(toolbar)
        self.add_widget(scroll_view)
        
        # Auto-save timer
        self.auto_save_timer = None
    
    def load_file(self, file_path: str, content: str = None):
        """Load a file into the editor"""
        try:
            self.current_file = file_path
            self.file_label.text = f'Editing: {os.path.basename(file_path)}'
            
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            self.text_input.text = content
            self.is_modified = False
            
            # Start auto-save if enabled
            self.start_auto_save()
            
        except Exception as e:
            print(f"Error loading file: {e}")
    
    def save_file(self, instance=None):
        """Save the current file"""
        if not self.current_file:
            return
        
        try:
            # Create backup before saving
            if os.path.exists(self.current_file):
                fs_operations.FileOperations.backup_file(self.current_file)
            
            # Save the file
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.text_input.text)
            
            self.is_modified = False
            self.file_label.text = f'Editing: {os.path.basename(self.current_file)} (Saved)'
            
            # Schedule status reset
            Clock.schedule_once(self.reset_save_status, 2)
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def reset_save_status(self, dt):
        """Reset the save status display"""
        if self.current_file:
            self.file_label.text = f'Editing: {os.path.basename(self.current_file)}'
    
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
        self.stop_auto_save()
    
    def on_text_changed(self, instance, value):
        """Handle text changes"""
        if self.current_file:
            self.is_modified = True
            self.file_label.text = f'Editing: {os.path.basename(self.current_file)} *'
    
    def start_auto_save(self):
        """Start auto-save timer"""
        self.stop_auto_save()
        self.auto_save_timer = Clock.schedule_interval(self.auto_save, 30)  # Save every 30 seconds
    
    def stop_auto_save(self):
        """Stop auto-save timer"""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
    
    def auto_save(self, dt):
        """Auto-save function"""
        if self.is_modified and self.current_file:
            self.save_file()
    
    def show_save_prompt(self):
        """Show save prompt dialog"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        
        content = BoxLayout(orientation='vertical', padding=dp(20))
        content.add_widget(Label(
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
        
        save_btn = Button(text='Save', background_color=(0.2, 0.8, 0.2, 1))
        save_btn.bind(on_press=lambda x: self.save_and_close(popup))
        
        dont_save_btn = Button(text="Don't Save", background_color=(0.8, 0.8, 0.2, 1))
        dont_save_btn.bind(on_press=lambda x: self.close_without_save(popup))
        
        cancel_btn = Button(text='Cancel', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        button_layout.add_widget(save_btn)
        button_layout.add_widget(dont_save_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        
        popup = Popup(
            title='Save Changes?',
            content=content,
            size_hint=(0.8, 0.4)
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
    
    def get_text(self) -> str:
        """Get current text content"""
        return self.text_input.text
    
    def set_text(self, text: str):
        """Set text content"""
        self.text_input.text = text
    
    def insert_text(self, text: str):
        """Insert text at cursor position"""
        self.text_input.insert_text(text)
    
    def get_selection(self) -> str:
        """Get selected text"""
        return self.text_input.selection_text
    
    def find_text(self, search_text: str, case_sensitive: bool = False):
        """Find text in editor"""
        # Simple text search implementation
        content = self.text_input.text
        if not case_sensitive:
            content = content.lower()
            search_text = search_text.lower()
        
        if search_text in content:
            # Highlight the first occurrence
            start = content.find(search_text)
            self.text_input.cursor = (start, start + len(search_text))
            return True
        return False
    
    def replace_text(self, search_text: str, replace_text: str, case_sensitive: bool = False):
        """Replace text in editor"""
        content = self.text_input.text
        if not case_sensitive:
            # Case-insensitive replace
            import re
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            new_content = pattern.sub(replace_text, content)
        else:
            new_content = content.replace(search_text, replace_text)
        
        self.text_input.text = new_content
        return content != new_content