import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, colorchooser
from tkinter import font as tkfont
import os
import sys
import json
import subprocess
import threading
import time
import re
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer, CSharpLexer, PythonLexer, JavascriptLexer, HtmlLexer, CssLexer, JsonLexer
from pygments.token import Token
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
import psutil
from PIL import Image, ImageTk
import requests

class ProfessionalAnoraEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Anora Editor Pro - Professional Code Editor for Unity")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Professional color scheme (VS Code Dark+ inspired)
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#d4d4d4',
            'select_bg': '#264f78',
            'select_fg': '#ffffff',
            'insert_bg': '#d4d4d4',
            'tab_bg': '#2d2d30',
            'tab_active_bg': '#3e3e42',
            'tab_fg': '#cccccc',
            'menu_bg': '#2d2d30',
            'menu_fg': '#cccccc',
            'button_bg': '#3e3e42',
            'button_fg': '#cccccc',
            'entry_bg': '#3e3e42',
            'entry_fg': '#cccccc',
            'sidebar_bg': '#252526',
            'sidebar_fg': '#cccccc',
            'status_bg': '#007acc',
            'status_fg': '#ffffff',
            'line_numbers_bg': '#1e1e1e',
            'line_numbers_fg': '#858585',
            'current_line_bg': '#2a2d2e',
            'bracket_bg': '#ffd700',
            'error_bg': '#f44747',
            'warning_bg': '#ffcc02',
            'success_bg': '#4ec9b0'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Enhanced variables
        self.tabs = []
        self.current_tab = None
        self.closed_tabs_stack: List[dict] = []
        self.recent_files: List[str] = []
        self.recent_menu = None
        self.session_path = str(Path.home() / ".anora_editor_pro_session.json")
        self.autosave_after_id = None
        self.always_on_top = tk.BooleanVar()
        self.fullscreen = tk.BooleanVar()
        self.search_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.search_results = []
        self.current_search_index = 0
        self.show_line_numbers = tk.BooleanVar(value=True)
        self.show_minimap = tk.BooleanVar(value=True)
        self.show_sidebar = tk.BooleanVar(value=True)
        self.auto_complete = tk.BooleanVar(value=True)
        self.bracket_matching = tk.BooleanVar(value=True)
        self.word_wrap = tk.BooleanVar(value=False)
        self.font_size = tk.IntVar(value=14)
        self.font_family = tk.StringVar(value="Consolas")
        
        # Unity-specific variables
        self.unity_project_path = None
        self.unity_api_cache = {}
        
        # Performance variables
        self.highlight_timer = None
        self.autosave_timer = None
        
        self.setup_ui()
        self.setup_bindings()
        self.setup_native_drag_drop()
        self.load_session()
        self.detect_unity_project()
        self.root.protocol("WM_DELETE_WINDOW", self.on_app_close)
        
    def setup_ui(self):
        """Create professional UI with modern design"""
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main editor area
        self.create_editor_area()
        
        # Create status bar
        self.create_status_bar()
        
    def setup_styles(self):
        """Configure professional ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook style
        style.configure('Editor.TNotebook', background=self.colors['bg'])
        style.configure('Editor.TNotebook.Tab', 
                       background=self.colors['tab_bg'],
                       foreground=self.colors['tab_fg'],
                       padding=[15, 8],
                       font=('Segoe UI', 9))
        style.map('Editor.TNotebook.Tab',
                 background=[('selected', self.colors['tab_active_bg'])])
        
        # Treeview style
        style.configure('Sidebar.Treeview',
                       background=self.colors['sidebar_bg'],
                       foreground=self.colors['sidebar_fg'],
                       fieldbackground=self.colors['sidebar_bg'],
                       font=('Segoe UI', 9))
        style.configure('Sidebar.Treeview.Heading',
                       background=self.colors['sidebar_bg'],
                       foreground=self.colors['sidebar_fg'],
                       font=('Segoe UI', 9, 'bold'))
        
        # Button styles
        style.configure('Toolbar.TButton',
                       background=self.colors['button_bg'],
                       foreground=self.colors['button_fg'],
                       padding=[8, 4],
                       font=('Segoe UI', 9))
        
    def create_sidebar(self):
        """Create professional sidebar with project explorer"""
        if not self.show_sidebar.get():
            return
            
        self.sidebar_frame = ttk.Frame(self.main_container, width=250)
        self.main_container.add(self.sidebar_frame, weight=0)
        
        # Sidebar header
        header_frame = ttk.Frame(self.sidebar_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="EXPLORER", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        
        # Project tree
        self.project_tree = ttk.Treeview(self.sidebar_frame, style='Sidebar.Treeview', show='tree')
        self.project_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for tree
        tree_scroll = ttk.Scrollbar(self.sidebar_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.project_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Bind tree events
        self.project_tree.bind('<Double-1>', self.on_tree_double_click)
        self.project_tree.bind('<Button-3>', self.on_tree_right_click)
        
    def create_editor_area(self):
        """Create main editor area with enhanced features"""
        self.editor_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.editor_frame, weight=1)
        
        # Toolbar
        self.create_toolbar()
        
        # Search panel
        self.create_search_panel()
        
        # Main notebook
        self.notebook = ttk.Notebook(self.editor_frame, style='Editor.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind notebook events
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
    def create_toolbar(self):
        """Create professional toolbar with icons"""
        toolbar_frame = ttk.Frame(self.editor_frame)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # File operations
        ttk.Button(toolbar_frame, text="📄 New", command=self.new_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="📂 Open", command=self.open_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="💾 Save", command=self.save_file, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Edit operations
        ttk.Button(toolbar_frame, text="🔍 Find", command=self.show_search, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="🔄 Replace", command=self.show_replace, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # View options
        ttk.Checkbutton(toolbar_frame, text="📊 Line Numbers", variable=self.show_line_numbers, 
                       command=self.toggle_line_numbers, style='Toolbar.TCheckbutton').pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(toolbar_frame, text="🗺️ Minimap", variable=self.show_minimap, 
                       command=self.toggle_minimap, style='Toolbar.TCheckbutton').pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Window controls
        ttk.Button(toolbar_frame, text="📌 Pin", command=self.toggle_always_on_top, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar_frame, text="⛶ Full", command=self.toggle_fullscreen, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        
        # Unity integration
        if self.unity_project_path:
            ttk.Button(toolbar_frame, text="🎮 Unity", command=self.open_unity_project, style='Toolbar.TButton').pack(side=tk.RIGHT, padx=2)
        
    def create_search_panel(self):
        """Create enhanced search and replace panel"""
        self.search_frame = ttk.Frame(self.editor_frame)
        
        # Search controls
        search_controls = ttk.Frame(self.search_frame)
        search_controls.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(search_controls, text="Find:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_controls, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_controls, text="🔍", command=self.find_text, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="⬆️", command=self.find_previous, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="⬇️", command=self.find_next, width=3).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(search_controls, text="Replace:").pack(side=tk.LEFT, padx=(10, 0))
        self.replace_entry = ttk.Entry(search_controls, textvariable=self.replace_var, width=30)
        self.replace_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_controls, text="🔄", command=self.replace_text, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_controls, text="🔄 All", command=self.replace_all, width=6).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(search_controls, text="❌", command=self.hide_search, width=3).pack(side=tk.RIGHT, padx=2)
        
        # Search options
        options_frame = ttk.Frame(self.search_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.case_sensitive = tk.BooleanVar()
        self.regex_search = tk.BooleanVar()
        self.whole_word = tk.BooleanVar()
        
        ttk.Checkbutton(options_frame, text="Case Sensitive", variable=self.case_sensitive).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Regex", variable=self.regex_search).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(options_frame, text="Whole Word", variable=self.whole_word).pack(side=tk.LEFT, padx=5)
        
        # Initially hide search panel
        self.search_frame.pack_forget()
        
    def create_status_bar(self):
        """Create professional status bar with enhanced information"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Left side - file info
        self.file_info_label = ttk.Label(self.status_frame, text="Ready", font=('Segoe UI', 9))
        self.file_info_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Center - position info
        self.position_label = ttk.Label(self.status_frame, text="Line 1, Col 1", font=('Segoe UI', 9))
        self.position_label.pack(side=tk.LEFT, padx=20, pady=2)
        
        # Right side - encoding and other info
        self.encoding_label = ttk.Label(self.status_frame, text="UTF-8", font=('Segoe UI', 9))
        self.encoding_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.file_size_label = ttk.Label(self.status_frame, text="0 KB", font=('Segoe UI', 9))
        self.file_size_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Unity project indicator
        if self.unity_project_path:
            self.unity_label = ttk.Label(self.status_frame, text="🎮 Unity Project", 
                                       foreground=self.colors['success_bg'], font=('Segoe UI', 9, 'bold'))
            self.unity_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def setup_native_drag_drop(self):
        """Setup native drag and drop without external dependencies"""
        # Bind drag and drop events
        self.root.bind('<B1-Motion>', self.on_drag)
        self.root.bind('<ButtonRelease-1>', self.on_drop)
        self.root.bind('<Enter>', self.on_drag_enter)
        self.root.bind('<Leave>', self.on_drag_leave)
        
        # Enable file dropping on the entire window
        self.root.drop_target_register('*')
        
    def on_drag_enter(self, event):
        """Handle drag enter event"""
        self.root.configure(cursor='hand2')
        
    def on_drag_leave(self, event):
        """Handle drag leave event"""
        self.root.configure(cursor='')
        
    def on_drag(self, event):
        """Handle drag event"""
        pass
        
    def on_drop(self, event):
        """Handle file drop event"""
        try:
            # Get dropped files from clipboard or selection
            files = self.root.selection_get(selection='DND_Files')
            if files:
                for file_path in files.split():
                    if os.path.exists(file_path):
                        self.open_file_path(file_path)
        except:
            # Fallback: try to get from clipboard
            try:
                clipboard_content = self.root.clipboard_get()
                if os.path.exists(clipboard_content):
                    self.open_file_path(clipboard_content)
            except:
                pass
                
    def open_file_path(self, file_path):
        """Open file from path with enhanced error handling"""
        try:
            self.create_new_tab(file_path)
            self.add_recent_file(file_path)
            self.update_project_tree()
            self.update_status(f"Opened: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
            
    def create_new_tab(self, file_path=None):
        """Create new tab with enhanced features"""
        # Create tab frame
        tab_frame = ttk.Frame(self.notebook)
        
        # Create text widget with line numbers
        text_frame = ttk.Frame(tab_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, 
                                   width=6, 
                                   bg=self.colors['line_numbers_bg'],
                                   fg=self.colors['line_numbers_fg'],
                                   font=(self.font_family.get(), self.font_size.get()),
                                   relief=tk.FLAT,
                                   state=tk.DISABLED,
                                   padx=5,
                                   pady=5)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text widget
        text_widget = tk.Text(text_frame,
                             bg=self.colors['bg'],
                             fg=self.colors['fg'],
                             insertbackground=self.colors['insert_bg'],
                             selectbackground=self.colors['select_bg'],
                             selectforeground=self.colors['select_fg'],
                             font=(self.font_family.get(), self.font_size.get()),
                             relief=tk.FLAT,
                             padx=10,
                             pady=5,
                             wrap=tk.WORD if self.word_wrap.get() else tk.NONE)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        text_widget.bind('<KeyRelease>', self.on_text_change)
        text_widget.bind('<Button-1>', self.update_line_numbers)
        text_widget.bind('<Key>', self.on_key_press)
        
        # Load file content
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_widget.insert('1.0', content)
                self.update_line_numbers()
                self.highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {str(e)}")
        
        # Create tab info
        tab_info = {
            'frame': tab_frame,
            'text': text_widget,
            'line_numbers': self.line_numbers,
            'file_path': file_path,
            'modified': False,
            'encoding': 'utf-8'
        }
        
        # Add to notebook
        title = os.path.basename(file_path) if file_path else f"Untitled {len(self.tabs) + 1}"
        self.notebook.add(tab_frame, text=title)
        
        # Add to tabs list
        self.tabs.append(tab_info)
        self.current_tab = len(self.tabs) - 1
        
        # Select the new tab
        self.notebook.select(self.current_tab)
        
        return tab_info
        
    def on_key_press(self, event):
        """Handle key press events for enhanced features"""
        if self.current_tab is None or not self.tabs:
            return
            
        # Auto-completion
        if self.auto_complete.get() and event.char in '({[':
            self.insert_matching_bracket(event.char)
            
        # Bracket matching
        if self.bracket_matching.get():
            self.highlight_matching_brackets()
            
        # Update line numbers
        self.root.after(10, self.update_line_numbers)
        
    def insert_matching_bracket(self, opening_bracket):
        """Insert matching closing bracket"""
        brackets = {'(': ')', '{': '}', '[': ']'}
        if opening_bracket in brackets:
            closing_bracket = brackets[opening_bracket]
            self.tabs[self.current_tab]['text'].insert(tk.INSERT, closing_bracket)
            # Move cursor back
            self.tabs[self.current_tab]['text'].mark_set(tk.INSERT, f"{tk.INSERT}-1c")
            
    def highlight_matching_brackets(self):
        """Highlight matching brackets"""
        # Implementation for bracket highlighting
        pass
        
    def toggle_line_numbers(self):
        """Toggle line numbers visibility"""
        if self.current_tab is not None and self.tabs:
            line_numbers = self.tabs[self.current_tab]['line_numbers']
            if self.show_line_numbers.get():
                line_numbers.pack(side=tk.LEFT, fill=tk.Y)
            else:
                line_numbers.pack_forget()
                
    def toggle_minimap(self):
        """Toggle minimap visibility"""
        # Implementation for minimap
        pass
        
    def show_search(self):
        """Show search panel"""
        self.search_frame.pack(fill=tk.X, before=self.notebook)
        self.search_entry.focus()
        
    def hide_search(self):
        """Hide search panel"""
        self.search_frame.pack_forget()
        
    def show_replace(self):
        """Show replace panel"""
        self.show_search()
        self.replace_entry.focus()
        
    def find_text(self):
        """Find text with enhanced search"""
        if self.current_tab is None or not self.tabs:
            return
            
        search_term = self.search_var.get()
        if not search_term:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        
        # Clear previous highlights
        text_widget.tag_remove('search_highlight', '1.0', tk.END)
        
        # Search options
        flags = 0
        if not self.case_sensitive.get():
            flags = re.IGNORECASE
            
        if self.regex_search.get():
            try:
                pattern = re.compile(search_term, flags)
            except re.error:
                messagebox.showerror("Error", "Invalid regex pattern")
                return
        else:
            pattern = re.compile(re.escape(search_term), flags)
            
        # Find all matches
        content = text_widget.get('1.0', tk.END)
        matches = list(pattern.finditer(content))
        
        if matches:
            self.search_results = matches
            self.current_search_index = 0
            self.highlight_search_results()
            self.go_to_search_result(0)
            self.update_status(f"Found {len(matches)} matches")
        else:
            self.update_status("No matches found")
            
    def highlight_search_results(self):
        """Highlight all search results"""
        if self.current_tab is None or not self.tabs:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        
        # Configure highlight tag
        text_widget.tag_configure('search_highlight', 
                                 background=self.colors['select_bg'],
                                 foreground=self.colors['select_fg'])
        
        # Highlight all matches
        for match in self.search_results:
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.tag_add('search_highlight', start, end)
            
    def go_to_search_result(self, index):
        """Go to specific search result"""
        if not self.search_results or index >= len(self.search_results):
            return
            
        if self.current_tab is None or not self.tabs:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        match = self.search_results[index]
        
        # Calculate position
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        
        # Select and scroll to match
        text_widget.tag_remove('search_selection', '1.0', tk.END)
        text_widget.tag_add('search_selection', start, end)
        text_widget.tag_configure('search_selection', 
                                 background=self.colors['bracket_bg'],
                                 foreground='black')
        text_widget.see(start)
        text_widget.mark_set(tk.INSERT, start)
        
    def find_next(self):
        """Find next search result"""
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.go_to_search_result(self.current_search_index)
            
    def find_previous(self):
        """Find previous search result"""
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.go_to_search_result(self.current_search_index)
            
    def replace_text(self):
        """Replace current search result"""
        if not self.search_results or self.current_search_index >= len(self.search_results):
            return
            
        if self.current_tab is None or not self.tabs:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        match = self.search_results[self.current_search_index]
        replace_text = self.replace_var.get()
        
        # Replace the text
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        text_widget.delete(start, end)
        text_widget.insert(start, replace_text)
        
        # Update search results
        self.find_text()
        
    def replace_all(self):
        """Replace all search results"""
        if not self.search_results:
            return
            
        if self.current_tab is None or not self.tabs:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        replace_text = self.replace_var.get()
        
        # Sort matches in reverse order to maintain positions
        sorted_matches = sorted(self.search_results, key=lambda x: x.start(), reverse=True)
        
        for match in sorted_matches:
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            text_widget.delete(start, end)
            text_widget.insert(start, replace_text)
            
        self.update_status(f"Replaced {len(self.search_results)} occurrences")
        self.search_results = []
        
    def detect_unity_project(self):
        """Detect Unity project in current directory"""
        current_dir = os.getcwd()
        
        # Look for Unity project files
        unity_indicators = ['Assets', 'ProjectSettings', 'Packages', 'Library']
        for indicator in unity_indicators:
            if os.path.exists(os.path.join(current_dir, indicator)):
                self.unity_project_path = current_dir
                self.update_status("Unity project detected!")
                return
                
        # Check parent directories
        parent_dir = os.path.dirname(current_dir)
        if parent_dir != current_dir:
            for indicator in unity_indicators:
                if os.path.exists(os.path.join(parent_dir, indicator)):
                    self.unity_project_path = parent_dir
                    self.update_status("Unity project detected in parent directory!")
                    return
                    
    def open_unity_project(self):
        """Open Unity project in Unity"""
        if self.unity_project_path and os.path.exists(self.unity_project_path):
            try:
                # Try to find Unity executable
                unity_paths = [
                    r"C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe",
                    r"C:\Program Files (x86)\Unity\Editor\Unity.exe",
                    "/Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity",
                    "/opt/unity/editor/Unity"
                ]
                
                for path_pattern in unity_paths:
                    import glob
                    matches = glob.glob(path_pattern)
                    if matches:
                        subprocess.Popen([matches[0], "-projectPath", self.unity_project_path])
                        self.update_status("Opening Unity project...")
                        return
                        
                # Fallback: try to open project folder
                if platform.system() == "Windows":
                    os.startfile(self.unity_project_path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", self.unity_project_path])
                else:
                    subprocess.run(["xdg-open", self.unity_project_path])
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not open Unity project: {str(e)}")
                
    def update_project_tree(self):
        """Update project explorer tree"""
        if not hasattr(self, 'project_tree'):
            return
            
        # Clear existing items
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
            
        # Add current directory
        current_dir = os.getcwd()
        if self.unity_project_path:
            current_dir = self.unity_project_path
            
        root_item = self.project_tree.insert('', 'end', text=os.path.basename(current_dir), 
                                           values=[current_dir], open=True)
        
        # Add files and folders
        self.add_directory_to_tree(root_item, current_dir)
        
    def add_directory_to_tree(self, parent, directory):
        """Add directory contents to tree"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                # Skip hidden files and system directories
                if item.startswith('.') or item in ['__pycache__', 'Library', 'Temp']:
                    continue
                    
                if os.path.isdir(item_path):
                    folder_item = self.project_tree.insert(parent, 'end', text=item, 
                                                         values=[item_path], open=False)
                    self.add_directory_to_tree(folder_item, item_path)
                else:
                    # Only add supported file types
                    if self.is_supported_file(item):
                        self.project_tree.insert(parent, 'end', text=item, values=[item_path])
        except PermissionError:
            pass
            
    def is_supported_file(self, filename):
        """Check if file type is supported"""
        supported_extensions = ['.py', '.cs', '.js', '.html', '.css', '.json', '.xml', 
                              '.txt', '.md', '.sh', '.bat', '.ps1', '.yml', '.yaml']
        return any(filename.lower().endswith(ext) for ext in supported_extensions)
        
    def on_tree_double_click(self, event):
        """Handle tree double click"""
        selection = self.project_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.project_tree.item(item, 'values')[0]
            if os.path.isfile(file_path):
                self.open_file_path(file_path)
                
    def on_tree_right_click(self, event):
        """Handle tree right click"""
        # Implementation for context menu
        pass
        
    def new_file(self):
        """Create new file"""
        self.create_new_tab()
        
    def open_file(self):
        """Open file dialog"""
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Files", "*.*"),
                ("Python Files", "*.py"),
                ("C# Files", "*.cs"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JSON Files", "*.json"),
                ("Text Files", "*.txt")
            ]
        )
        if file_path:
            self.open_file_path(file_path)
            
    def save_file(self):
        """Save current file"""
        if self.current_tab is None or not self.tabs:
            return
            
        tab = self.tabs[self.current_tab]
        
        if not tab['file_path']:
            return self.save_file_as()
            
        try:
            content = tab['text'].get('1.0', tk.END)
            with open(tab['file_path'], 'w', encoding=tab['encoding']) as f:
                f.write(content)
            tab['modified'] = False
            self.update_tab_title()
            self.update_status(f"Saved: {os.path.basename(tab['file_path'])}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            
    def save_file_as(self):
        """Save file as dialog"""
        if self.current_tab is None or not self.tabs:
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("All Files", "*.*"),
                ("Python Files", "*.py"),
                ("C# Files", "*.cs"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JSON Files", "*.json"),
                ("Text Files", "*.txt")
            ]
        )
        if file_path:
            tab = self.tabs[self.current_tab]
            tab['file_path'] = file_path
            self.save_file()
            
    def toggle_always_on_top(self):
        """Toggle always on top"""
        self.always_on_top.set(not self.always_on_top.get())
        self.root.attributes('-topmost', self.always_on_top.get())
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.fullscreen.set(not self.fullscreen.get())
        self.root.attributes('-fullscreen', self.fullscreen.get())
        
    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        self.root.bind('<Control-f>', lambda e: self.show_search())
        self.root.bind('<Control-h>', lambda e: self.show_replace())
        self.root.bind('<Control-g>', lambda e: self.go_to_line())
        self.root.bind('<F3>', lambda e: self.find_next())
        self.root.bind('<Shift-F3>', lambda e: self.find_previous())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        
    def go_to_line(self):
        """Go to line dialog"""
        # Implementation for go to line
        pass
        
    def select_all(self):
        """Select all text"""
        if self.current_tab is not None and self.tabs:
            self.tabs[self.current_tab]['text'].tag_add(tk.SEL, "1.0", tk.END)
            
    def undo(self):
        """Undo last action"""
        if self.current_tab is not None and self.tabs:
            try:
                self.tabs[self.current_tab]['text'].edit_undo()
            except tk.TclError:
                pass
                
    def redo(self):
        """Redo last action"""
        if self.current_tab is not None and self.tabs:
            try:
                self.tabs[self.current_tab]['text'].edit_redo()
            except tk.TclError:
                pass
                
    def on_text_change(self, event):
        """Handle text changes"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['modified'] = True
            self.update_tab_title()
            
            # Delayed syntax highlighting for performance
            if self.highlight_timer:
                self.root.after_cancel(self.highlight_timer)
            self.highlight_timer = self.root.after(300, self.highlight_syntax)
            
            # Auto-save
            self.schedule_autosave()
            
    def highlight_syntax(self):
        """Enhanced syntax highlighting"""
        if self.current_tab is None or not self.tabs:
            return
            
        tab = self.tabs[self.current_tab]
        text_widget = tab['text']
        
        # Determine syntax based on file extension
        if tab['file_path']:
            ext = os.path.splitext(tab['file_path'])[1].lower()
            syntax_map = {
                '.py': 'python',
                '.cs': 'csharp',
                '.js': 'javascript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.xml': 'xml',
                '.sh': 'bash',
                '.bat': 'batch',
                '.ps1': 'powershell'
            }
            syntax = syntax_map.get(ext, 'text')
        else:
            syntax = 'text'
            
        try:
            # Get lexer
            if syntax == 'csharp':
                lexer = CSharpLexer()
            elif syntax == 'python':
                lexer = PythonLexer()
            elif syntax == 'javascript':
                lexer = JavascriptLexer()
            elif syntax == 'html':
                lexer = HtmlLexer()
            elif syntax == 'css':
                lexer = CssLexer()
            elif syntax == 'json':
                lexer = JsonLexer()
            else:
                lexer = TextLexer()
                
            # Get content
            content = text_widget.get('1.0', tk.END)
            
            # Clear existing tags
            for tag in text_widget.tag_names():
                if tag != 'search_highlight' and tag != 'search_selection':
                    text_widget.tag_remove(tag, '1.0', tk.END)
                    
            # Apply syntax highlighting
            tokens = lexer.get_tokens(content)
            current_pos = '1.0'
            
            for token_type, value in tokens:
                if value:
                    end_pos = f"{current_pos}+{len(value)}c"
                    
                    # Configure tag based on token type
                    tag_name = str(token_type)
                    if tag_name not in text_widget.tag_names():
                        color = self.get_token_color(token_type)
                        text_widget.tag_configure(tag_name, foreground=color)
                        
                    text_widget.tag_add(tag_name, current_pos, end_pos)
                    current_pos = end_pos
                    
        except Exception as e:
            print(f"Syntax highlighting error: {e}")
            
    def get_token_color(self, token_type):
        """Get color for token type"""
        color_map = {
            Token.Keyword: '#569cd6',
            Token.Name: '#9cdcfe',
            Token.String: '#ce9178',
            Token.Comment: '#6a9955',
            Token.Number: '#b5cea8',
            Token.Operator: '#d4d4d4',
            Token.Punctuation: '#d4d4d4',
            Token.Literal: '#4ec9b0',
            Token.Error: '#f44747'
        }
        
        for token_class, color in color_map.items():
            if token_type in token_class:
                return color
        return self.colors['fg']
        
    def update_tab_title(self):
        """Update tab title with modification indicator"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            title = os.path.basename(tab['file_path']) if tab['file_path'] else f"Untitled {self.current_tab + 1}"
            if tab['modified']:
                title += " *"
            self.notebook.tab(self.current_tab, text=title)
            
    def update_line_numbers(self, event=None):
        """Update line numbers with enhanced performance"""
        if self.current_tab is None or not self.tabs:
            return
            
        tab = self.tabs[self.current_tab]
        text_widget = tab['text']
        line_numbers = tab['line_numbers']
        
        # Get current line and column
        index = text_widget.index(tk.INSERT)
        line, col = index.split('.')
        
        # Update position label
        self.position_label.config(text=f"Line {line}, Col {int(col) + 1}")
        
        # Update file size
        content = text_widget.get("1.0", tk.END)
        size_kb = len(content.encode('utf-8')) / 1024
        self.file_size_label.config(text=f"{size_kb:.1f} KB")
        
        # Update line numbers
        content = text_widget.get("1.0", tk.END)
        lines = content.count('\n')
        
        # Store current scroll position
        current_scroll = text_widget.yview()[0]
        
        line_numbers.config(state='normal')
        line_numbers.delete("1.0", tk.END)
        
        # Add line numbers with proper formatting
        for i in range(1, lines + 1):
            line_numbers.insert(tk.END, f"{i:4d}\n")
        line_numbers.config(state='disabled')
        
        # Force scroll sync
        try:
            line_numbers.yview_moveto(current_scroll)
        except Exception:
            pass
            
    def on_tab_changed(self, event):
        """Handle tab change"""
        if self.tabs:
            self.current_tab = self.notebook.index(self.notebook.select())
            self.update_status()
            self.update_line_numbers()
            self.highlight_syntax()
            
    def schedule_autosave(self):
        """Schedule auto-save"""
        if self.autosave_timer:
            self.root.after_cancel(self.autosave_timer)
        self.autosave_timer = self.root.after(30000, self.autosave)  # 30 seconds
        
    def autosave(self):
        """Auto-save current file"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            if tab['modified'] and tab['file_path']:
                self.save_file()
                
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        
    def load_session(self):
        """Load session data"""
        try:
            if os.path.exists(self.session_path):
                with open(self.session_path, 'r') as f:
                    data = json.load(f)
                    self.recent_files = data.get('recent_files', [])
                    # Load recent files as tabs
                    for file_path in self.recent_files[:5]:  # Load first 5 files
                        if os.path.exists(file_path):
                            self.create_new_tab(file_path)
        except Exception as e:
            print(f"Could not load session: {e}")
            
    def save_session(self):
        """Save session data"""
        try:
            data = {
                'recent_files': self.recent_files,
                'window_geometry': self.root.geometry()
            }
            with open(self.session_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Could not save session: {e}")
            
    def update_status(self, message=None):
        """Update status bar"""
        if message:
            self.file_info_label.config(text=message)
        elif self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            if tab['file_path']:
                self.file_info_label.config(text=f"Ready - {os.path.basename(tab['file_path'])}")
            else:
                self.file_info_label.config(text="Ready - Untitled")
        else:
            self.file_info_label.config(text="Ready")
            
    def on_app_close(self):
        """Handle application close"""
        self.save_session()
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        self.update_project_tree()
        self.root.mainloop()

if __name__ == "__main__":
    app = ProfessionalAnoraEditor()
    app.run()