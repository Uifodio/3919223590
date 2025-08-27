import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont
import os
import sys
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.token import Token
from pygments.formatters import HtmlFormatter
import re
from typing import Dict, List, Optional
import threading
import time

class AnoraEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Anora Editor - Professional Code Editor for Unity")
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
        
        # Configure tags for syntax highlighting
        text_widget.tag_configure("keyword", foreground="#569cd6")
        text_widget.tag_configure("string", foreground="#ce9178")
        text_widget.tag_configure("comment", foreground="#6a9955")
        text_widget.tag_configure("number", foreground="#b5cea8")
        text_widget.tag_configure("function", foreground="#dcdcaa")
        
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

        # Editing helpers
        text_widget.bind('<Return>', self.handle_auto_indent)
        for ch in ['(', '{', '[', '"', "'"]:
            text_widget.bind(ch, self.handle_bracket_autoclose)
        
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
        # Drag and drop functionality will be implemented with native tkinter
        # For now, we'll use file dialogs for opening files
        pass
        
    def on_drop(self, event):
        # Placeholder for drag and drop functionality
        pass
                
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
                    '.xml': 'xml'
                }
                tab['syntax'] = syntax_map.get(ext, 'text')
            
            # Apply syntax highlighting
            content = text_widget.get("1.0", tk.END)
            try:
                lexer = get_lexer_by_name(tab['syntax'])
                tokens = list(lexer.get_tokens(content))

                # Clear existing tags
                for tag in ["keyword", "string", "comment", "number", "function"]:
                    text_widget.tag_remove(tag, "1.0", tk.END)

                # Pre-compute line start offsets for fast conversion
                # Exclude the very last trailing newline Pygments may append tokens for
                raw = content
                line_starts = [0]
                for i, ch in enumerate(raw):
                    if ch == '\n':
                        line_starts.append(i + 1)

                def offset_to_index(offset: int) -> str:
                    # Binary search for line
                    lo, hi = 0, len(line_starts) - 1
                    while lo <= hi:
                        mid = (lo + hi) // 2
                        if line_starts[mid] <= offset:
                            lo = mid + 1
                        else:
                            hi = mid - 1
                    line = hi
                    col = offset - line_starts[line]
                    # Tk indices are 1-based lines and 0-based columns
                    return f"{line + 1}.{col}"

                def should_tag(tt) -> Optional[str]:
                    # Map pygments token types to our tags
                    if tt in Token.Keyword or tt in Token.Name.Builtin:
                        return "keyword"
                    if tt in Token.String:
                        return "string"
                    if tt in Token.Comment:
                        return "comment"
                    if tt in Token.Literal.Number:
                        return "number"
                    if tt in Token.Name.Function:
                        return "function"
                    return None

                # Walk tokens and tag precise ranges
                offset = 0
                for tt, val in tokens:
                    length = len(val)
                    tag_name = should_tag(tt)
                    if tag_name and length > 0:
                        start_idx = offset_to_index(offset)
                        end_idx = offset_to_index(offset + length)
                        try:
                            text_widget.tag_add(tag_name, start_idx, end_idx)
                        except Exception:
                            pass
                    offset += length

            except Exception:
                pass  # Ignore highlighting errors

    def handle_auto_indent(self, event):
        if self.current_tab is None or not self.tabs:
            return
        tab = self.tabs[self.current_tab]
        text_widget = tab['text']
        # Get current line content
        current_index = text_widget.index(tk.INSERT)
        line_start = f"{current_index.split('.')[0]}.0"
        line_text = text_widget.get(line_start, current_index)
        leading_ws = re.match(r"^[ \t]*", line_text).group(0)

        # Insert newline + same indent
        text_widget.insert(tk.INSERT, "\n" + leading_ws)
        # Prevent default newline since we inserted our own
        return "break"

    def handle_bracket_autoclose(self, event):
        if self.current_tab is None or not self.tabs:
            return
        tab = self.tabs[self.current_tab]
        text_widget = tab['text']

        pairs = {
            '(': ')',
            '{': '}',
            '[': ']',
            '"': '"',
            "'": "'"
        }

        ch = event.char
        close_ch = pairs.get(ch)
        if not close_ch:
            return

        try:
            # If there is a selection, wrap it
            if text_widget.tag_ranges("sel"):
                sel_start = text_widget.index("sel.first")
                sel_end = text_widget.index("sel.last")
                text_widget.insert(sel_start, ch)
                text_widget.insert(sel_end + "+1c", close_ch)
                text_widget.mark_set(tk.INSERT, sel_end + "+1c")
            else:
                text_widget.insert(tk.INSERT, ch + close_ch)
                # Move cursor back between the pair
                text_widget.mark_set(tk.INSERT, text_widget.index(tk.INSERT + "-1c"))
        except Exception:
            pass

        return "break"
                
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
                text_widget.tag_config("search", background="yellow", foreground="black")
                
                if self.search_results:
                    self.current_search_index = 0
                    self.goto_search_result()
                    self.update_status(f"Found {len(self.search_results)} matches")
                else:
                    self.update_status("No matches found")
                    
    def goto_search_result(self):
        if self.search_results and self.current_tab is not None and self.tabs:
            tab = self.tabs[self.current_tab]
            text_widget = tab['text']
            
            # Remove previous selection
            text_widget.tag_remove("sel", "1.0", tk.END)
            
            # Select current result
            start, end = self.search_results[self.current_search_index]
            text_widget.tag_add("sel", start, end)
            text_widget.see(start)
            
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
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AnoraEditor()
    app.run()