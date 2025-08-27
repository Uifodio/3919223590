import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont
import os
import sys
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer, get_lexer_for_filename
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
import re
from typing import Dict, List, Optional
import threading
import time
import json
import pickle
from datetime import datetime

class NovaEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nova Editor - Professional Code Editor for Unity")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # Configure dark theme colors
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
            'entry_fg': '#cccccc'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Variables
        self.tabs = []
        self.current_tab = None
        self.always_on_top = tk.BooleanVar()
        self.fullscreen = tk.BooleanVar()
        self.search_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.search_results = []
        self.current_search_index = 0
        
        # Enhanced features
        self.undo_history = {}  # Tab-based undo history
        self.redo_history = {}  # Tab-based redo history
        self.recent_files = []
        self.settings = self.load_settings()
        self.file_associations = self.load_file_associations()
        
        # Drag and drop support
        self.drag_drop_enabled = True
        
        self.setup_ui()
        self.setup_bindings()
        self.setup_drag_drop()
        
    def setup_ui(self):
        # Menu bar
        self.create_menu()
        
        # Toolbar
        self.create_toolbar()
        
        # Search and replace panel
        self.create_search_panel()
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.create_status_bar()
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg'])
        style.configure('TNotebook.Tab', 
                       background=self.colors['tab_bg'],
                       foreground=self.colors['tab_fg'],
                       padding=[10, 5])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['tab_active_bg'])])
        
        # Create initial tab
        self.create_new_tab()
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.create_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.show_search, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.show_replace, accelerator="Ctrl+H")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Always on Top", variable=self.always_on_top, 
                                 command=self.toggle_always_on_top)
        view_menu.add_checkbutton(label="Fullscreen", variable=self.fullscreen, 
                                 command=self.toggle_fullscreen)
        
        # Window menu
        window_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        menubar.add_cascade(label="Window", menu=window_menu)
        window_menu.add_command(label="New Tab", command=self.create_new_tab, accelerator="Ctrl+T")
        window_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        window_menu.add_command(label="Close All Tabs", command=self.close_all_tabs)
        window_menu.add_separator()
        window_menu.add_command(label="Next Tab", command=self.next_tab, accelerator="Ctrl+Tab")
        window_menu.add_command(label="Previous Tab", command=self.previous_tab, accelerator="Ctrl+Shift+Tab")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        tools_menu.add_command(label="File Associations", command=self.show_file_associations)
        tools_menu.add_separator()
        tools_menu.add_command(label="Format Code", command=self.format_code)
        tools_menu.add_command(label="Comment/Uncomment", command=self.toggle_comment, accelerator="Ctrl+/")
        tools_menu.add_command(label="Duplicate Line", command=self.duplicate_line, accelerator="Ctrl+D")
        tools_menu.add_command(label="Delete Line", command=self.delete_line, accelerator="Ctrl+L")
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg=self.colors['bg'], height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        toolbar.pack_propagate(False)
        
        # New file button
        new_btn = tk.Button(toolbar, text="📄 New", command=self.create_new_tab,
                           bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                           relief=tk.FLAT, padx=10)
        new_btn.pack(side=tk.LEFT, padx=2)
        
        # Open file button
        open_btn = tk.Button(toolbar, text="📂 Open", command=self.open_file,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                            relief=tk.FLAT, padx=10)
        open_btn.pack(side=tk.LEFT, padx=2)
        
        # Save button
        save_btn = tk.Button(toolbar, text="💾 Save", command=self.save_file,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                            relief=tk.FLAT, padx=10)
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        tk.Frame(toolbar, bg=self.colors['tab_bg'], width=2).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Find button
        find_btn = tk.Button(toolbar, text="🔍 Find", command=self.show_search,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                            relief=tk.FLAT, padx=10)
        find_btn.pack(side=tk.LEFT, padx=2)
        
        # Replace button
        replace_btn = tk.Button(toolbar, text="🔄 Replace", command=self.show_replace,
                               bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                               relief=tk.FLAT, padx=10)
        replace_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        tk.Frame(toolbar, bg=self.colors['tab_bg'], width=2).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Always on top toggle
        self.top_btn = tk.Button(toolbar, text="📌 Pin", command=self.toggle_always_on_top,
                                bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                                relief=tk.FLAT, padx=10)
        self.top_btn.pack(side=tk.LEFT, padx=2)
        
        # Fullscreen toggle
        self.fullscreen_btn = tk.Button(toolbar, text="⛶ Full", command=self.toggle_fullscreen,
                                       bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                                       relief=tk.FLAT, padx=10)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=2)
        
    def create_search_panel(self):
        self.search_frame = tk.Frame(self.root, bg=self.colors['bg'], height=80)
        
        # Search entry
        search_label = tk.Label(self.search_frame, text="Find:", bg=self.colors['bg'], fg=self.colors['fg'])
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var,
                                    bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                                    width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Replace entry
        replace_label = tk.Label(self.search_frame, text="Replace:", bg=self.colors['bg'], fg=self.colors['fg'])
        replace_label.pack(side=tk.LEFT, padx=5)
        
        self.replace_entry = tk.Entry(self.search_frame, textvariable=self.replace_var,
                                     bg=self.colors['entry_bg'], fg=self.colors['entry_fg'],
                                     width=20)
        self.replace_entry.pack(side=tk.LEFT, padx=5)
        
        # Search buttons
        find_btn = tk.Button(self.search_frame, text="Find", command=self.find_text,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                            relief=tk.FLAT, padx=10)
        find_btn.pack(side=tk.LEFT, padx=2)
        
        replace_btn = tk.Button(self.search_frame, text="Replace", command=self.replace_text,
                               bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                               relief=tk.FLAT, padx=10)
        replace_btn.pack(side=tk.LEFT, padx=2)
        
        skip_btn = tk.Button(self.search_frame, text="Skip", command=self.skip_current,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                            relief=tk.FLAT, padx=10)
        skip_btn.pack(side=tk.LEFT, padx=2)
        
        replace_all_btn = tk.Button(self.search_frame, text="Replace All", command=self.replace_all,
                                   bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                                   relief=tk.FLAT, padx=10)
        replace_all_btn.pack(side=tk.LEFT, padx=2)
        
        close_btn = tk.Button(self.search_frame, text="✕", command=self.hide_search,
                             bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                             relief=tk.FLAT, padx=5)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Initially hidden
        self.search_frame.pack_forget()
        
    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=self.colors['tab_bg'], height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                    bg=self.colors['tab_bg'], fg=self.colors['tab_fg'])
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.position_label = tk.Label(self.status_bar, text="Line 1, Col 1", 
                                      bg=self.colors['tab_bg'], fg=self.colors['tab_fg'])
        self.position_label.pack(side=tk.RIGHT, padx=5)
        
    def create_new_tab(self, file_path=None):
        # Create tab frame
        tab_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        # Create text widget with line numbers
        text_frame = tk.Frame(tab_frame, bg=self.colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=3, takefocus=0,
                                   border=0, background=self.colors['tab_bg'],
                                   foreground=self.colors['tab_fg'],
                                   state='disabled', font=('Consolas', 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main text editor
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['insert_bg'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['select_fg'],
            font=('Consolas', 10),
            wrap=tk.NONE,
            undo=True
        )
        text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Configure tags for enhanced syntax highlighting
        text_widget.tag_configure("keyword", foreground="#569cd6", font=('Consolas', 10, 'bold'))
        text_widget.tag_configure("string", foreground="#ce9178", font=('Consolas', 10))
        text_widget.tag_configure("comment", foreground="#6a9955", font=('Consolas', 10, 'italic'))
        text_widget.tag_configure("number", foreground="#b5cea8", font=('Consolas', 10))
        text_widget.tag_configure("function", foreground="#dcdcaa", font=('Consolas', 10, 'bold'))
        text_widget.tag_configure("class", foreground="#4ec9b0", font=('Consolas', 10, 'bold'))
        text_widget.tag_configure("operator", foreground="#d4d4d4", font=('Consolas', 10))
        text_widget.tag_configure("variable", foreground="#9cdcfe", font=('Consolas', 10))
        text_widget.tag_configure("constant", foreground="#4fc1ff", font=('Consolas', 10))
        text_widget.tag_configure("type", foreground="#4ec9b0", font=('Consolas', 10))
        text_widget.tag_configure("decorator", foreground="#dcdcaa", font=('Consolas', 10))
        text_widget.tag_configure("error", foreground="#f44747", font=('Consolas', 10))
        text_widget.tag_configure("warning", foreground="#ffcc02", font=('Consolas', 10))
        
        # Search highlighting tags
        text_widget.tag_configure("search", background="#ffff00", foreground="#000000")
        text_widget.tag_configure("current_search", background="#00ff00", foreground="#000000")
        
        # Tab data
        tab_data = {
            'frame': tab_frame,
            'text': text_widget,
            'line_numbers': self.line_numbers,
            'file_path': file_path,
            'modified': False,
            'syntax': 'text'
        }
        
        # Add to notebook
        tab_title = os.path.basename(file_path) if file_path else f"Untitled {len(self.tabs) + 1}"
        self.notebook.add(tab_frame, text=tab_title)
        self.tabs.append(tab_data)
        
        # Set as current tab
        self.current_tab = len(self.tabs) - 1
        self.notebook.select(self.current_tab)
        
        # Bind events
        text_widget.bind('<KeyRelease>', self.on_text_change)
        text_widget.bind('<Button-1>', self.update_line_numbers)
        text_widget.bind('<Key>', self.update_line_numbers)
        text_widget.bind('<MouseWheel>', self.update_line_numbers)
        text_widget.bind('<Control-z>', self.undo)
        text_widget.bind('<Control-y>', self.redo)
        text_widget.bind('<Control-d>', self.duplicate_line)
        text_widget.bind('<Control-l>', self.delete_line)
        text_widget.bind('<Control-slash>', self.toggle_comment)
        text_widget.bind('<Control-Tab>', self.next_tab)
        text_widget.bind('<Control-Shift-Tab>', self.previous_tab)
        
        # Drag and drop bindings for text widget
        try:
            text_widget.drop_target_register('DND_Files')
            text_widget.dnd_bind('<<Drop>>', self.on_text_drop)
        except:
            # Drag and drop not available
            pass
        
        # Load file if provided
        if file_path:
            self.load_file(file_path)
            
        return tab_data
        
    def setup_bindings(self):
        # Global bindings
        self.root.bind('<Control-n>', lambda e: self.create_new_tab())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.show_search())
        self.root.bind('<Control-h>', lambda e: self.show_replace())
        self.root.bind('<Control-t>', lambda e: self.create_new_tab())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        
        # Tab change binding
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
    def setup_drag_drop(self):
        # Enable drag and drop for the main window
        self.drag_drop_enabled = True
        try:
            # Try to use tkinterdnd2 if available
            self.root.drop_target_register('DND_Files')
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        except:
            # Fallback to native Windows drag and drop
            try:
                import win32com.client
                self.setup_windows_drag_drop()
            except:
                # If all else fails, disable drag and drop
                self.drag_drop_enabled = False
                print("Drag and drop not available")
                
    def setup_windows_drag_drop(self):
        """Setup Windows native drag and drop"""
        try:
            # Bind to the main window
            self.root.bind('<Button-1>', self.on_drag_start)
            self.root.bind('<B1-Motion>', self.on_drag_motion)
            self.root.bind('<ButtonRelease-1>', self.on_drag_release)
        except:
            pass
        
    def on_drop(self, event):
        """Handle file drops on the editor"""
        if not self.drag_drop_enabled:
            return
            
        try:
            files = event.data
            if isinstance(files, str):
                files = [files]
            
            for file_path in files:
                if os.path.isfile(file_path):
                    # Check if file is already open
                    existing_tab = self.find_tab_by_path(file_path)
                    if existing_tab is not None:
                        # Switch to existing tab
                        self.notebook.select(existing_tab)
                    else:
                        # Create new tab
                        self.create_new_tab(file_path)
        except Exception as e:
            print(f"Drop error: {e}")
            
    def on_drag_start(self, event):
        """Handle drag start"""
        pass
        
    def on_drag_motion(self, event):
        """Handle drag motion"""
        pass
        
    def on_drag_release(self, event):
        """Handle drag release"""
        pass
        
    def on_text_drop(self, event):
        """Handle drops on text widget"""
        try:
            # Get the dropped data
            data = event.data
            if data:
                # Handle file paths
                if isinstance(data, str):
                    files = [data]
                else:
                    files = data
                
                for file_path in files:
                    if os.path.isfile(file_path):
                        # Check if file is already open
                        existing_tab = self.find_tab_by_path(file_path)
                        if existing_tab is not None:
                            # Switch to existing tab
                            self.notebook.select(existing_tab)
                        else:
                            # Create new tab
                            self.create_new_tab(file_path)
        except Exception as e:
            print(f"Text drop error: {e}")
                    
    def find_tab_by_path(self, file_path):
        """Find tab index by file path"""
        for i, tab in enumerate(self.tabs):
            if tab['file_path'] == file_path:
                return i
        return None
                
    def on_tab_changed(self, event):
        if self.tabs:
            self.current_tab = self.notebook.index(self.notebook.select())
            self.update_status()
            
    def on_text_change(self, event):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['modified'] = True
            self.update_tab_title()
            self.highlight_syntax()
            
    def update_tab_title(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            title = os.path.basename(tab['file_path']) if tab['file_path'] else f"Untitled {self.current_tab + 1}"
            if tab['modified']:
                title += " *"
            self.notebook.tab(self.current_tab, text=title)
            
    def update_line_numbers(self, event=None):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            line_numbers = tab['line_numbers']
            
            # Get current line and column
            index = text_widget.index(tk.INSERT)
            line, col = index.split('.')
            
            # Update position label
            self.position_label.config(text=f"Line {line}, Col {int(col) + 1}")
            
            # Update line numbers
            content = text_widget.get("1.0", tk.END)
            lines = content.count('\n')
            
            line_numbers.config(state='normal')
            line_numbers.delete("1.0", tk.END)
            for i in range(1, lines + 1):
                line_numbers.insert(tk.END, f"{i}\n")
            line_numbers.config(state='disabled')
            
    def highlight_syntax(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            
            # Determine syntax based on file extension
            if tab['file_path']:
                try:
                    lexer = get_lexer_for_filename(tab['file_path'])
                    tab['syntax'] = lexer.name
                except:
                    ext = os.path.splitext(tab['file_path'])[1].lower()
                    syntax_map = {
                        '.py': 'python',
                        '.js': 'javascript',
                        '.cs': 'csharp',
                        '.cpp': 'cpp',
                        '.c': 'c',
                        '.h': 'cpp',
                        '.html': 'html',
                        '.css': 'css',
                        '.json': 'json',
                        '.xml': 'xml',
                        '.sh': 'bash',
                        '.bat': 'batch',
                        '.ps1': 'powershell',
                        '.php': 'php',
                        '.rb': 'ruby',
                        '.java': 'java',
                        '.kt': 'kotlin',
                        '.swift': 'swift',
                        '.go': 'go',
                        '.rs': 'rust',
                        '.sql': 'sql',
                        '.md': 'markdown',
                        '.yml': 'yaml',
                        '.yaml': 'yaml',
                        '.toml': 'toml',
                        '.ini': 'ini',
                        '.cfg': 'ini',
                        '.conf': 'ini'
                    }
                    tab['syntax'] = syntax_map.get(ext, 'text')
            
            # Always use simple syntax highlighting that works
            self.simple_highlight_syntax(tab, text_widget)
                
    def simple_highlight_syntax(self, tab, text_widget):
        """Simple syntax highlighting as fallback"""
        try:
            content = text_widget.get("1.0", tk.END)
            syntax = tab.get('syntax', 'text')
            
            # Simple keyword highlighting for common languages
            if syntax == 'python':
                keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global', 'nonlocal']
                
                # Highlight keywords
                for keyword in keywords:
                    start = "1.0"
                    while True:
                        pos = text_widget.search(keyword, start, tk.END)
                        if not pos:
                            break
                        end = f"{pos}+{len(keyword)}c"
                        text_widget.tag_add("keyword", pos, end)
                        start = end
                
                # Highlight strings
                start = "1.0"
                while True:
                    pos = text_widget.search('"', start, tk.END)
                    if not pos:
                        break
                    # Find the end quote
                    end_pos = text_widget.search('"', f"{pos}+1c", tk.END)
                    if end_pos:
                        end = f"{end_pos}+1c"
                        text_widget.tag_add("string", pos, end)
                        start = end
                    else:
                        start = f"{pos}+1c"
                
                # Highlight comments
                start = "1.0"
                while True:
                    pos = text_widget.search('#', start, tk.END)
                    if not pos:
                        break
                    # Find end of line
                    line_end = text_widget.index(f"{pos} lineend")
                    text_widget.tag_add("comment", pos, line_end)
                    start = line_end
                    
            elif syntax == 'csharp':
                keywords = ['public', 'private', 'protected', 'internal', 'class', 'struct', 'interface', 'enum', 'namespace', 'using', 'static', 'readonly', 'const', 'virtual', 'override', 'abstract', 'sealed', 'partial', 'async', 'await', 'var', 'void', 'int', 'string', 'bool', 'float', 'double', 'if', 'else', 'for', 'while', 'foreach', 'switch', 'case', 'default', 'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally', 'new', 'this', 'base', 'null', 'true', 'false']
                
                # Highlight keywords
                for keyword in keywords:
                    start = "1.0"
                    while True:
                        pos = text_widget.search(keyword, start, tk.END)
                        if not pos:
                            break
                        end = f"{pos}+{len(keyword)}c"
                        text_widget.tag_add("keyword", pos, end)
                        start = end
                
                # Highlight strings
                start = "1.0"
                while True:
                    pos = text_widget.search('"', start, tk.END)
                    if not pos:
                        break
                    end_pos = text_widget.search('"', f"{pos}+1c", tk.END)
                    if end_pos:
                        end = f"{end_pos}+1c"
                        text_widget.tag_add("string", pos, end)
                        start = end
                    else:
                        start = f"{pos}+1c"
                
                # Highlight comments
                start = "1.0"
                while True:
                    pos = text_widget.search('//', start, tk.END)
                    if not pos:
                        break
                    line_end = text_widget.index(f"{pos} lineend")
                    text_widget.tag_add("comment", pos, line_end)
                    start = line_end
                    
            elif syntax == 'javascript':
                keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'null', 'undefined', 'true', 'false', 'class', 'extends', 'super', 'import', 'export', 'async', 'await']
                
                # Highlight keywords
                for keyword in keywords:
                    start = "1.0"
                    while True:
                        pos = text_widget.search(keyword, start, tk.END)
                        if not pos:
                            break
                        end = f"{pos}+{len(keyword)}c"
                        text_widget.tag_add("keyword", pos, end)
                        start = end
                
                # Highlight strings
                start = "1.0"
                while True:
                    pos = text_widget.search('"', start, tk.END)
                    if not pos:
                        break
                    end_pos = text_widget.search('"', f"{pos}+1c", tk.END)
                    if end_pos:
                        end = f"{end_pos}+1c"
                        text_widget.tag_add("string", pos, end)
                        start = end
                    else:
                        start = f"{pos}+1c"
                
                # Highlight comments
                start = "1.0"
                while True:
                    pos = text_widget.search('//', start, tk.END)
                    if not pos:
                        break
                    line_end = text_widget.index(f"{pos} lineend")
                    text_widget.tag_add("comment", pos, line_end)
                    start = line_end
                    
        except Exception as e:
            print(f"Simple highlighting error: {e}")
            pass
                
    def get_tag_for_token(self, token_type):
        """Get the appropriate tag for a token type"""
        if token_type in ['Keyword', 'Name.Builtin']:
            return "keyword"
        elif token_type in ['String', 'String.Single', 'String.Double', 'String.Triple']:
            return "string"
        elif token_type in ['Comment', 'Comment.Single', 'Comment.Multiline']:
            return "comment"
        elif token_type in ['Literal.Number', 'Literal.Number.Integer', 'Literal.Number.Float']:
            return "number"
        elif token_type in ['Name.Function', 'Name.Function.Magic']:
            return "function"
        elif token_type in ['Name.Class']:
            return "class"
        elif token_type in ['Operator', 'Punctuation']:
            return "operator"
        elif token_type in ['Name.Variable', 'Name.Variable.Instance']:
            return "variable"
        elif token_type in ['Name.Constant']:
            return "constant"
        elif token_type in ['Name.Builtin.Type', 'Name.Type']:
            return "type"
        elif token_type in ['Name.Decorator']:
            return "decorator"
        elif token_type in ['Generic.Error']:
            return "error"
        elif token_type in ['Generic.Warning']:
            return "warning"
        else:
            return "normal"
                
    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Files", "*.*"),
                ("Python Files", "*.py"),
                ("C# Files", "*.cs"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("JSON Files", "*.json")
            ]
        )
        if file_path:
            self.create_new_tab(file_path)
            
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            if self.current_tab is not None and self.tabs:
                tab = self.tabs[self.current_tab]
                tab['text'].delete("1.0", tk.END)
                tab['text'].insert("1.0", content)
                tab['modified'] = False
                tab['file_path'] = file_path
                self.update_tab_title()
                self.highlight_syntax()
                self.update_status(f"Loaded {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
            
    def save_file(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            if tab['file_path']:
                self.save_to_file(tab['file_path'])
            else:
                self.save_file_as()
                
    def save_file_as(self):
        if self.current_tab is not None and self.tabs:
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
                    ("JSON Files", "*.json")
                ]
            )
            if file_path:
                tab = self.tabs[self.current_tab]
                tab['file_path'] = file_path
                self.save_to_file(file_path)
                
    def save_to_file(self, file_path):
        try:
            if self.current_tab is not None and self.tabs:
                tab = self.tabs[self.current_tab]
                content = tab['text'].get("1.0", tk.END)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
                tab['modified'] = False
                self.update_tab_title()
                self.update_status(f"Saved {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            
    def close_current_tab(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            if tab['modified']:
                result = messagebox.askyesnocancel("Save Changes", 
                                                 "Do you want to save changes before closing?")
                if result is None:  # Cancel
                    return
                elif result:  # Yes
                    self.save_file()
                    
            self.notebook.forget(self.current_tab)
            self.tabs.pop(self.current_tab)
            
            if self.tabs:
                self.current_tab = min(self.current_tab, len(self.tabs) - 1)
                self.notebook.select(self.current_tab)
            else:
                self.create_new_tab()
                
    def close_all_tabs(self):
        """Close all tabs with save prompts"""
        if not self.tabs:
            return
            
        # Check for modified tabs
        modified_tabs = []
        for i, tab in enumerate(self.tabs):
            if tab['modified']:
                modified_tabs.append(i)
        
        if modified_tabs:
            result = messagebox.askyesnocancel("Save Changes", 
                                             f"Do you want to save changes to {len(modified_tabs)} modified file(s)?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                for i in modified_tabs:
                    self.current_tab = i
                    self.notebook.select(i)
                    self.save_file()
        
        # Close all tabs
        for _ in range(len(self.tabs)):
            self.notebook.forget(0)
        self.tabs.clear()
        self.current_tab = None
        
        # Create new tab
        self.create_new_tab()
        
    def next_tab(self, event=None):
        """Switch to next tab"""
        if self.tabs and len(self.tabs) > 1:
            next_index = (self.current_tab + 1) % len(self.tabs)
            self.notebook.select(next_index)
            self.current_tab = next_index
            
    def previous_tab(self, event=None):
        """Switch to previous tab"""
        if self.tabs and len(self.tabs) > 1:
            prev_index = (self.current_tab - 1) % len(self.tabs)
            self.notebook.select(prev_index)
            self.current_tab = prev_index
                
    def show_search(self):
        self.search_frame.pack(fill=tk.X, padx=5, pady=2)
        self.search_entry.focus()
        
    def show_replace(self):
        self.search_frame.pack(fill=tk.X, padx=5, pady=2)
        self.replace_entry.focus()
        
    def hide_search(self):
        self.search_frame.pack_forget()
        
    def find_text(self):
        if self.current_tab is not None and self.tabs:
            search_term = self.search_var.get()
            if search_term:
                tab = self.tabs[self.current_tab]
                text_widget = tab['text']
                
                # Clear previous highlights
                text_widget.tag_remove("search", "1.0", tk.END)
                text_widget.tag_remove("current_search", "1.0", tk.END)
                
                # Find all occurrences
                self.search_results = []
                start = "1.0"
                while True:
                    pos = text_widget.search(search_term, start, tk.END)
                    if not pos:
                        break
                    end = f"{pos}+{len(search_term)}c"
                    self.search_results.append((pos, end))
                    text_widget.tag_add("search", pos, end)
                    start = end
                    
                # Highlight search results
                text_widget.tag_config("search", background="#ffff00", foreground="#000000")
                
                if self.search_results:
                    self.current_search_index = 0
                    self.goto_search_result()
                    self.update_status(f"Found {len(self.search_results)} matches (1 of {len(self.search_results)})")
                else:
                    self.update_status("No matches found")
                    
    def goto_search_result(self):
        if self.search_results and self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            
            # Remove previous selection and current search highlight
            text_widget.tag_remove("sel", "1.0", tk.END)
            text_widget.tag_remove("current_search", "1.0", tk.END)
            
            # Select and highlight current result
            start, end = self.search_results[self.current_search_index]
            text_widget.tag_add("sel", start, end)
            text_widget.tag_add("current_search", start, end)
            text_widget.see(start)
            
            # Update status
            self.update_status(f"Match {self.current_search_index + 1} of {len(self.search_results)}")
            
    def replace_text(self):
        if self.current_tab is not None and self.tabs and self.search_results:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            replace_term = self.replace_var.get()
            
            # Replace current selection
            if text_widget.tag_ranges("sel"):
                text_widget.delete("sel.first", "sel.last")
                text_widget.insert("insert", replace_term)
                
            # Move to next result
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.goto_search_result()
            
    def skip_current(self):
        """Skip current search result and go to next"""
        if self.search_results and self.current_tab is not None and self.tabs:
            # Move to next result without replacing
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.goto_search_result()
            
    def replace_all(self):
        if self.current_tab is not None and self.tabs:
            search_term = self.search_var.get()
            replace_term = self.replace_var.get()
            
            if search_term:
                tab = self.tabs[self.current_tab]
                text_widget = tab['text']
                content = text_widget.get("1.0", tk.END)
                
                # Count replacements
                count = content.count(search_term)
                
                # Perform replacement
                new_content = content.replace(search_term, replace_term)
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", new_content)
                
                self.update_status(f"Replaced {count} occurrences")
                
    def select_all(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['text'].tag_add("sel", "1.0", tk.END)
            
    def undo(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['text'].edit_undo()
            
    def redo(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['text'].edit_redo()
            
    def cut(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['text'].event_generate("<<Cut>>")
            
    def copy(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['text'].event_generate("<<Copy>>")
            
    def paste(self):
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            tab['text'].event_generate("<<Paste>>")
            
    def toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())
        if self.always_on_top.get():
            self.top_btn.config(bg='#4CAF50', fg='white')
        else:
            self.top_btn.config(bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            
    def toggle_fullscreen(self):
        self.root.attributes('-fullscreen', self.fullscreen.get())
        if self.fullscreen.get():
            self.fullscreen_btn.config(bg='#4CAF50', fg='white')
        else:
            self.fullscreen_btn.config(bg=self.colors['button_bg'], fg=self.colors['button_fg'])
            
    def update_status(self, message="Ready"):
        self.status_label.config(text=message)
        
    def duplicate_line(self, event=None):
        """Duplicate the current line"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            
            # Get current line
            current_line = text_widget.index(tk.INSERT).split('.')[0]
            line_start = f"{current_line}.0"
            line_end = f"{int(current_line) + 1}.0"
            
            # Get line content
            line_content = text_widget.get(line_start, line_end)
            
            # Insert duplicate
            text_widget.insert(line_end, line_content)
            
    def delete_line(self, event=None):
        """Delete the current line"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            
            # Get current line
            current_line = text_widget.index(tk.INSERT).split('.')[0]
            line_start = f"{current_line}.0"
            line_end = f"{int(current_line) + 1}.0"
            
            # Delete line
            text_widget.delete(line_start, line_end)
            
    def toggle_comment(self, event=None):
        """Toggle comment for current line or selection"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            
            # Get syntax for comment style
            syntax = tab.get('syntax', 'text')
            comment_chars = {
                'python': '#',
                'csharp': '//',
                'javascript': '//',
                'cpp': '//',
                'c': '//',
                'java': '//',
                'php': '//',
                'ruby': '#',
                'go': '//',
                'rust': '//',
                'swift': '//',
                'kotlin': '//',
                'sql': '--',
                'bash': '#',
                'powershell': '#',
                'batch': 'REM ',
                'html': '<!--',
                'xml': '<!--'
            }
            
            comment_char = comment_chars.get(syntax, '#')
            
            # Get selection or current line
            try:
                sel_start = text_widget.index("sel.first")
                sel_end = text_widget.index("sel.last")
                has_selection = True
            except tk.TclError:
                # No selection, use current line
                current_line = text_widget.index(tk.INSERT).split('.')[0]
                sel_start = f"{current_line}.0"
                sel_end = f"{int(current_line) + 1}.0"
                has_selection = False
            
            # Get selected text
            selected_text = text_widget.get(sel_start, sel_end)
            
            # Check if already commented
            lines = selected_text.split('\n')
            all_commented = all(line.strip().startswith(comment_char) for line in lines if line.strip())
            
            if all_commented:
                # Uncomment
                new_lines = []
                for line in lines:
                    if line.strip().startswith(comment_char):
                        new_lines.append(line.replace(comment_char, '', 1))
                    else:
                        new_lines.append(line)
                new_text = '\n'.join(new_lines)
            else:
                # Comment
                new_lines = []
                for line in lines:
                    if line.strip() and not line.strip().startswith(comment_char):
                        new_lines.append(comment_char + ' ' + line)
                    else:
                        new_lines.append(line)
                new_text = '\n'.join(new_lines)
            
            # Replace text
            text_widget.delete(sel_start, sel_end)
            text_widget.insert(sel_start, new_text)
            
    def format_code(self):
        """Format the current code"""
        if self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            syntax = tab.get('syntax', 'text')
            
            # Get current content
            content = text_widget.get("1.0", tk.END)
            
            # Basic formatting for different languages
            if syntax == 'python':
                # Basic Python formatting
                lines = content.split('\n')
                formatted_lines = []
                indent_level = 0
                
                for line in lines:
                    stripped = line.strip()
                    if stripped:
                        # Adjust indent level
                        if stripped.endswith(':'):
                            formatted_lines.append('    ' * indent_level + stripped)
                            indent_level += 1
                        elif stripped.startswith(('return', 'break', 'continue', 'pass')):
                            indent_level = max(0, indent_level - 1)
                            formatted_lines.append('    ' * indent_level + stripped)
                        else:
                            formatted_lines.append('    ' * indent_level + stripped)
                    else:
                        formatted_lines.append('')
                
                formatted_content = '\n'.join(formatted_lines)
                
            elif syntax in ['csharp', 'javascript', 'cpp', 'java']:
                # Basic C-style formatting
                lines = content.split('\n')
                formatted_lines = []
                indent_level = 0
                
                for line in lines:
                    stripped = line.strip()
                    if stripped:
                        if stripped.endswith('{'):
                            formatted_lines.append('    ' * indent_level + stripped)
                            indent_level += 1
                        elif stripped.startswith('}'):
                            indent_level = max(0, indent_level - 1)
                            formatted_lines.append('    ' * indent_level + stripped)
                        else:
                            formatted_lines.append('    ' * indent_level + stripped)
                    else:
                        formatted_lines.append('')
                
                formatted_content = '\n'.join(formatted_lines)
                
            else:
                # Default formatting - just clean up whitespace
                lines = content.split('\n')
                formatted_lines = []
                for line in lines:
                    if line.strip():
                        formatted_lines.append(line.rstrip())
                    else:
                        formatted_lines.append('')
                formatted_content = '\n'.join(formatted_lines)
            
            # Replace content
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", formatted_content)
            self.update_status("Code formatted")
            
    def load_settings(self):
        """Load editor settings"""
        default_settings = {
            'theme': 'dark',
            'font_size': 10,
            'font_family': 'Consolas',
            'tab_size': 4,
            'auto_save': False,
            'word_wrap': False,
            'line_numbers': True,
            'syntax_highlighting': True,
            'auto_indent': True
        }
        
        try:
            with open('anora_settings.json', 'r') as f:
                settings = json.load(f)
                return {**default_settings, **settings}
        except:
            return default_settings
            
    def save_settings(self):
        """Save editor settings"""
        try:
            with open('anora_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
            
    def load_file_associations(self):
        """Load file associations"""
        default_associations = {
            '.py': 'python',
            '.js': 'javascript',
            '.cs': 'csharp',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'cpp',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml'
        }
        
        try:
            with open('file_associations.json', 'r') as f:
                associations = json.load(f)
                return {**default_associations, **associations}
        except:
            return default_associations
            
    def show_settings(self):
        """Show settings dialog"""
        # Placeholder for settings dialog
        messagebox.showinfo("Settings", "Settings dialog will be implemented in the next version!")
        
    def show_file_associations(self):
        """Show file associations dialog"""
        # Placeholder for file associations dialog
        messagebox.showinfo("File Associations", "File associations dialog will be implemented in the next version!")
        
    def run(self):
        # Handle command line arguments for opening files
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                # Check if file is already open
                existing_tab = self.find_tab_by_path(file_path)
                if existing_tab is not None:
                    # Switch to existing tab
                    self.notebook.select(existing_tab)
                else:
                    # Create new tab
                    self.create_new_tab(file_path)
        
        self.root.mainloop()

if __name__ == "__main__":
    app = NovaEditor()
    app.run()