#!/usr/bin/env python3
"""
Anora Code Editor - Professional Unity Development Editor
Advanced version with animations, professional UI, and smooth interactions
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
import math

# Import Pygments for syntax highlighting
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter
    from pygments.styles import get_style_by_name
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False
    print("Pygments not available - syntax highlighting disabled")

class AnimatedWidget:
    """Base class for animated widgets"""
    
    def __init__(self, widget, duration=300):
        self.widget = widget
        self.duration = duration
        self.animation_thread = None
        self.is_animating = False
        
    def animate_opacity(self, start_opacity, end_opacity, callback=None):
        """Animate widget opacity"""
        if self.is_animating:
            return
            
        self.is_animating = True
        steps = 30
        step_delay = self.duration / steps
        opacity_step = (end_opacity - start_opacity) / steps
        
        def animation_worker():
            current_opacity = start_opacity
            for i in range(steps):
                if not self.is_animating:
                    break
                current_opacity += opacity_step
                self.widget.attributes('-alpha', max(0.0, min(1.0, current_opacity)))
                time.sleep(step_delay / 1000)
            
            if callback:
                callback()
            self.is_animating = False
            
        self.animation_thread = threading.Thread(target=animation_worker, daemon=True)
        self.animation_thread.start()
        
    def animate_position(self, start_x, start_y, end_x, end_y, callback=None):
        """Animate widget position"""
        if self.is_animating:
            return
            
        self.is_animating = True
        steps = 30
        step_delay = self.duration / steps
        x_step = (end_x - start_x) / steps
        y_step = (end_y - start_y) / steps
        
        def animation_worker():
            current_x, current_y = start_x, start_y
            for i in range(steps):
                if not self.is_animating:
                    break
                current_x += x_step
                current_y += y_step
                self.widget.geometry(f"+{int(current_x)}+{int(current_y)}")
                time.sleep(step_delay / 1000)
            
            if callback:
                callback()
            self.is_animating = False
            
        self.animation_thread = threading.Thread(target=animation_worker, daemon=True)
        self.animation_thread.start()
        
    def stop_animation(self):
        """Stop current animation"""
        self.is_animating = False

class ModernButton(tk.Canvas):
    """Modern animated button with hover effects"""
    
    def __init__(self, parent, text, command=None, icon=None, **kwargs):
        # Extract custom parameters
        hover_bg = kwargs.pop('hover_bg', '#4e4e52')
        pressed_bg = kwargs.pop('pressed_bg', '#2e2e32')
        text_color = kwargs.pop('text_color', '#d4d4d4')
        
        super().__init__(parent, **kwargs)
        self.text = text
        self.command = command
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        
        # Colors
        self.normal_bg = kwargs.get('bg', '#3e3e42')
        self.hover_bg = hover_bg
        self.pressed_bg = pressed_bg
        self.text_color = text_color
        
        self.setup_button()
        
    def setup_button(self):
        """Setup button appearance and bindings"""
        self.configure(highlightthickness=0, relief='flat')
        
        # Bind events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
        
        self.draw_button()
        
    def draw_button(self):
        """Draw the button"""
        self.delete('all')
        
        # Get current colors based on state
        if self.is_pressed:
            bg_color = self.pressed_bg
        elif self.is_hovered:
            bg_color = self.hover_bg
        else:
            bg_color = self.normal_bg
            
        # Draw background with rounded corners
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Rounded rectangle
        radius = 6
        self.create_rounded_rectangle(0, 0, width, height, radius, fill=bg_color)
        
        # Draw icon if provided
        icon_x = 10
        if self.icon:
            self.create_text(icon_x, height//2, text=self.icon, 
                           fill=self.text_color, font=('Arial', 12))
            icon_x = 30
            
        # Draw text
        self.create_text(icon_x + 5, height//2, text=self.text, 
                        fill=self.text_color, font=('Segoe UI', 9), anchor='w')
        
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        """Create a rounded rectangle"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        """Handle mouse enter"""
        self.is_hovered = True
        self.draw_button()
        
    def on_leave(self, event):
        """Handle mouse leave"""
        self.is_hovered = False
        self.is_pressed = False
        self.draw_button()
        
    def on_press(self, event):
        """Handle mouse press"""
        self.is_pressed = True
        self.draw_button()
        
    def on_release(self, event):
        """Handle mouse release"""
        self.is_pressed = False
        self.draw_button()
        if self.command:
            self.command()

class SyntaxHighlighter:
    """Advanced syntax highlighter with real-time processing"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.highlight_thread = None
        self.highlight_queue = []
        self.is_highlighting = False
        
        # Syntax patterns
        self.patterns = {
            'keywords': {
                'python': r'\b(def|class|import|from|as|if|else|elif|for|while|try|except|finally|with|return|yield|break|continue|pass|raise|assert|del|global|nonlocal|lambda|True|False|None|and|or|not|in|is)\b',
                'csharp': r'\b(using|namespace|class|struct|interface|enum|public|private|protected|internal|static|readonly|const|virtual|override|abstract|sealed|new|this|base|null|true|false|if|else|switch|case|default|for|foreach|while|do|break|continue|return|throw|try|catch|finally|lock|using|var|void|int|string|bool|float|double|decimal|object|dynamic)\b',
                'javascript': r'\b(function|var|let|const|if|else|switch|case|default|for|while|do|break|continue|return|try|catch|finally|throw|new|delete|typeof|instanceof|in|of|class|extends|super|import|export|default|async|await|yield|true|false|null|undefined)\b'
            },
            'strings': r'"[^"]*"|\'[^\']*\'',
            'comments': r'//.*$|/\*.*?\*/|#.*$',
            'numbers': r'\b\d+\.?\d*\b',
            'functions': r'\b\w+(?=\()'
        }
        
        # Colors
        self.colors = {
            'keywords': '#569cd6',
            'strings': '#ce9178',
            'comments': '#6a9955',
            'numbers': '#b5cea8',
            'functions': '#dcdcaa'
        }
        
    def start_highlighting(self):
        """Start the highlighting thread"""
        if not self.is_highlighting:
            self.is_highlighting = True
            self.highlight_thread = threading.Thread(target=self.highlight_worker, daemon=True)
            self.highlight_thread.start()
            
    def stop_highlighting(self):
        """Stop the highlighting thread"""
        self.is_highlighting = False
        
    def queue_highlight(self):
        """Queue a highlight operation"""
        if not self.highlight_queue:
            self.highlight_queue.append(True)
            
    def highlight_worker(self):
        """Background highlighting worker"""
        while self.is_highlighting:
            if self.highlight_queue:
                self.highlight_queue.pop()
                self.perform_highlight()
            time.sleep(0.1)
            
    def perform_highlight(self):
        """Perform syntax highlighting"""
        try:
            content = self.text_widget.get(1.0, tk.END)
            if not content.strip():
                return
                
            # Clear existing tags
            for tag in self.colors.keys():
                self.text_widget.tag_remove(tag, 1.0, tk.END)
                
            # Get file extension for language detection
            # This would need to be passed from the main editor
            language = 'python'  # Default
            
            # Highlight keywords
            if language in self.patterns['keywords']:
                for match in re.finditer(self.patterns['keywords'][language], content, re.IGNORECASE):
                    start = f"1.0+{match.start()}c"
                    end = f"1.0+{match.end()}c"
                    self.text_widget.tag_add('keywords', start, end)
                    
            # Highlight strings
            for match in re.finditer(self.patterns['strings'], content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add('strings', start, end)
                
            # Highlight comments
            for match in re.finditer(self.patterns['comments'], content, re.MULTILINE | re.DOTALL):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add('comments', start, end)
                
            # Highlight numbers
            for match in re.finditer(self.patterns['numbers'], content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add('numbers', start, end)
                
            # Highlight functions
            for match in re.finditer(self.patterns['functions'], content):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_widget.tag_add('functions', start, end)
                
            # Configure tag colors
            for tag, color in self.colors.items():
                self.text_widget.tag_config(tag, foreground=color)
                
        except Exception as e:
            print(f"Highlighting error: {e}")

class AnoraEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Anora Code Editor")
        self.root.geometry("1000x700")
        self.root.minsize(600, 400)
        
        # Dark theme colors
        self.colors = {
            'bg': '#1e1e1e',
            'text': '#d4d4d4',
            'selection': '#264f78',
            'current_line': '#33415e',
            'tabs': '#2d2d30',
            'buttons': '#3e3e42',
            'hover': '#4e4e52',
            'pressed': '#2e2e32',
            'keywords': '#569cd6',
            'strings': '#ce9178',
            'comments': '#6a9955',
            'numbers': '#b5cea8',
            'functions': '#dcdcaa',
            'error': '#f44747',
            'warning': '#ffcc02',
            'success': '#4ec9b0'
        }
        
        # Editor state
        self.tabs = []
        self.current_tab = None
        self.closed_tabs = []
        self.recent_files = []
        self.always_on_top = False
        self.fullscreen = False
        self.find_panel_visible = False
        self.search_matches = []
        self.current_match = -1
        self.animations = []
        
        # Configure the root window
        self.root.configure(bg=self.colors['bg'])
        self.setup_styles()
        self.create_widgets()
        self.setup_bindings()
        self.load_session()
        
        # Start autosave thread
        self.autosave_thread = threading.Thread(target=self.autosave_worker, daemon=True)
        self.autosave_thread.start()
        
        # Start animation loop
        self.animation_loop()
        
    def setup_styles(self):
        """Configure ttk styles for dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['tabs'],
                       foreground=self.colors['text'],
                       padding=[15, 8],
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['selection'])],
                 foreground=[('selected', self.colors['text'])])
        
    def create_widgets(self):
        """Create all UI widgets with animations"""
        # Menu bar
        self.create_menu()
        
        # Toolbar with modern buttons
        self.create_toolbar()
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Search panel (hidden by default)
        self.create_search_panel()
        
        # Status bar
        self.create_status_bar()
        
        # Create initial tab
        self.new_tab()
        
    def create_menu(self):
        """Create the menu bar with modern styling"""
        menubar = tk.Menu(self.root, bg=self.colors['bg'], fg=self.colors['text'])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['bg'], fg=self.colors['text'])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
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
        edit_menu.add_command(label="Find", command=self.show_find_panel, accelerator="Ctrl+F")
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
        """Create the toolbar with modern animated buttons"""
        toolbar = tk.Frame(self.root, bg=self.colors['bg'], height=40)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        toolbar.pack_propagate(False)
        
        # Toolbar buttons with icons
        buttons = [
            ("📄", "New", self.new_file),
            ("📂", "Open", self.open_file),
            ("💾", "Save", self.save_file),
            ("🔍", "Find", self.show_find_panel),
            ("🔄", "Replace", self.show_replace_panel),
            ("📌", "Pin", self.toggle_always_on_top),
            ("⛶", "Full", self.toggle_fullscreen)
        ]
        
        for icon, tooltip, command in buttons:
            btn = ModernButton(toolbar, text=tooltip, command=command,
                              icon=icon, bg=self.colors['buttons'],
                              hover_bg=self.colors['hover'],
                              pressed_bg=self.colors['pressed'],
                              text_color=self.colors['text'])
            btn.pack(side=tk.LEFT, padx=2, pady=5)
            
    def create_search_panel(self):
        """Create the search and replace panel with animations"""
        self.search_frame = tk.Frame(self.root, bg=self.colors['bg'], height=50)
        
        # Find input with modern styling
        tk.Label(self.search_frame, text="Find:", bg=self.colors['bg'], 
                fg=self.colors['text'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        self.find_entry = tk.Entry(self.search_frame, bg=self.colors['buttons'], 
                                  fg=self.colors['text'], insertbackground=self.colors['text'],
                                  relief='flat', width=25, font=('Consolas', 10))
        self.find_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Replace input
        tk.Label(self.search_frame, text="Replace:", bg=self.colors['bg'], 
                fg=self.colors['text'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=5)
        
        self.replace_entry = tk.Entry(self.search_frame, bg=self.colors['buttons'], 
                                     fg=self.colors['text'], insertbackground=self.colors['text'],
                                     relief='flat', width=25, font=('Consolas', 10))
        self.replace_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Modern buttons
        find_btn = ModernButton(self.search_frame, text="Find", command=self.find_text,
                    bg=self.colors['buttons'], hover_bg=self.colors['hover'],
                    pressed_bg=self.colors['pressed'], text_color=self.colors['text'])
        find_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        replace_btn = ModernButton(self.search_frame, text="Replace", command=self.replace_text,
                    bg=self.colors['buttons'], hover_bg=self.colors['hover'],
                    pressed_bg=self.colors['pressed'], text_color=self.colors['text'])
        replace_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        replace_all_btn = ModernButton(self.search_frame, text="Replace All", command=self.replace_all,
                    bg=self.colors['buttons'], hover_bg=self.colors['hover'],
                    pressed_bg=self.colors['pressed'], text_color=self.colors['text'])
        replace_all_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        next_btn = ModernButton(self.search_frame, text="Next", command=self.next_match,
                    bg=self.colors['buttons'], hover_bg=self.colors['hover'],
                    pressed_bg=self.colors['pressed'], text_color=self.colors['text'])
        next_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        prev_btn = ModernButton(self.search_frame, text="Prev", command=self.prev_match,
                    bg=self.colors['buttons'], hover_bg=self.colors['hover'],
                    pressed_bg=self.colors['pressed'], text_color=self.colors['text'])
        prev_btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        close_btn = ModernButton(self.search_frame, text="✕", command=self.hide_search_panel,
                    bg=self.colors['error'], hover_bg='#ff6666',
                    pressed_bg='#cc3333', text_color='white')
        close_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
    def create_status_bar(self):
        """Create the status bar with animations"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg'], height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.position_label = tk.Label(self.status_bar, text="Line 1, Col 1",
                                      bg=self.colors['bg'], fg=self.colors['text'],
                                      font=('Segoe UI', 9))
        self.position_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        self.message_label = tk.Label(self.status_bar, text="Ready",
                                     bg=self.colors['bg'], fg=self.colors['success'],
                                     font=('Segoe UI', 9))
        self.message_label.pack(side=tk.RIGHT, padx=10, pady=2)
        
    def create_text_widget(self, parent):
        """Create a text widget with line numbers and syntax highlighting"""
        # Main frame
        frame = tk.Frame(parent, bg=self.colors['bg'])
        
        # Line numbers with modern styling
        self.line_numbers = tk.Text(frame, width=5, padx=8, takefocus=0,
                                   border=0, background=self.colors['tabs'],
                                   foreground=self.colors['text'], state='disabled',
                                   font=('Consolas', 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Text widget with advanced features
        text_widget = tk.Text(frame, wrap=tk.NONE, undo=True,
                             bg=self.colors['bg'], fg=self.colors['text'],
                             insertbackground=self.colors['text'],
                             selectbackground=self.colors['selection'],
                             font=('Consolas', 11), padx=10, pady=10,
                             relief='flat', borderwidth=0)
        text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Scrollbars with modern styling
        v_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview,
                                  bg=self.colors['tabs'], troughcolor=self.colors['bg'],
                                  width=12, relief='flat')
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=text_widget.xview,
                                  bg=self.colors['tabs'], troughcolor=self.colors['bg'],
                                  width=12, relief='flat')
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        text_widget.bind('<KeyRelease>', self.on_text_change)
        text_widget.bind('<Button-1>', self.update_position)
        text_widget.bind('<Key>', self.update_position)
        text_widget.bind('<ButtonRelease-1>', self.update_position)
        text_widget.bind('<KeyRelease>', self.update_position)
        
        # Initialize syntax highlighter
        highlighter = SyntaxHighlighter(text_widget)
        highlighter.start_highlighting()
        
        return frame, text_widget, highlighter
        
    def new_tab(self, file_path=None):
        """Create a new tab with animations"""
        frame, text_widget, highlighter = self.create_text_widget(self.notebook)
        
        tab_info = {
            'frame': frame,
            'text': text_widget,
            'highlighter': highlighter,
            'file_path': file_path,
            'modified': False,
            'content': ''
        }
        
        self.tabs.append(tab_info)
        
        # Create tab title
        if file_path:
            title = os.path.basename(file_path)
        else:
            title = "Untitled"
            
        self.notebook.add(frame, text=title)
        self.notebook.select(len(self.tabs) - 1)
        self.current_tab = len(self.tabs) - 1
        
        # Load file content if path provided
        if file_path:
            self.load_file_content(file_path, text_widget)
            
        # Animate tab creation
        self.animate_tab_creation(frame)
        
        return tab_info
        
    def animate_tab_creation(self, frame):
        """Animate the creation of a new tab"""
        # Start with 0 opacity and animate to full
        frame.configure(bg=self.colors['bg'])
        
        def fade_in():
            for i in range(10):
                alpha = i / 10.0
                frame.configure(bg=self.colors['bg'])
                self.root.update()
                time.sleep(0.02)
                
        threading.Thread(target=fade_in, daemon=True).start()
        
    def show_find_panel(self):
        """Show find panel with slide animation"""
        if not self.find_panel_visible:
            self.search_frame.pack(fill=tk.X, before=self.notebook)
            self.find_panel_visible = True
            self.find_entry.focus()
            
            # Animate panel appearance
            self.animate_panel_slide(self.search_frame, True)
            
    def hide_search_panel(self):
        """Hide search panel with slide animation"""
        if self.find_panel_visible:
            self.animate_panel_slide(self.search_frame, False)
            
    def animate_panel_slide(self, panel, show):
        """Animate panel sliding in/out"""
        def slide_animation():
            if show:
                # Slide down
                for i in range(10):
                    height = int((i + 1) * 5)
                    panel.configure(height=height)
                    self.root.update()
                    time.sleep(0.02)
            else:
                # Slide up
                for i in range(10, 0, -1):
                    height = int(i * 5)
                    panel.configure(height=height)
                    self.root.update()
                    time.sleep(0.02)
                panel.pack_forget()
                self.find_panel_visible = False
                self.clear_search_highlights()
                
        threading.Thread(target=slide_animation, daemon=True).start()
        
    def animation_loop(self):
        """Main animation loop for smooth transitions"""
        # Update animations
        for animation in self.animations[:]:
            if not animation.is_animating:
                self.animations.remove(animation)
                
        # Schedule next frame
        self.root.after(16, self.animation_loop)  # ~60 FPS
        
    def show_message(self, message, message_type='info'):
        """Show animated message in status bar"""
        colors = {
            'info': self.colors['text'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['error']
        }
        
        self.message_label.configure(text=message, fg=colors.get(message_type, self.colors['text']))
        
        # Animate message appearance
        def message_animation():
            for i in range(5):
                self.message_label.configure(fg=colors.get(message_type, self.colors['text']))
                time.sleep(0.1)
                self.message_label.configure(fg=self.colors['bg'])
                time.sleep(0.1)
            self.message_label.configure(fg=colors.get(message_type, self.colors['text']))
            
        threading.Thread(target=message_animation, daemon=True).start()
        
    def new_file(self):
        """Create a new file"""
        self.new_tab()
        
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
            self.add_recent_file(file_path)
            
    def load_file_content(self, file_path, text_widget):
        """Load content from file into text widget"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_widget.delete(1.0, tk.END)
                text_widget.insert(1.0, content)
                self.update_line_numbers(text_widget)
                self.update_position()
                self.show_message(f"Loaded: {os.path.basename(file_path)}", 'success')
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
            
    def save_file(self):
        """Save current file"""
        if not self.tabs:
            return
            
        current_tab = self.tabs[self.current_tab]
        
        if current_tab['file_path']:
            self.save_to_file(current_tab['file_path'], current_tab['text'])
        else:
            self.save_as()
            
    def save_as(self):
        """Save file as"""
        if not self.tabs:
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
            current_tab = self.tabs[self.current_tab]
            self.save_to_file(file_path, current_tab['text'])
            current_tab['file_path'] = file_path
            self.update_tab_title()
            self.add_recent_file(file_path)
            
    def save_to_file(self, file_path, text_widget):
        """Save text widget content to file"""
        try:
            content = text_widget.get(1.0, tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.set_modified(False)
            self.show_message(f"Saved: {os.path.basename(file_path)}", 'success')
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            
    def close_tab(self):
        """Close current tab"""
        if not self.tabs:
            return
            
        current_tab = self.tabs[self.current_tab]
        
        if current_tab['modified']:
            result = messagebox.askyesnocancel("Save Changes", 
                                             "Do you want to save changes?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                self.save_file()
                
        # Store in closed tabs for reopening
        self.closed_tabs.append(current_tab)
        
        # Remove tab
        self.notebook.forget(self.current_tab)
        self.tabs.pop(self.current_tab)
        
        if self.tabs:
            self.current_tab = min(self.current_tab, len(self.tabs) - 1)
            self.notebook.select(self.current_tab)
        else:
            self.new_tab()
            
    def close_others(self):
        """Close all tabs except current"""
        if len(self.tabs) <= 1:
            return
            
        current_index = self.current_tab
        tabs_to_close = []
        
        for i, tab in enumerate(self.tabs):
            if i != current_index:
                tabs_to_close.append((i, tab))
                
        for index, tab in reversed(tabs_to_close):
            if tab['modified']:
                result = messagebox.askyesnocancel("Save Changes", 
                                                 f"Save changes to {tab.get('file_path', 'Untitled')}?")
                if result is None:  # Cancel
                    return
                elif result:  # Yes
                    if tab['file_path']:
                        self.save_to_file(tab['file_path'], tab['text'])
                    else:
                        continue
                        
            self.closed_tabs.append(tab)
            self.notebook.forget(index)
            self.tabs.pop(index)
            
        self.current_tab = 0
        self.notebook.select(0)
        
    def reopen_closed_tab(self):
        """Reopen the last closed tab"""
        if not self.closed_tabs:
            return
            
        tab_info = self.closed_tabs.pop()
        self.new_tab(tab_info['file_path'])
        
        # Restore content
        current_tab = self.tabs[self.current_tab]
        current_tab['text'].delete(1.0, tk.END)
        current_tab['text'].insert(1.0, tab_info['content'])
        current_tab['modified'] = tab_info['modified']
        
    def undo(self):
        """Undo last action"""
        if self.tabs:
            self.tabs[self.current_tab]['text'].edit_undo()
            
    def redo(self):
        """Redo last action"""
        if self.tabs:
            self.tabs[self.current_tab]['text'].edit_redo()
            
    def cut(self):
        """Cut selected text"""
        if self.tabs:
            self.tabs[self.current_tab]['text'].event_generate("<<Cut>>")
            
    def copy(self):
        """Copy selected text"""
        if self.tabs:
            self.tabs[self.current_tab]['text'].event_generate("<<Copy>>")
            
    def paste(self):
        """Paste text"""
        if self.tabs:
            self.tabs[self.current_tab]['text'].event_generate("<<Paste>>")
            
    def select_all(self):
        """Select all text"""
        if self.tabs:
            self.tabs[self.current_tab]['text'].tag_add(tk.SEL, "1.0", tk.END)
            
    def show_replace_panel(self):
        """Show replace panel"""
        if not self.find_panel_visible:
            self.search_frame.pack(fill=tk.X, before=self.notebook)
            self.find_panel_visible = True
            self.find_entry.focus()
            
    def find_text(self):
        """Find text in current tab"""
        if not self.tabs:
            return
            
        search_text = self.find_entry.get()
        if not search_text:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        self.clear_search_highlights()
        
        # Find all matches
        self.search_matches = []
        content = text_widget.get(1.0, tk.END)
        
        for match in re.finditer(re.escape(search_text), content, re.IGNORECASE):
            start_line = content[:match.start()].count('\n') + 1
            start_col = match.start() - content.rfind('\n', 0, match.start()) - 1
            end_line = content[:match.end()].count('\n') + 1
            end_col = match.end() - content.rfind('\n', 0, match.end()) - 1
            
            self.search_matches.append((f"{start_line}.{start_col}", f"{end_line}.{end_col}"))
            
        # Highlight all matches
        for start, end in self.search_matches:
            text_widget.tag_add("search", start, end)
            
        text_widget.tag_config("search", background="yellow")
        
        if self.search_matches:
            self.current_match = 0
            self.highlight_current_match()
            self.show_message(f"Found {len(self.search_matches)} matches", 'success')
        else:
            self.show_message("No matches found", 'warning')
            
    def highlight_current_match(self):
        """Highlight current search match"""
        if not self.search_matches or self.current_match < 0:
            return
            
        text_widget = self.tabs[self.current_tab]['text']
        
        # Clear previous current match highlight
        text_widget.tag_remove("current_match", "1.0", tk.END)
        
        # Highlight current match
        start, end = self.search_matches[self.current_match]
        text_widget.tag_add("current_match", start, end)
        text_widget.tag_config("current_match", background="green")
        
        # Scroll to current match
        text_widget.see(start)
        
    def next_match(self):
        """Go to next search match"""
        if not self.search_matches:
            return
            
        self.current_match = (self.current_match + 1) % len(self.search_matches)
        self.highlight_current_match()
        
    def prev_match(self):
        """Go to previous search match"""
        if not self.search_matches:
            return
            
        self.current_match = (self.current_match - 1) % len(self.search_matches)
        self.highlight_current_match()
        
    def replace_text(self):
        """Replace current search match"""
        if not self.search_matches or self.current_match < 0:
            return
            
        replace_text = self.replace_entry.get()
        text_widget = self.tabs[self.current_tab]['text']
        
        start, end = self.search_matches[self.current_match]
        text_widget.delete(start, end)
        text_widget.insert(start, replace_text)
        
        self.set_modified(True)
        self.find_text()  # Refresh search
        
    def replace_all(self):
        """Replace all search matches"""
        if not self.search_matches:
            return
            
        replace_text = self.replace_entry.get()
        text_widget = self.tabs[self.current_tab]['text']
        
        # Replace from end to start to maintain positions
        for start, end in reversed(self.search_matches):
            text_widget.delete(start, end)
            text_widget.insert(start, replace_text)
            
        self.set_modified(True)
        self.clear_search_highlights()
        self.show_message(f"Replaced {len(self.search_matches)} matches", 'success')
        
    def clear_search_highlights(self):
        """Clear search highlights"""
        if self.tabs:
            text_widget = self.tabs[self.current_tab]['text']
            text_widget.tag_remove("search", "1.0", tk.END)
            text_widget.tag_remove("current_match", "1.0", tk.END)
            
    def toggle_always_on_top(self):
        """Toggle always on top"""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        status = "enabled" if self.always_on_top else "disabled"
        self.show_message(f"Always on top {status}", 'info')
        
    def toggle_fullscreen(self):
        """Toggle fullscreen"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        status = "enabled" if self.fullscreen else "disabled"
        self.show_message(f"Fullscreen {status}", 'info')
        
    def go_to_line(self):
        """Go to specific line"""
        if not self.tabs:
            return
            
        line_num = simpledialog.askinteger("Go To Line", "Enter line number:")
        if line_num:
            text_widget = self.tabs[self.current_tab]['text']
            text_widget.see(f"{line_num}.0")
            text_widget.mark_set(tk.INSERT, f"{line_num}.0")
            self.show_message(f"Jumped to line {line_num}", 'info')
            
    def on_text_change(self, event=None):
        """Handle text changes"""
        if self.tabs:
            current_tab = self.tabs[self.current_tab]
            current_tab['content'] = current_tab['text'].get(1.0, tk.END)
            self.set_modified(True)
            self.update_line_numbers(current_tab['text'])
            
            # Queue syntax highlighting
            if hasattr(current_tab, 'highlighter'):
                current_tab['highlighter'].queue_highlight()
            
    def set_modified(self, modified):
        """Set tab modified state"""
        if self.tabs:
            current_tab = self.tabs[self.current_tab]
            current_tab['modified'] = modified
            self.update_tab_title()
            
    def update_tab_title(self):
        """Update current tab title"""
        if self.tabs:
            current_tab = self.tabs[self.current_tab]
            title = os.path.basename(current_tab['file_path']) if current_tab['file_path'] else "Untitled"
            if current_tab['modified']:
                title += " *"
            self.notebook.tab(self.current_tab, text=title)
            
    def update_line_numbers(self, text_widget):
        """Update line numbers"""
        content = text_widget.get(1.0, tk.END)
        lines = content.count('\n')
        
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 2))
        
        # Find the line numbers widget
        for child in text_widget.master.winfo_children():
            if isinstance(child, tk.Text) and child != text_widget:
                child.config(state='normal')
                child.delete(1.0, tk.END)
                child.insert(1.0, line_numbers_text)
                child.config(state='disabled')
                break
                
    def update_position(self, event=None):
        """Update position display in status bar"""
        if self.tabs:
            text_widget = self.tabs[self.current_tab]['text']
            pos = text_widget.index(tk.INSERT)
            line, col = pos.split('.')
            self.position_label.config(text=f"Line {line}, Col {int(col) + 1}")
            
    def on_tab_changed(self, event):
        """Handle tab change"""
        self.current_tab = self.notebook.index(self.notebook.select())
        if self.tabs:
            self.update_position()
            self.update_line_numbers(self.tabs[self.current_tab]['text'])
            
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10
        self.update_recent_menu()
        
    def update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.delete(0, tk.END)
        for file_path in self.recent_files:
            self.recent_menu.add_command(
                label=os.path.basename(file_path),
                command=lambda fp=file_path: self.open_recent_file(fp)
            )
            
    def open_recent_file(self, file_path):
        """Open a recent file"""
        if os.path.exists(file_path):
            self.new_tab(file_path)
        else:
            messagebox.showerror("Error", "File no longer exists")
            self.recent_files.remove(file_path)
            self.update_recent_menu()
            
    def setup_bindings(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.show_find_panel())
        self.root.bind('<Control-h>', lambda e: self.show_replace_panel())
        self.root.bind('<Control-t>', lambda e: self.new_tab())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-g>', lambda e: self.go_to_line())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.bind('<F3>', lambda e: self.next_match())
        self.root.bind('<Shift-F3>', lambda e: self.prev_match())
        
    def load_session(self):
        """Load editor session"""
        session_file = os.path.expanduser("~/.anora_editor_session.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session = json.load(f)
                    
                # Load recent files
                self.recent_files = session.get('recent_files', [])
                self.update_recent_menu()
                
                # Load open tabs
                open_files = session.get('open_files', [])
                for file_path in open_files:
                    if os.path.exists(file_path):
                        self.new_tab(file_path)
                        
            except Exception as e:
                print(f"Error loading session: {e}")
                
    def save_session(self):
        """Save editor session"""
        session_file = os.path.expanduser("~/.anora_editor_session.json")
        try:
            session = {
                'recent_files': self.recent_files,
                'open_files': [tab['file_path'] for tab in self.tabs if tab['file_path']]
            }
            
            with open(session_file, 'w') as f:
                json.dump(session, f)
                
        except Exception as e:
            print(f"Error saving session: {e}")
            
    def autosave_worker(self):
        """Background thread for autosaving"""
        while True:
            time.sleep(0.5)  # Autosave every 500ms
            if self.tabs:
                self.save_session()
                
    def quit_app(self):
        """Quit the application"""
        # Save session
        self.save_session()
        
        # Check for unsaved changes
        unsaved_tabs = [tab for tab in self.tabs if tab['modified']]
        if unsaved_tabs:
            result = messagebox.askyesnocancel("Save Changes", 
                                             f"You have {len(unsaved_tabs)} unsaved file(s). Save before quitting?")
            if result is None:  # Cancel
                return
            elif result:  # Yes
                for tab in unsaved_tabs:
                    if tab['file_path']:
                        self.save_to_file(tab['file_path'], tab['text'])
                    else:
                        continue
                        
        self.root.quit()
        
    def run(self):
        """Run the editor with smooth animations"""
        self.root.mainloop()

if __name__ == "__main__":
    editor = AnoraEditor()
    editor.run()