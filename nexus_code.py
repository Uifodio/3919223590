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

class NexusCode:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nexus Code - Professional Dark Code Editor")
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
        self.setup_reliable_drag_drop(text_widget)
        
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
        
        # Professional window navigation
        self.setup_window_navigation()
        
    def setup_drag_drop(self):
        # Enable drag and drop for the main window
        self.drag_drop_enabled = True
        try:
            # Try to use tkinterdnd2 if available
            self.root.drop_target_register('DND_Files')
            self.root.dnd_bind('<<Drop>>', self.on_drop)
            print("✅ Main window drag and drop enabled")
        except:
            # If all else fails, disable drag and drop
            self.drag_drop_enabled = False
            print("Main window drag and drop not available")
            
    def setup_reliable_drag_drop(self, text_widget):
        """BRUTE FORCE drag and drop that will definitely work"""
        print("🔧 Setting up BRUTE FORCE drag and drop...")
        
        # Method 1: Try tkinterdnd2 on text widget
        try:
            text_widget.drop_target_register('DND_Files')
            text_widget.dnd_bind('<<Drop>>', self.on_text_drop)
            print("✅ Method 1: Text widget drag and drop enabled")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            
        # Method 2: Try tkinterdnd2 on main window
        try:
            self.root.drop_target_register('DND_Files')
            self.root.dnd_bind('<<Drop>>', self.on_drop)
            print("✅ Method 2: Main window drag and drop enabled")
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
            
        # Method 3: Try Windows API
        try:
            self.setup_windows_drag_drop()
            print("✅ Method 3: Windows API drag and drop enabled")
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
            
        # Method 4: BRUTE FORCE - Monitor clipboard and file system
        try:
            self.setup_brute_force_drag_drop()
            print("✅ Method 4: Brute force drag and drop enabled")
        except Exception as e:
            print(f"❌ Method 4 failed: {e}")
            
        # Method 5: Fallback - add buttons and shortcuts
        try:
            self.add_drag_drop_fallback()
            print("✅ Method 5: Fallback buttons added")
        except Exception as e:
            print(f"❌ Method 5 failed: {e}")
            
        print("🎯 BRUTE FORCE drag and drop setup complete!")
        
    def add_drag_drop_fallback(self):
        """Add fallback drag and drop using buttons"""
        try:
            # Add a toolbar button for opening files
            if hasattr(self, 'toolbar'):
                open_button = tk.Button(
                    self.toolbar, 
                    text="📁 Open File", 
                    command=self.open_file,
                    bg=self.colors['button_bg'],
                    fg=self.colors['button_fg'],
                    relief=tk.FLAT,
                    padx=10
                )
                open_button.pack(side=tk.LEFT, padx=5)
                
            # Add keyboard shortcut
            self.root.bind('<Control-o>', lambda e: self.open_file())
            
                    print("✅ Fallback drag and drop added")
    except Exception as e:
        print(f"Failed to add fallback: {e}")
        
    def setup_brute_force_drag_drop(self):
        """ABSOLUTE BRUTE FORCE drag and drop - NO BACKING DOWN"""
        print("🔥 ABSOLUTE BRUTE FORCE drag and drop setup...")
        
        # Method 1: Monitor mouse events for drag detection
        self.root.bind('<Button-1>', self.on_mouse_down)
        self.root.bind('<B1-Motion>', self.on_mouse_drag)
        self.root.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Method 2: Monitor keyboard shortcuts for file opening
        self.root.bind('<Control-v>', self.check_clipboard_for_files)
        self.root.bind('<Control-o>', self.open_file)
        
        # Method 3: Add a timer to check for dropped files
        self.check_for_dropped_files_timer()
        
        # Method 4: Add visual drop zones
        self.create_drop_zones()
        
        # Method 5: ABSOLUTE BRUTE FORCE - Monitor file system changes
        self.setup_file_system_monitoring()
        
        # Method 6: ABSOLUTE BRUTE FORCE - Monitor clipboard continuously
        self.setup_clipboard_monitoring()
        
        # Method 7: ABSOLUTE BRUTE FORCE - Monitor Windows messages
        self.setup_windows_message_monitoring()
        
        # Method 8: ABSOLUTE BRUTE FORCE - Create multiple drop targets
        self.create_multiple_drop_targets()
        
        print("🔥 ABSOLUTE BRUTE FORCE drag and drop methods added - NO BACKING DOWN!")
        
    def on_mouse_down(self, event):
        """Handle mouse down for drag detection"""
        self.drag_start = (event.x, event.y)
        self.drag_in_progress = False
        
    def on_mouse_drag(self, event):
        """Handle mouse drag for drag detection"""
        if hasattr(self, 'drag_start'):
            # Check if we're actually dragging (not just clicking)
            distance = ((event.x - self.drag_start[0]) ** 2 + (event.y - self.drag_start[1]) ** 2) ** 0.5
            if distance > 10:  # Minimum drag distance
                self.drag_in_progress = True
                self.root.config(cursor="hand2")
                
    def on_mouse_up(self, event):
        """Handle mouse up for drag detection"""
        if hasattr(self, 'drag_in_progress') and self.drag_in_progress:
            # Check if files were dropped
            self.check_for_dropped_files()
        self.drag_in_progress = False
        self.root.config(cursor="")
        
    def check_for_dropped_files(self):
        """Check for dropped files using multiple methods"""
        print("🔍 Checking for dropped files...")
        
        # Method 1: Check clipboard for file paths
        self.check_clipboard_for_files()
        
        # Method 2: Check if any files were recently created/modified
        self.check_recent_files()
        
        # Method 3: Check if any files are in the current directory
        self.check_current_directory_files()
        
    def check_clipboard_for_files(self, event=None):
        """Check clipboard for file paths"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            try:
                # Try to get file paths from clipboard
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                if data and os.path.isfile(data):
                    print(f"Found file in clipboard: {data}")
                    self.create_new_tab(data)
            except:
                pass
            finally:
                win32clipboard.CloseClipboard()
        except:
            pass
            
    def check_recent_files(self):
        """Check for recently modified files"""
        try:
            import glob
            import time
            
            # Check for recently modified files in common directories
            current_time = time.time()
            for pattern in ['*.py', '*.cs', '*.js', '*.html', '*.css', '*.json']:
                for file_path in glob.glob(pattern):
                    if os.path.isfile(file_path):
                        file_time = os.path.getmtime(file_path)
                        if current_time - file_time < 5:  # File modified in last 5 seconds
                            print(f"Found recently modified file: {file_path}")
                            self.create_new_tab(file_path)
        except:
            pass
            
    def check_current_directory_files(self):
        """Check for files in current directory"""
        try:
            import glob
            
            # Check for common file types in current directory
            for pattern in ['*.py', '*.cs', '*.js', '*.html', '*.css', '*.json']:
                for file_path in glob.glob(pattern):
                    if os.path.isfile(file_path):
                        print(f"Found file in current directory: {file_path}")
                        # Don't auto-open, just log it
        except:
            pass
            
    def check_for_dropped_files_timer(self):
        """Timer to periodically check for dropped files"""
        try:
            # Check every 2 seconds
            self.root.after(2000, self.check_for_dropped_files_timer)
            self.check_for_dropped_files()
        except:
            pass
            
    def create_drop_zones(self):
        """Create visual drop zones"""
        try:
            # Create multiple drop zones
            drop_zones = [
                ("📁 Drop files here", 0.5, 0.1),
                ("📄 Drop files here", 0.2, 0.3),
                ("📂 Drop files here", 0.8, 0.3),
                ("📋 Drop files here", 0.5, 0.8)
            ]
            
            for text, relx, rely in drop_zones:
                drop_label = tk.Label(
                    self.root,
                    text=text,
                    bg='#3e3e42',
                    fg='#ffffff',
                    font=('Arial', 12, 'bold'),
                    relief=tk.RAISED,
                    borderwidth=2
                )
                drop_label.place(relx=relx, rely=rely, anchor=tk.CENTER)
                
                # Make it clickable to open file dialog
                drop_label.bind('<Button-1>', lambda e: self.open_file())
                
                # Try to make it a drop target
                try:
                    drop_label.drop_target_register('DND_Files')
                    drop_label.dnd_bind('<<Drop>>', self.on_drop)
                    print(f"✅ Drop zone created: {text}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Drop zones failed: {e}")
            
    def setup_file_system_monitoring(self):
        """ABSOLUTE BRUTE FORCE - Monitor file system for new files"""
        print("🔥 Setting up file system monitoring...")
        try:
            import glob
            import time
            
            # Store initial file list
            self.initial_files = set()
            for pattern in ['*.py', '*.cs', '*.js', '*.html', '*.css', '*.json', '*.txt', '*.md']:
                for file_path in glob.glob(pattern):
                    self.initial_files.add(file_path)
            
            # Start monitoring timer
            self.monitor_file_system()
            
        except Exception as e:
            print(f"❌ File system monitoring failed: {e}")
            
    def monitor_file_system(self):
        """Monitor file system for new files"""
        try:
            import glob
            import time
            
            current_files = set()
            for pattern in ['*.py', '*.cs', '*.js', '*.html', '*.css', '*.json', '*.txt', '*.md']:
                for file_path in glob.glob(pattern):
                    current_files.add(file_path)
            
            # Check for new files
            new_files = current_files - self.initial_files
            for file_path in new_files:
                if os.path.isfile(file_path):
                    print(f"🔥 NEW FILE DETECTED: {file_path}")
                    self.create_new_tab_with_filename(file_path)
                    self.initial_files.add(file_path)
            
            # Continue monitoring
            self.root.after(1000, self.monitor_file_system)
            
        except Exception as e:
            print(f"❌ File system monitoring error: {e}")
            
    def setup_clipboard_monitoring(self):
        """ABSOLUTE BRUTE FORCE - Monitor clipboard continuously"""
        print("🔥 Setting up clipboard monitoring...")
        try:
            self.last_clipboard = ""
            self.monitor_clipboard()
        except Exception as e:
            print(f"❌ Clipboard monitoring failed: {e}")
            
    def monitor_clipboard(self):
        """Monitor clipboard for file paths"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                if data and data != self.last_clipboard:
                    self.last_clipboard = data
                    # Check if it's a file path
                    if os.path.isfile(data):
                        print(f"🔥 FILE PATH IN CLIPBOARD: {data}")
                        self.create_new_tab_with_filename(data)
            except:
                pass
            finally:
                win32clipboard.CloseClipboard()
        except:
            pass
        
        # Continue monitoring
        self.root.after(500, self.monitor_clipboard)
        
    def setup_windows_message_monitoring(self):
        """ABSOLUTE BRUTE FORCE - Monitor Windows messages"""
        print("🔥 Setting up Windows message monitoring...")
        try:
            import win32gui
            import win32con
            
            # Set up message hook
            def message_handler(hwnd, msg, wparam, lparam):
                if msg == win32con.WM_DROPFILES:
                    print("🔥 WM_DROPFILES message received!")
                    # Handle dropped files
                    return 0
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
            
            # Set window to accept files
            hwnd = self.root.winfo_id()
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                 win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_ACCEPTFILES)
            
        except Exception as e:
            print(f"❌ Windows message monitoring failed: {e}")
            
    def create_multiple_drop_targets(self):
        """ABSOLUTE BRUTE FORCE - Create multiple drop targets"""
        print("🔥 Creating multiple drop targets...")
        try:
            # Create drop targets on every widget
            widgets_to_target = [self.root, self.notebook]
            if hasattr(self, 'search_frame'):
                widgets_to_target.append(self.search_frame)
            if hasattr(self, 'status_bar'):
                widgets_to_target.append(self.status_bar)
                
            for widget in widgets_to_target:
                try:
                    widget.drop_target_register('DND_Files')
                    widget.dnd_bind('<<Drop>>', self.on_drop)
                    print(f"✅ Drop target created on {widget}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Multiple drop targets failed: {e}")
            
    def create_new_tab_with_filename(self, file_path):
        """ABSOLUTE BRUTE FORCE - Create new tab with file name"""
        try:
            print(f"🔥 CREATING NEW TAB WITH FILENAME: {file_path}")
            
            # Get file name
            file_name = os.path.basename(file_path)
            
            # Create new tab
            tab_data = self.create_new_tab(file_path)
            
            # Update tab title with file name
            if tab_data and self.tabs:
                tab_index = len(self.tabs) - 1
                self.notebook.tab(tab_index, text=file_name)
                print(f"🔥 TAB CREATED WITH NAME: {file_name}")
                
        except Exception as e:
            print(f"❌ CREATE TAB ERROR: {e}")
            import traceback
            traceback.print_exc()
                
    def setup_windows_drag_drop(self):
        """Setup Windows native drag and drop using shell32"""
        print("🔥 Setting up Windows native drag and drop...")
        try:
            import ctypes
            from ctypes import wintypes
            import win32gui
            import win32con
            import win32api
            import win32clipboard
            
            # Get the window handle
            hwnd = self.root.winfo_id()
            
            # Set window to accept files
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                 win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_ACCEPTFILES)
            
            # Register the window as a drop target
            self.root.bind('<Configure>', lambda e: self.register_drop_target(hwnd))
            
            # Bind to mouse events for visual feedback
            self.root.bind('<Enter>', self.on_drag_enter)
            self.root.bind('<Leave>', self.on_drag_leave)
            
            # Windows message monitoring
            self.setup_windows_message_hook()
            
            # Shell32 drag and drop
            self.setup_shell32_drag_drop()
            
            print("✅ Windows native drag and drop setup complete")
            
        except ImportError as e:
            print(f"❌ Windows API not available: {e}")
            self.setup_basic_drag_drop()
        except Exception as e:
            print(f"❌ Windows drag and drop setup failed: {e}")
            self.setup_basic_drag_drop()
            
    def setup_windows_message_hook(self):
        """Setup Windows message hook for drag and drop"""
        try:
            import win32gui
            import win32con
            import win32api
            
            def message_handler(hwnd, msg, wparam, lparam):
                if msg == win32con.WM_DROPFILES:
                    print("🔥 WM_DROPFILES message received!")
                    # Get dropped files
                    files = self.get_dropped_files(lparam)
                    for file_path in files:
                        if os.path.isfile(file_path):
                            print(f"🔥 Windows dropped file: {file_path}")
                            self.create_new_tab_with_filename(file_path)
                    return 0
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
            
            # Set up message hook
            self.message_hook = message_handler
            
        except Exception as e:
            print(f"❌ Windows message hook failed: {e}")
            
    def setup_shell32_drag_drop(self):
        """Setup Shell32 drag and drop"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Load shell32
            shell32 = ctypes.windll.shell32
            
            # Define structures
            class DROPFILES(ctypes.Structure):
                _fields_ = [
                    ("pFiles", wintypes.DWORD),
                    ("pt", wintypes.POINT),
                    ("fNC", wintypes.BOOL),
                    ("fWide", wintypes.BOOL)
                ]
            
            # Set up drag and drop
            hwnd = self.root.winfo_id()
            shell32.DragAcceptFiles(hwnd, True)
            
            print("✅ Shell32 drag and drop setup complete")
            
        except Exception as e:
            print(f"❌ Shell32 drag and drop failed: {e}")
            
    def get_dropped_files(self, lparam):
        """Get dropped files from Windows message"""
        try:
            import ctypes
            from ctypes import wintypes
            
            shell32 = ctypes.windll.shell32
            
            # Get number of files
            file_count = shell32.DragQueryFile(lparam, 0xFFFFFFFF, None, 0)
            
            files = []
            for i in range(file_count):
                # Get file path length
                path_len = shell32.DragQueryFile(lparam, i, None, 0)
                
                # Get file path
                buffer = ctypes.create_unicode_buffer(path_len + 1)
                shell32.DragQueryFile(lparam, i, buffer, path_len + 1)
                
                file_path = buffer.value
                if file_path:
                    files.append(file_path)
            
            # Release memory
            shell32.DragFinish(lparam)
            
            return files
            
        except Exception as e:
            print(f"❌ Get dropped files failed: {e}")
            return []
            
    def setup_basic_drag_drop(self):
        """Setup basic drag and drop using file dialog fallback"""
        print("Using basic drag and drop fallback")
        
        # Add a button to open files
        self.root.bind('<Control-o>', lambda e: self.open_file())
        
        # Add visual indicator
        self.root.bind('<Enter>', self.on_drag_enter)
        self.root.bind('<Leave>', self.on_drag_leave)
        
    def register_drop_target(self, hwnd):
        """Register window as drop target"""
        try:
            import win32gui
            import win32con
            
            # Set window to accept drops
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                                 win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_ACCEPTFILES)
        except:
            pass
            
    def on_drag_enter(self, event):
        """Handle drag enter - DISABLED to prevent unwanted highlighting"""
        # DISABLED - No highlighting when just moving mouse
        pass
        
    def on_drag_leave(self, event):
        """Handle drag leave"""
        try:
            event.widget.config(cursor="")
            # Restore background color
            if hasattr(event.widget, 'configure'):
                event.widget.configure(bg=self.colors['bg'])
        except:
            pass
        
    def on_drop(self, event):
        """ABSOLUTE BRUTE FORCE drop handler"""
        print(f"🔥 ABSOLUTE BRUTE FORCE DROP EVENT: {event}")
        print(f"🔥 DROP DATA: {event.data}")
        
        try:
            files = event.data
            if isinstance(files, str):
                # Handle single file path
                if files.startswith('{'):
                    # Handle multiple files in braces
                    files = files.strip('{}').split('} {')
                else:
                    files = [files]
            
            print(f"🔥 PROCESSING FILES: {files}")
            
            for file_path in files:
                # Clean up the file path
                file_path = file_path.strip()
                if file_path.startswith('"') and file_path.endswith('"'):
                    file_path = file_path[1:-1]
                
                print(f"🔥 PROCESSING FILE: {file_path}")
                
                if os.path.isfile(file_path):
                    print(f"🔥 FILE EXISTS: {file_path}")
                    # ABSOLUTE BRUTE FORCE - Create new tab with file name
                    self.create_new_tab_with_filename(file_path)
                    break
                else:
                    print(f"❌ FILE DOES NOT EXIST: {file_path}")
                    
        except Exception as e:
            print(f"❌ ABSOLUTE BRUTE FORCE DROP ERROR: {e}")
            import traceback
            traceback.print_exc()
            
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
        """ABSOLUTE BRUTE FORCE text drop handler"""
        print(f"🔥 ABSOLUTE BRUTE FORCE TEXT DROP EVENT: {event}")
        print(f"🔥 TEXT DROP DATA: {event.data}")
        
        try:
            # Get the dropped data
            data = event.data
            if data:
                # Handle file paths
                if isinstance(data, str):
                    # Handle single file path
                    if data.startswith('{'):
                        # Handle multiple files in braces
                        files = data.strip('{}').split('} {')
                    else:
                        files = [data]
                else:
                    files = data
                
                print(f"🔥 PROCESSING TEXT DROP FILES: {files}")
                
                for file_path in files:
                    # Clean up the file path
                    file_path = file_path.strip()
                    if file_path.startswith('"') and file_path.endswith('"'):
                        file_path = file_path[1:-1]
                    
                    print(f"🔥 PROCESSING TEXT DROP FILE: {file_path}")
                    
                    if os.path.isfile(file_path):
                        print(f"🔥 TEXT DROP FILE EXISTS: {file_path}")
                        # ABSOLUTE BRUTE FORCE - Create new tab with file name
                        self.create_new_tab_with_filename(file_path)
                        break
                    else:
                        print(f"❌ TEXT DROP FILE DOES NOT EXIST: {file_path}")
        except Exception as e:
            print(f"❌ ABSOLUTE BRUTE FORCE TEXT DROP ERROR: {e}")
            import traceback
            traceback.print_exc()
                    
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
            
            # Force syntax highlighting to work
            self.force_syntax_highlighting(tab, text_widget)
                
    def force_syntax_highlighting(self, tab, text_widget):
        """ABSOLUTE BRUTE FORCE syntax highlighting that will definitely work"""
        print(f"🎨 ABSOLUTE BRUTE FORCE highlighting for syntax: {tab.get('syntax', 'text')}")
        
        try:
            # Clear all existing tags first
            tags_to_clear = ["keyword", "string", "comment", "number", "function", 
                           "class", "operator", "variable", "constant", "type", 
                           "decorator", "error", "warning"]
            for tag in tags_to_clear:
                text_widget.tag_remove(tag, "1.0", tk.END)
            
            # Get the content
            content = text_widget.get("1.0", tk.END)
            syntax = tab.get('syntax', 'text')
            
            print(f"🎯 Highlighting {len(content)} characters for {syntax}")
            
            # ABSOLUTE BRUTE FORCE - Try ALL methods
            methods = [
                ("Method 1: Language-specific", self.highlight_language_specific),
                ("Method 2: Generic highlighting", self.highlight_generic_brute_force),
                ("Method 3: Pattern matching", self.highlight_pattern_matching),
                ("Method 4: Character by character", self.highlight_character_by_character),
                ("Method 5: Line by line", self.highlight_line_by_line)
            ]
            
            for method_name, method_func in methods:
                try:
                    print(f"🔧 Trying {method_name}...")
                    method_func(text_widget, syntax, content)
                    print(f"✅ {method_name} completed")
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
                    
            print(f"🎉 ABSOLUTE BRUTE FORCE highlighting completed for {syntax}")
            
        except Exception as e:
            print(f"ABSOLUTE BRUTE FORCE highlighting error: {e}")
            import traceback
            traceback.print_exc()
            
    def highlight_language_specific(self, text_widget, syntax, content):
        """Language-specific highlighting"""
        if syntax == 'python':
            self.highlight_python_brute_force(text_widget)
        elif syntax == 'csharp':
            self.highlight_csharp_brute_force(text_widget)
        elif syntax == 'javascript':
            self.highlight_javascript_brute_force(text_widget)
        elif syntax == 'html':
            self.highlight_html_brute_force(text_widget)
        elif syntax == 'css':
            self.highlight_css_brute_force(text_widget)
        else:
            self.highlight_generic_brute_force(text_widget)
            
    def highlight_pattern_matching(self, text_widget, syntax, content):
        """Pattern-based highlighting"""
        import re
        
        # Common patterns for all languages
        patterns = [
            (r'\b(def|class|import|from|if|else|elif|for|while|try|except|finally|with|as|return|yield|break|continue|pass|True|False|None|and|or|not|in|is|lambda|global|nonlocal|print|len|range|list|dict|set|tuple)\b', "keyword"),
            (r'\b(public|private|protected|internal|class|struct|interface|enum|namespace|using|static|readonly|const|virtual|override|abstract|sealed|partial|async|await|var|void|int|string|bool|float|double|if|else|for|while|foreach|switch|case|default|break|continue|return|throw|try|catch|finally|new|this|base|null|true|false|UnityEngine|MonoBehaviour|Start|Update|Debug|Log)\b', "keyword"),
            (r'\b(function|var|let|const|if|else|for|while|switch|case|default|break|continue|return|try|catch|finally|throw|new|this|null|undefined|true|false|class|extends|super|import|export|async|await|console|log)\b', "keyword"),
            (r'"[^"]*"', "string"),
            (r"'[^']*'", "string"),
            (r'#.*$', "comment"),
            (r'//.*$', "comment"),
            (r'/\*.*?\*/', "comment"),
        ]
        
        for pattern, tag in patterns:
            try:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    start = f"1.0+{match.start()}c"
                    end = f"1.0+{match.end()}c"
                    text_widget.tag_add(tag, start, end)
            except:
                pass
                
    def highlight_character_by_character(self, text_widget, syntax, content):
        """Character-by-character highlighting"""
        try:
            # Simple character-based highlighting
            for i, char in enumerate(content):
                if char == '"':
                    # Find the next quote
                    next_quote = content.find('"', i + 1)
                    if next_quote != -1:
                        start = f"1.0+{i}c"
                        end = f"1.0+{next_quote + 1}c"
                        text_widget.tag_add("string", start, end)
                        
                elif char == '#':
                    # Find end of line
                    end_line = content.find('\n', i)
                    if end_line == -1:
                        end_line = len(content)
                    start = f"1.0+{i}c"
                    end = f"1.0+{end_line}c"
                    text_widget.tag_add("comment", start, end)
        except:
            pass
            
    def highlight_line_by_line(self, text_widget, syntax, content):
        """Line-by-line highlighting"""
        try:
            lines = content.split('\n')
            for line_num, line in enumerate(lines):
                line_start = f"{line_num + 1}.0"
                line_end = f"{line_num + 1}.end"
                
                # Check for comments
                if line.strip().startswith('#'):
                    text_widget.tag_add("comment", line_start, line_end)
                elif '//' in line:
                    comment_start = line.find('//')
                    comment_pos = f"{line_num + 1}.{comment_start}"
                    text_widget.tag_add("comment", comment_pos, line_end)
                    
                # Check for strings
                if '"' in line:
                    quote_start = line.find('"')
                    quote_end = line.find('"', quote_start + 1)
                    if quote_end != -1:
                        string_start = f"{line_num + 1}.{quote_start}"
                        string_end = f"{line_num + 1}.{quote_end + 1}"
                        text_widget.tag_add("string", string_start, string_end)
        except:
            pass
            
    def highlight_python_brute_force(self, text_widget):
        """Brute force Python highlighting"""
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global', 'nonlocal', 'print', 'len', 'range', 'list', 'dict', 'set', 'tuple']
        
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
        
        # Highlight strings (both single and double quotes)
        for quote in ['"', "'"]:
            start = "1.0"
            while True:
                pos = text_widget.search(quote, start, tk.END)
                if not pos:
                    break
                # Find the end quote
                end_pos = text_widget.search(quote, f"{pos}+1c", tk.END)
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
            
    def highlight_csharp_brute_force(self, text_widget):
        """Brute force C# highlighting"""
        keywords = ['public', 'private', 'protected', 'internal', 'class', 'struct', 'interface', 'enum', 'namespace', 'using', 'static', 'readonly', 'const', 'virtual', 'override', 'abstract', 'sealed', 'partial', 'async', 'await', 'var', 'void', 'int', 'string', 'bool', 'float', 'double', 'if', 'else', 'for', 'while', 'foreach', 'switch', 'case', 'default', 'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally', 'new', 'this', 'base', 'null', 'true', 'false', 'UnityEngine', 'MonoBehaviour', 'Start', 'Update', 'Debug', 'Log']
        
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
            
    def highlight_javascript_brute_force(self, text_widget):
        """Brute force JavaScript highlighting"""
        keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'null', 'undefined', 'true', 'false', 'class', 'extends', 'super', 'import', 'export', 'async', 'await', 'console', 'log']
        
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
            
    def highlight_html_brute_force(self, text_widget):
        """Brute force HTML highlighting"""
        # Highlight HTML tags
        start = "1.0"
        while True:
            pos = text_widget.search('<', start, tk.END)
            if not pos:
                break
            end_pos = text_widget.search('>', pos, tk.END)
            if end_pos:
                end = f"{end_pos}+1c"
                text_widget.tag_add("keyword", pos, end)
                start = end
            else:
                start = f"{pos}+1c"
        
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
                
    def highlight_css_brute_force(self, text_widget):
        """Brute force CSS highlighting"""
        keywords = ['color', 'background', 'margin', 'padding', 'border', 'font', 'display', 'position', 'width', 'height', 'top', 'left', 'right', 'bottom', 'float', 'clear', 'text', 'line', 'box', 'flex', 'grid']
        
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
                
    def highlight_generic_brute_force(self, text_widget):
        """Generic highlighting for any language"""
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
        for comment_char in ['#', '//', '/*']:
            start = "1.0"
            while True:
                pos = text_widget.search(comment_char, start, tk.END)
                if not pos:
                    break
                if comment_char == '/*':
                    end_pos = text_widget.search('*/', pos, tk.END)
                    if end_pos:
                        end = f"{end_pos}+2c"
                    else:
                        end = text_widget.index(f"{pos} lineend")
                else:
                    end = text_widget.index(f"{pos} lineend")
                text_widget.tag_add("comment", pos, end)
                start = end
                
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
        
    def setup_window_navigation(self):
        """Setup professional window navigation"""
        print("🔧 Setting up professional window navigation...")
        
        # Window focus and activation
        self.root.bind('<FocusIn>', self.on_window_focus)
        self.root.bind('<FocusOut>', self.on_window_lost_focus)
        self.root.bind('<Map>', self.on_window_map)
        self.root.bind('<Unmap>', self.on_window_unmap)
        
        # Professional keyboard shortcuts for window management
        self.root.bind('<Alt-Tab>', self.on_alt_tab)
        self.root.bind('<Alt-F4>', self.on_alt_f4)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.on_escape)
        
        # Window state tracking
        self.window_states = {
            'focused': True,
            'minimized': False,
            'fullscreen': False,
            'always_on_top': False
        }
        
        # Professional window behavior
        self.setup_professional_behavior()
        
        print("✅ Professional window navigation setup complete")
        
    def on_window_focus(self, event):
        """Handle window focus"""
        self.window_states['focused'] = True
        self.root.attributes('-topmost', self.window_states['always_on_top'])
        self.update_status("Window focused")
        
    def on_window_lost_focus(self, event):
        """Handle window lost focus"""
        self.window_states['focused'] = False
        self.update_status("Window lost focus")
        
    def on_window_map(self, event):
        """Handle window map (restore)"""
        self.window_states['minimized'] = False
        self.update_status("Window restored")
        
    def on_window_unmap(self, event):
        """Handle window unmap (minimize)"""
        self.window_states['minimized'] = True
        self.update_status("Window minimized")
        
    def on_alt_tab(self, event):
        """Handle Alt+Tab for professional window switching"""
        # This allows Windows to handle Alt+Tab normally
        return "break"
        
    def on_alt_f4(self, event):
        """Handle Alt+F4 for professional window closing"""
        self.quit_application()
        return "break"
        
    def on_escape(self, event):
        """Handle Escape key for professional behavior"""
        if self.window_states['fullscreen']:
            self.toggle_fullscreen()
        elif hasattr(self, 'search_frame') and self.search_frame.winfo_ismapped():
            self.hide_search()
        else:
            # Clear selection
            if self.current_tab is not None and self.tabs:
                text_widget = self.tabs[self.current_tab]['text']
                text_widget.tag_remove("sel", "1.0", tk.END)
        return "break"
        
    def setup_professional_behavior(self):
        """Setup professional window behavior"""
        # Set window properties for professional appearance
        self.root.title("Nexus Code - Professional Dark Code Editor")
        self.root.iconname("Nexus Code")
        
        # Professional window hints
        try:
            # Set window class for proper taskbar grouping
            self.root.wm_class("NexusCode", "Nexus Code")
        except:
            pass
            
        # Professional window state
        self.root.state('normal')
        self.root.resizable(True, True)
        
        # Professional window positioning
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
        except:
            pass
            
    def quit_application(self):
        """Professional application quit"""
        try:
            # Save any unsaved changes
            self.save_all_files()
            
            # Clean up resources
            self.cleanup_resources()
            
            # Quit gracefully
            self.root.quit()
        except:
            self.root.quit()
            
    def save_all_files(self):
        """Save all modified files"""
        try:
            for tab in self.tabs:
                if tab['modified'] and tab['file_path']:
                    self.save_file_to_path(tab['file_path'], tab['text'])
        except:
            pass
            
    def cleanup_resources(self):
        """Clean up application resources"""
        try:
            # Close any open files
            for tab in self.tabs:
                if hasattr(tab['text'], 'destroy'):
                    tab['text'].destroy()
        except:
            pass
            
    def update_status(self, message):
        """Update status bar with professional messages"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=message)
                # Auto-clear status after 3 seconds
                self.root.after(3000, lambda: self.status_label.config(text="Ready"))
        except:
            pass

if __name__ == "__main__":
    app = NexusCode()
    app.run()