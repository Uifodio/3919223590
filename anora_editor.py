#!/usr/bin/env python3
"""
ANORA EDITOR - Professional Code Editor for Unity
==================================================

A lightweight, fast, professional code editor designed specifically for Unity development.
Features dark theme, syntax highlighting, tab management, and always-on-top capability.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
from pathlib import Path
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter
import re
from datetime import datetime
import threading
import time

class AnoraEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Anora Editor - Professional Code Editor for Unity")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # Dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'text': '#d4d4d4',
            'selection': '#264f78',
            'current_line': '#33415e',
            'tabs': '#2d2d30',
            'buttons': '#3e3e42',
            'keywords': '#569cd6',
            'strings': '#ce9178',
            'comments': '#6a9955',
            'numbers': '#b5cea8',
            'functions': '#dcdcaa'
        }
        
        # Editor state
        self.tabs = []
        self.current_tab = None
        self.closed_tabs = []
        self.recent_files = []
        self.session_file = os.path.expanduser("~/.anora_editor_session.json")
        self.always_on_top = False
        self.fullscreen = False
        self.search_panel_visible = False
        self.search_matches = []
        self.current_match_index = -1
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        self.setup_styles()
        self.create_menu()
        self.create_toolbar()
        self.create_notebook()
        self.create_status_bar()
        self.create_search_panel()
        self.bind_shortcuts()
        
        # Load session
        self.load_session()
        
        # Create new tab on startup
        self.new_tab()
        
        # Start autosave thread
        self.autosave_thread = threading.Thread(target=self.autosave_loop, daemon=True)
        self.autosave_thread.start()

    def setup_styles(self):
        """Configure ttk styles for dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['tabs'],
                       foreground=self.colors['text'],
                       padding=[10, 5],
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['selection'])],
                 foreground=[('selected', self.colors['text'])])
        
        # Configure button style
        style.configure('Toolbar.TButton',
                       background=self.colors['buttons'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='flat',
                       padding=[5, 2])
        style.map('Toolbar.TButton',
                 background=[('active', self.colors['selection'])],
                 foreground=[('active', self.colors['text'])])

    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root, bg=self.colors['bg'], fg=self.colors['text'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.show_search_panel, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.show_replace_panel, accelerator="Ctrl+H")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Always on Top", command=self.toggle_always_on_top)
        view_menu.add_checkbutton(label="Fullscreen", command=self.toggle_fullscreen)
        
        # Window menu
        window_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="Window", menu=window_menu)
        window_menu.add_command(label="New Tab", command=self.new_tab, accelerator="Ctrl+T")
        window_menu.add_command(label="Close Tab", command=self.close_tab, accelerator="Ctrl+W")
        window_menu.add_command(label="Close Others", command=self.close_others)
        window_menu.add_command(label="Reopen Closed Tab", command=self.reopen_closed_tab, accelerator="Ctrl+Shift+T")
        
        # Navigate menu
        navigate_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="Navigate", menu=navigate_menu)
        navigate_menu.add_command(label="Go To Line", command=self.go_to_line, accelerator="Ctrl+G")

    def create_toolbar(self):
        """Create the toolbar with icon buttons"""
        toolbar = tk.Frame(self.root, bg=self.colors['bg'], height=30)
        toolbar.pack(fill='x', padx=2, pady=2)
        toolbar.pack_propagate(False)
        
        # Toolbar buttons with Unicode icons
        buttons = [
            ("📄", "New", self.new_tab),
            ("📂", "Open", self.open_file),
            ("💾", "Save", self.save_file),
            ("🔍", "Find", self.show_search_panel),
            ("🔄", "Replace", self.show_replace_panel),
            ("📌", "Pin", self.toggle_always_on_top),
            ("⛶", "Full", self.toggle_fullscreen)
        ]
        
        for icon, tooltip, command in buttons:
            btn = tk.Button(toolbar, text=icon, command=command,
                           bg=self.colors['buttons'], fg=self.colors['text'],
                           relief='flat', borderwidth=1, padx=5, pady=2,
                           font=('Arial', 10))
            btn.pack(side='left', padx=1)
            
            # Tooltip
            self.create_tooltip(btn, tooltip)

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, bg=self.colors['selection'], 
                           fg=self.colors['text'], relief='solid', borderwidth=1)
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)

    def create_notebook(self):
        """Create the tabbed notebook"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=2, pady=2)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg'], height=20)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                   bg=self.colors['bg'], fg=self.colors['text'])
        self.status_label.pack(side='left', padx=5)
        
        self.position_label = tk.Label(self.status_bar, text="Line 1, Col 1", 
                                     bg=self.colors['bg'], fg=self.colors['text'])
        self.position_label.pack(side='right', padx=5)

    def create_search_panel(self):
        """Create the search and replace panel"""
        self.search_frame = tk.Frame(self.root, bg=self.colors['bg'])
        
        # Find input
        tk.Label(self.search_frame, text="Find:", bg=self.colors['bg'], fg=self.colors['text']).pack(side='left', padx=5)
        self.find_entry = tk.Entry(self.search_frame, bg=self.colors['buttons'], fg=self.colors['text'])
        self.find_entry.pack(side='left', padx=5)
        self.find_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Replace input
        tk.Label(self.search_frame, text="Replace:", bg=self.colors['bg'], fg=self.colors['text']).pack(side='left', padx=5)
        self.replace_entry = tk.Entry(self.search_frame, bg=self.colors['buttons'], fg=self.colors['text'])
        self.replace_entry.pack(side='left', padx=5)
        
        # Buttons
        tk.Button(self.search_frame, text="Find", command=self.find_next, 
                 bg=self.colors['buttons'], fg=self.colors['text']).pack(side='left', padx=2)
        tk.Button(self.search_frame, text="Replace", command=self.replace_current, 
                 bg=self.colors['buttons'], fg=self.colors['text']).pack(side='left', padx=2)
        tk.Button(self.search_frame, text="Replace All", command=self.replace_all, 
                 bg=self.colors['buttons'], fg=self.colors['text']).pack(side='left', padx=2)
        tk.Button(self.search_frame, text="Next", command=self.find_next, 
                 bg=self.colors['buttons'], fg=self.colors['text']).pack(side='left', padx=2)
        tk.Button(self.search_frame, text="Prev", command=self.find_prev, 
                 bg=self.colors['buttons'], fg=self.colors['text']).pack(side='left', padx=2)
        tk.Button(self.search_frame, text="✕", command=self.hide_search_panel, 
                 bg=self.colors['buttons'], fg=self.colors['text']).pack(side='left', padx=2)

    def create_text_widget(self, parent):
        """Create a text widget with line numbers and syntax highlighting"""
        # Main frame
        frame = tk.Frame(parent, bg=self.colors['bg'])
        
        # Line numbers
        self.line_numbers = tk.Text(frame, width=4, padx=3, takefocus=0,
                                   border=0, background=self.colors['tabs'],
                                   foreground=self.colors['text'], state='disabled',
                                   font=('Consolas', 10))
        self.line_numbers.pack(side='left', fill='y')
        
        # Text widget
        text_widget = tk.Text(frame, wrap='none', undo=True,
                             bg=self.colors['bg'], fg=self.colors['text'],
                             insertbackground=self.colors['text'],
                             selectbackground=self.colors['selection'],
                             font=('Consolas', 10), padx=5, pady=5)
        text_widget.pack(side='right', fill='both', expand=True)
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
        v_scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = tk.Scrollbar(parent, orient='horizontal', command=text_widget.xview)
        h_scrollbar.pack(side='bottom', fill='x')
        text_widget.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        text_widget.bind('<KeyRelease>', lambda e: self.on_text_change(text_widget))
        text_widget.bind('<Button-1>', lambda e: self.update_line_numbers(text_widget))
        text_widget.bind('<Key>', lambda e: self.update_line_numbers(text_widget))
        text_widget.bind('<MouseWheel>', lambda e: self.update_line_numbers(text_widget))
        text_widget.bind('<Return>', lambda e: self.auto_indent(text_widget))
        text_widget.bind('<KeyPress>', lambda e: self.auto_close_brackets(text_widget, e))
        text_widget.bind('<Button-3>', lambda e: self.show_context_menu(text_widget, e))
        
        # Context menu
        self.context_menu = tk.Menu(text_widget, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        self.context_menu.add_command(label="Cut", command=lambda: self.cut())
        self.context_menu.add_command(label="Copy", command=lambda: self.copy())
        self.context_menu.add_command(label="Paste", command=lambda: self.paste())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=lambda: self.select_all())
        
        return frame, text_widget

    def new_tab(self, file_path=None):
        """Create a new tab"""
        frame, text_widget = self.create_text_widget(self.notebook)
        
        tab_info = {
            'frame': frame,
            'text_widget': text_widget,
            'file_path': file_path,
            'modified': False,
            'content': ''
        }
        
        self.tabs.append(tab_info)
        
        # Set tab title
        if file_path:
            title = os.path.basename(file_path)
            self.add_to_recent_files(file_path)
        else:
            title = "Untitled"
        
        self.notebook.add(frame, text=title)
        self.notebook.select(frame)
        self.current_tab = len(self.tabs) - 1
        
        # Load file content if provided
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', content)
                    tab_info['content'] = content
                    self.update_line_numbers(text_widget)
                    self.apply_syntax_highlighting(text_widget)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
        
        return tab_info

    def open_file(self):
        """Open a file"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All supported", "*.py *.cs *.js *.html *.css *.json *.txt *.c *.cpp *.h"),
                ("Python files", "*.py"),
                ("C# files", "*.cs"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("C files", "*.c *.cpp *.h"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.new_tab(file_path)

    def save_file(self):
        """Save the current file"""
        if self.current_tab is None:
            return
        
        tab_info = self.tabs[self.current_tab]
        
        if tab_info['file_path']:
            try:
                content = tab_info['text_widget'].get('1.0', tk.END)
                with open(tab_info['file_path'], 'w', encoding='utf-8') as f:
                    f.write(content)
                tab_info['modified'] = False
                tab_info['content'] = content
                self.update_tab_title(self.current_tab)
                self.status_label.config(text="File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as()

    def save_as(self):
        """Save file as"""
        if self.current_tab is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("All supported", "*.py *.cs *.js *.html *.css *.json *.txt *.c *.cpp *.h"),
                ("Python files", "*.py"),
                ("C# files", "*.cs"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("C files", "*.c *.cpp *.h"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            tab_info = self.tabs[self.current_tab]
            tab_info['file_path'] = file_path
            self.save_file()
            self.add_to_recent_files(file_path)

    def close_tab(self):
        """Close the current tab"""
        if self.current_tab is None or len(self.tabs) <= 1:
            return
        
        tab_info = self.tabs[self.current_tab]
        
        if tab_info['modified']:
            result = messagebox.askyesnocancel("Save Changes", 
                                             "Do you want to save changes before closing?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()
        
        # Store in closed tabs for reopening
        self.closed_tabs.append(tab_info)
        
        # Remove tab
        self.notebook.forget(self.current_tab)
        self.tabs.pop(self.current_tab)
        
        # Update current tab
        if self.tabs:
            self.current_tab = min(self.current_tab, len(self.tabs) - 1)
            self.notebook.select(self.current_tab)
        else:
            self.current_tab = None

    def close_others(self):
        """Close all tabs except the current one"""
        if self.current_tab is None:
            return
        
        current_tab_info = self.tabs[self.current_tab]
        
        # Close all other tabs
        for i in range(len(self.tabs) - 1, -1, -1):
            if i != self.current_tab:
                tab_info = self.tabs[i]
                if tab_info['modified']:
                    result = messagebox.askyesnocancel("Save Changes", 
                                                     f"Save changes to {tab_info.get('file_path', 'Untitled')}?")
                    if result is None:  # Cancel
                        return
                    elif result:  # Yes
                        self.save_file()
                
                self.closed_tabs.append(tab_info)
                self.notebook.forget(i)
                self.tabs.pop(i)
        
        self.current_tab = 0

    def reopen_closed_tab(self):
        """Reopen the last closed tab"""
        if not self.closed_tabs:
            return
        
        tab_info = self.closed_tabs.pop()
        self.new_tab(tab_info.get('file_path'))

    def show_search_panel(self):
        """Show the search panel"""
        if not self.search_panel_visible:
            self.search_frame.pack(fill='x', padx=2, pady=2)
            self.search_panel_visible = True
            self.find_entry.focus()

    def show_replace_panel(self):
        """Show the replace panel"""
        self.show_search_panel()
        self.replace_entry.focus()

    def hide_search_panel(self):
        """Hide the search panel"""
        if self.search_panel_visible:
            self.search_frame.pack_forget()
            self.search_panel_visible = False
            self.clear_search_highlights()

    def on_search_change(self, event=None):
        """Handle search input changes"""
        self.find_matches()
        self.highlight_matches()

    def find_matches(self):
        """Find all matches in the current text"""
        if self.current_tab is None:
            return
        
        search_text = self.find_entry.get()
        if not search_text:
            self.search_matches = []
            return
        
        text_widget = self.tabs[self.current_tab]['text_widget']
        content = text_widget.get('1.0', tk.END)
        
        self.search_matches = []
        start = '1.0'
        
        while True:
            pos = text_widget.search(search_text, start, tk.END)
            if not pos:
                break
            
            end = f"{pos}+{len(search_text)}c"
            self.search_matches.append((pos, end))
            start = end

    def highlight_matches(self):
        """Highlight all search matches"""
        if self.current_tab is None:
            return
        
        text_widget = self.tabs[self.current_tab]['text_widget']
        
        # Remove existing highlights
        text_widget.tag_remove('search_highlight', '1.0', tk.END)
        text_widget.tag_remove('current_match', '1.0', tk.END)
        
        # Configure tags
        text_widget.tag_configure('search_highlight', background='yellow')
        text_widget.tag_configure('current_match', background='green')
        
        # Apply highlights
        for i, (start, end) in enumerate(self.search_matches):
            if i == self.current_match_index:
                text_widget.tag_add('current_match', start, end)
            else:
                text_widget.tag_add('search_highlight', start, end)

    def find_next(self):
        """Find next match"""
        if not self.search_matches:
            self.find_matches()
        
        if self.search_matches:
            self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
            self.highlight_matches()
            self.goto_match()

    def find_prev(self):
        """Find previous match"""
        if not self.search_matches:
            self.find_matches()
        
        if self.search_matches:
            self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
            self.highlight_matches()
            self.goto_match()

    def goto_match(self):
        """Go to the current match"""
        if self.current_match_index >= 0 and self.current_match_index < len(self.search_matches):
            start, end = self.search_matches[self.current_match_index]
            text_widget = self.tabs[self.current_tab]['text_widget']
            text_widget.see(start)
            text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            text_widget.tag_add(tk.SEL, start, end)

    def replace_current(self):
        """Replace current match"""
        if self.current_match_index >= 0 and self.current_match_index < len(self.search_matches):
            start, end = self.search_matches[self.current_match_index]
            text_widget = self.tabs[self.current_tab]['text_widget']
            replace_text = self.replace_entry.get()
            
            text_widget.delete(start, end)
            text_widget.insert(start, replace_text)
            
            # Update matches
            self.find_matches()
            self.highlight_matches()

    def replace_all(self):
        """Replace all matches"""
        if not self.search_matches:
            return
        
        text_widget = self.tabs[self.current_tab]['text_widget']
        search_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        # Replace from end to beginning to maintain positions
        for start, end in reversed(self.search_matches):
            text_widget.delete(start, end)
            text_widget.insert(start, replace_text)
        
        # Update matches
        self.find_matches()
        self.highlight_matches()

    def clear_search_highlights(self):
        """Clear search highlights"""
        if self.current_tab is None:
            return
        
        text_widget = self.tabs[self.current_tab]['text_widget']
        text_widget.tag_remove('search_highlight', '1.0', tk.END)
        text_widget.tag_remove('current_match', '1.0', tk.END)

    def toggle_always_on_top(self):
        """Toggle always on top"""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        
        # Update menu and toolbar
        for i in range(self.root.winfo_children()):
            if isinstance(i, tk.Menu):
                for j in range(i.index('end')):
                    if i.entrycget(j, 'label') == 'Always on Top':
                        i.entryconfig(j, variable=tk.BooleanVar(value=self.always_on_top))

    def toggle_fullscreen(self):
        """Toggle fullscreen"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)

    def go_to_line(self):
        """Go to specific line"""
        if self.current_tab is None:
            return
        
        line_num = simpledialog.askinteger("Go To Line", "Enter line number:")
        if line_num:
            text_widget = self.tabs[self.current_tab]['text_widget']
            try:
                text_widget.see(f"{line_num}.0")
                text_widget.mark_set(tk.INSERT, f"{line_num}.0")
            except tk.TclError:
                pass

    def undo(self):
        """Undo last action"""
        if self.current_tab is not None:
            self.tabs[self.current_tab]['text_widget'].edit_undo()

    def redo(self):
        """Redo last action"""
        if self.current_tab is not None:
            self.tabs[self.current_tab]['text_widget'].edit_redo()

    def cut(self):
        """Cut selected text"""
        if self.current_tab is not None:
            self.tabs[self.current_tab]['text_widget'].event_generate("<<Cut>>")

    def copy(self):
        """Copy selected text"""
        if self.current_tab is not None:
            self.tabs[self.current_tab]['text_widget'].event_generate("<<Copy>>")

    def paste(self):
        """Paste text"""
        if self.current_tab is not None:
            self.tabs[self.current_tab]['text_widget'].event_generate("<<Paste>>")

    def select_all(self):
        """Select all text"""
        if self.current_tab is not None:
            self.tabs[self.current_tab]['text_widget'].tag_add(tk.SEL, '1.0', tk.END)

    def auto_indent(self, text_widget):
        """Auto-indent on Enter"""
        current_line = text_widget.get("insert linestart", "insert")
        leading_spaces = len(current_line) - len(current_line.lstrip())
        
        if leading_spaces > 0:
            text_widget.insert(tk.INSERT, '\n' + ' ' * leading_spaces)
            return 'break'

    def auto_close_brackets(self, text_widget, event):
        """Auto-close brackets and quotes"""
        char = event.char
        brackets = {'(': ')', '{': '}', '[': ']', '"': '"', "'": "'"}
        
        if char in brackets:
            text_widget.insert(tk.INSERT, brackets[char])
            text_widget.mark_set(tk.INSERT, f"insert-1c")

    def show_context_menu(self, text_widget, event):
        """Show context menu"""
        self.context_menu.post(event.x_root, event.y_root)

    def on_text_change(self, text_widget):
        """Handle text changes"""
        if self.current_tab is None:
            return
        
        tab_info = self.tabs[self.current_tab]
        current_content = text_widget.get('1.0', tk.END)
        
        if current_content != tab_info['content']:
            tab_info['modified'] = True
            self.update_tab_title(self.current_tab)
        
        self.update_position_label()
        self.apply_syntax_highlighting(text_widget)

    def update_tab_title(self, tab_index):
        """Update tab title with modification indicator"""
        if tab_index >= len(self.tabs):
            return
        
        tab_info = self.tabs[tab_index]
        title = tab_info.get('file_path', 'Untitled')
        
        if title == 'Untitled':
            display_title = title
        else:
            display_title = os.path.basename(title)
        
        if tab_info['modified']:
            display_title += " *"
        
        self.notebook.tab(tab_index, text=display_title)

    def update_line_numbers(self, text_widget):
        """Update line numbers"""
        content = text_widget.get('1.0', tk.END)
        lines = content.count('\n')
        
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')

    def update_position_label(self):
        """Update position label in status bar"""
        if self.current_tab is None:
            return
        
        text_widget = self.tabs[self.current_tab]['text_widget']
        pos = text_widget.index(tk.INSERT)
        line, col = pos.split('.')
        self.position_label.config(text=f"Line {line}, Col {int(col) + 1}")

    def apply_syntax_highlighting(self, text_widget):
        """Apply syntax highlighting"""
        if self.current_tab is None:
            return
        
        tab_info = self.tabs[self.current_tab]
        file_path = tab_info.get('file_path', '')
        
        # Determine language based on file extension
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            lang_map = {
                '.py': 'python',
                '.cs': 'csharp',
                '.js': 'javascript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.c': 'c',
                '.cpp': 'cpp',
                '.h': 'c'
            }
            language = lang_map.get(ext, 'text')
        else:
            language = 'text'
        
        try:
            lexer = get_lexer_by_name(language)
        except:
            lexer = TextLexer()
        
        # Get visible lines for performance
        first_visible = text_widget.index("@0,0")
        last_visible = text_widget.index("@0,1000")
        
        content = text_widget.get(first_visible, last_visible)
        
        # Remove existing tags
        for tag in text_widget.tag_names():
            if tag.startswith('syntax_'):
                text_widget.tag_remove(tag, first_visible, last_visible)
        
        # Apply highlighting
        try:
            tokens = lexer.get_tokens(content)
            current_pos = first_visible
            
            for token_type, token_value in tokens:
                if token_value:
                    end_pos = f"{current_pos}+{len(token_value)}c"
                    
                    # Create tag based on token type
                    tag_name = f"syntax_{token_type}"
                    if tag_name not in text_widget.tag_names():
                        color = self.get_token_color(token_type)
                        text_widget.tag_configure(tag_name, foreground=color)
                    
                    text_widget.tag_add(tag_name, current_pos, end_pos)
                    current_pos = end_pos
        except:
            pass

    def get_token_color(self, token_type):
        """Get color for token type"""
        if 'Keyword' in token_type:
            return self.colors['keywords']
        elif 'String' in token_type:
            return self.colors['strings']
        elif 'Comment' in token_type:
            return self.colors['comments']
        elif 'Number' in token_type:
            return self.colors['numbers']
        elif 'Function' in token_type or 'Name' in token_type:
            return self.colors['functions']
        else:
            return self.colors['text']

    def on_tab_changed(self, event):
        """Handle tab change"""
        current = self.notebook.select()
        for i, tab_info in enumerate(self.tabs):
            if tab_info['frame'] == self.notebook.select():
                self.current_tab = i
                break
        
        if self.current_tab is not None:
            text_widget = self.tabs[self.current_tab]['text_widget']
            self.update_line_numbers(text_widget)
            self.update_position_label()
            self.apply_syntax_highlighting(text_widget)

    def add_to_recent_files(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only last 10
        self.update_recent_menu()

    def update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.delete(0, tk.END)
        
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                self.recent_menu.add_command(
                    label=os.path.basename(file_path),
                    command=lambda fp=file_path: self.new_tab(fp)
                )

    def save_session(self):
        """Save current session"""
        session_data = {
            'tabs': [],
            'recent_files': self.recent_files,
            'always_on_top': self.always_on_top,
            'fullscreen': self.fullscreen
        }
        
        for tab_info in self.tabs:
            tab_data = {
                'file_path': tab_info.get('file_path'),
                'content': tab_info['text_widget'].get('1.0', tk.END),
                'modified': tab_info['modified']
            }
            session_data['tabs'].append(tab_data)
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
        except:
            pass

    def load_session(self):
        """Load saved session"""
        if not os.path.exists(self.session_file):
            return
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            self.recent_files = session_data.get('recent_files', [])
            self.always_on_top = session_data.get('always_on_top', False)
            self.fullscreen = session_data.get('fullscreen', False)
            
            # Restore tabs
            for tab_data in session_data.get('tabs', []):
                if tab_data.get('file_path') and os.path.exists(tab_data['file_path']):
                    self.new_tab(tab_data['file_path'])
                elif tab_data.get('content'):
                    tab_info = self.new_tab()
                    tab_info['text_widget'].delete('1.0', tk.END)
                    tab_info['text_widget'].insert('1.0', tab_data['content'])
                    tab_info['modified'] = tab_data.get('modified', False)
            
            self.update_recent_menu()
        except:
            pass

    def autosave_loop(self):
        """Autosave loop"""
        while True:
            time.sleep(0.5)  # 500ms
            self.save_session()

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_tab())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.show_search_panel())
        self.root.bind('<Control-h>', lambda e: self.show_replace_panel())
        self.root.bind('<Control-t>', lambda e: self.new_tab())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-Shift-T>', lambda e: self.reopen_closed_tab())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-g>', lambda e: self.go_to_line())
        self.root.bind('<F3>', lambda e: self.find_next())
        self.root.bind('<Shift-F3>', lambda e: self.find_prev())
        self.root.bind('<Control-q>', lambda e: self.quit_app())

    def quit_app(self):
        """Quit the application"""
        self.save_session()
        self.root.quit()

def main():
    """Main function"""
    root = tk.Tk()
    app = AnoraEditor(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    
    root.mainloop()

if __name__ == "__main__":
    main()