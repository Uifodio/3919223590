#!/usr/bin/env python3
"""
Anora Editor - Professional Code Editor
Built with wxPython for extreme professionalism and native Windows integration
"""

import wx
import wx.stc as stc
import wx.aui
import wx.adv
import wx.html
import wx.grid
import wx.richtext
import os
import sys
import traceback
import re
import time
import threading
import subprocess
import platform
import json
import pickle
import glob
import shutil
from pathlib import Path
from datetime import datetime

# Windows-specific imports
try:
    import winreg
    import win32gui
    import win32con
    import win32api
    import win32clipboard
    import ctypes
    from ctypes import windll, wintypes
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    print("⚠️ Windows-specific features not available")

# Additional imports for advanced features
try:
    import pygments
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False
    print("⚠️ Pygments not available - using built-in highlighting")

class AnoraEditor(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Anora Editor - Professional Code Editor", 
                        size=(1400, 900))
        
        # Set up the main frame
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # Initialize variables
        self.current_file = None
        self.modified = False
        self.files = []
        self.recent_files = []
        self.window_states = {}
        self.drag_in_progress = False
        self.drag_start = None
        
        # Advanced features from previous version
        self.always_on_top = False
        self.fullscreen_mode = False
        self.line_numbers_visible = True
        self.word_wrap_enabled = False
        self.auto_save_enabled = True
        self.auto_save_interval = 30000  # 30 seconds
        self.last_auto_save = time.time()
        self.undo_history = []
        self.redo_history = []
        self.max_undo_steps = 100
        self.clipboard_history = []
        self.max_clipboard_items = 10
        self.file_watchers = {}
        self.external_changes = {}
        self.last_external_check = time.time()
        self.external_check_interval = 2000  # 2 seconds
        
        # Windows-specific features
        self.windows_drag_drop_enabled = WINDOWS_AVAILABLE
        self.windows_file_associations = {}
        self.windows_registry_entries = {}
        self.windows_clipboard_monitor = None
        self.windows_file_system_watcher = None
        
        # Professional features
        self.settings = {
            'theme': 'dark',
            'font_size': 10,
            'font_family': 'Consolas',
            'tab_width': 4,
            'line_numbers': True,
            'word_wrap': False,
            'auto_save': True,
            'auto_save_interval': 30,
            'syntax_highlighting': True,
            'bracket_matching': True,
            'auto_indent': True,
            'show_whitespace': False,
            'show_line_endings': False,
            'right_margin': 80,
            'always_on_top': False,
            'fullscreen': False,
            'recent_files_count': 10,
            'undo_steps': 100,
            'clipboard_history_size': 10
        }
        
        # Create the UI
        self.create_ui()
        
        # Set up native drag and drop
        self.setup_drag_drop()
        
        # Set up syntax highlighting
        self.setup_syntax_highlighting()
        
        # Set up professional window behavior
        self.setup_professional_behavior()
        
        # Set up advanced features
        self.setup_advanced_features()
        
        # Set up Windows-specific features
        if WINDOWS_AVAILABLE:
            self.setup_windows_features()
        
        # Set up auto-save timer
        self.setup_auto_save()
        
        # Set up file monitoring
        self.setup_file_monitoring()
        
        # Set up clipboard monitoring
        self.setup_clipboard_monitoring()
        
        # Center the window
        self.Center()
        
        # Bind events
        self.bind_events()
        
        # Load recent files
        self.load_recent_files()
        
        # Load settings
        self.load_settings()
        
        print("🔥 Anora Editor - Professional Code Editor Started!")
        
    def create_ui(self):
        """Create the user interface"""
        # Create main panel
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(30, 30, 30))
        
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        
        # Create search panel (hidden by default)
        self.create_search_panel()
        main_sizer.Add(self.search_panel, 0, wx.EXPAND)
        self.search_panel.Hide()
        
        # Create notebook for tabs
        self.notebook = wx.aui.AuiNotebook(self.panel, style=wx.aui.AUI_NB_TOP | 
                                         wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_TAB_MOVE |
                                         wx.aui.AUI_NB_SCROLL_BUTTONS | wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
        self.notebook.SetArtProvider(wx.aui.AuiDefaultTabArt())
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        
        # Create status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready")
        
        # Set the main sizer
        self.panel.SetSizer(main_sizer)
        
        # Create initial tab
        self.create_new_tab()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N", "Create a new file")
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open an existing file")
        file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S", "Save the current file")
        file_menu.Append(wx.ID_SAVEAS, "Save &As...\tCtrl+Shift+S", "Save file with a new name")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")
        menubar.Append(file_menu, "&File")
        
        # Edit menu
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_UNDO, "&Undo\tCtrl+Z", "Undo the last action")
        edit_menu.Append(wx.ID_REDO, "&Redo\tCtrl+Y", "Redo the last action")
        edit_menu.AppendSeparator()
        edit_menu.Append(wx.ID_CUT, "Cu&t\tCtrl+X", "Cut selected text")
        edit_menu.Append(wx.ID_COPY, "&Copy\tCtrl+C", "Copy selected text")
        edit_menu.Append(wx.ID_PASTE, "&Paste\tCtrl+V", "Paste text")
        edit_menu.AppendSeparator()
        edit_menu.Append(wx.ID_SELECTALL, "Select &All\tCtrl+A", "Select all text")
        menubar.Append(edit_menu, "&Edit")
        
        # Search menu
        search_menu = wx.Menu()
        # Custom IDs for Find Next/Previous (wx has no wx.ID_FINDNEXT/PREV)
        self.id_find_next = wx.NewIdRef()
        self.id_find_prev = wx.NewIdRef()
        search_menu.Append(wx.ID_FIND, "&Find\tCtrl+F", "Find text")
        search_menu.Append(wx.ID_REPLACE, "&Replace\tCtrl+H", "Replace text")
        search_menu.Append(self.id_find_next, "Find &Next\tF3", "Find next occurrence")
        search_menu.Append(self.id_find_prev, "Find &Previous\tShift+F3", "Find previous occurrence")
        menubar.Append(search_menu, "&Search")
        
        # View menu
        view_menu = wx.Menu()
        self.fullscreen_item = view_menu.Append(wx.ID_ANY, "&Fullscreen\tF11", "Toggle fullscreen mode")
        self.always_on_top_item = view_menu.Append(wx.ID_ANY, "Always on &Top", "Keep window on top")
        view_menu.AppendSeparator()
        view_menu.Append(wx.ID_ANY, "&Line Numbers", "Toggle line numbers")
        view_menu.Append(wx.ID_ANY, "&Word Wrap", "Toggle word wrap")
        menubar.Append(view_menu, "&View")
        
        # Tools menu
        tools_menu = wx.Menu()
        tools_menu.Append(wx.ID_ANY, "&Settings", "Open settings")
        tools_menu.Append(wx.ID_ANY, "&Plugins", "Manage plugins")
        menubar.Append(tools_menu, "&Tools")
        
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About", "About Anora Editor")
        help_menu.Append(wx.ID_HELP, "&Help\tF1", "Show help")
        menubar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menubar)
        
    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar = wx.ToolBar(self.panel, style=wx.TB_FLAT | wx.TB_HORIZONTAL)
        self.toolbar.SetBackgroundColour(wx.Colour(45, 45, 48))
        self.toolbar.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # New file button
        new_btn = self.toolbar.AddTool(wx.ID_NEW, "New", 
                                     wx.ArtProvider.GetBitmap(wx.ART_NEW))
        
        # Open file button
        open_btn = self.toolbar.AddTool(wx.ID_OPEN, "Open", 
                                      wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        
        # Save button
        save_btn = self.toolbar.AddTool(wx.ID_SAVE, "Save", 
                                      wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
        
        self.toolbar.AddSeparator()
        
        # Search button
        search_btn = self.toolbar.AddTool(wx.ID_FIND, "Find", 
                                        wx.ArtProvider.GetBitmap(wx.ART_FIND))
        
        # Replace button
        replace_btn = self.toolbar.AddTool(wx.ID_REPLACE, "Replace", 
                                         wx.ArtProvider.GetBitmap(wx.ART_REPLACE))
        
        self.toolbar.AddSeparator()
        
        # Fullscreen button
        fullscreen_btn = self.toolbar.AddTool(wx.ID_ANY, "Fullscreen", 
                                            wx.ArtProvider.GetBitmap(wx.ART_FULL_SCREEN))
        
        # Always on top button
        top_btn = self.toolbar.AddTool(wx.ID_ANY, "Always on Top", 
                                     wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
        
        # Pin button
        pin_btn = self.toolbar.AddTool(wx.ID_ANY, "Pin", 
                                     wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK))
        
        self.toolbar.Realize()
        
    def create_search_panel(self):
        """Create the search panel"""
        self.search_panel = wx.Panel(self.panel)
        self.search_panel.SetBackgroundColour(wx.Colour(45, 45, 48))
        
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Find label and text
        find_label = wx.StaticText(self.search_panel, label="Find:")
        find_label.SetForegroundColour(wx.Colour(212, 212, 212))
        self.find_input = wx.TextCtrl(self.search_panel, style=wx.TE_PROCESS_ENTER)
        self.find_input.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.find_input.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # Replace label and text
        replace_label = wx.StaticText(self.search_panel, label="Replace:")
        replace_label.SetForegroundColour(wx.Colour(212, 212, 212))
        self.replace_input = wx.TextCtrl(self.search_panel, style=wx.TE_PROCESS_ENTER)
        self.replace_input.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.replace_input.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # Buttons
        find_btn = wx.Button(self.search_panel, label="Find")
        find_btn.SetBackgroundColour(wx.Colour(0, 120, 215))
        find_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        
        replace_btn = wx.Button(self.search_panel, label="Replace")
        replace_btn.SetBackgroundColour(wx.Colour(0, 120, 215))
        replace_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        
        replace_all_btn = wx.Button(self.search_panel, label="Replace All")
        replace_all_btn.SetBackgroundColour(wx.Colour(0, 120, 215))
        replace_all_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        
        close_btn = wx.Button(self.search_panel, label="✕")
        close_btn.SetBackgroundColour(wx.Colour(60, 60, 60))
        close_btn.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # Add to sizer
        search_sizer.Add(find_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        search_sizer.Add(self.find_input, 1, wx.EXPAND | wx.ALL, 5)
        search_sizer.Add(replace_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        search_sizer.Add(self.replace_input, 1, wx.EXPAND | wx.ALL, 5)
        search_sizer.Add(find_btn, 0, wx.ALL, 5)
        search_sizer.Add(replace_btn, 0, wx.ALL, 5)
        search_sizer.Add(replace_all_btn, 0, wx.ALL, 5)
        search_sizer.Add(close_btn, 0, wx.ALL, 5)
        
        self.search_panel.SetSizer(search_sizer)
        
        # Bind events
        close_btn.Bind(wx.EVT_BUTTON, self.hide_search_panel)
        find_btn.Bind(wx.EVT_BUTTON, self.cmd_find)
        replace_btn.Bind(wx.EVT_BUTTON, self.cmd_replace)
        replace_all_btn.Bind(wx.EVT_BUTTON, self.cmd_replace_all)
        
    def create_new_tab(self, file_path=None):
        """Create a new tab with a text editor"""
        # Create the text editor
        editor = stc.StyledTextCtrl(self.notebook, style=wx.BORDER_NONE)
        
        # Set up the editor appearance
        self.setup_editor_style(editor)
        
        # Load file if provided
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                editor.SetText(content)
                self.current_file = file_path
                tab_title = os.path.basename(file_path)
                self.apply_syntax_highlighting(editor, file_path)
                self.add_recent_file(file_path)
            except Exception as e:
                print(f"Error loading file: {e}")
                tab_title = "Untitled"
                self.current_file = None
        else:
            tab_title = "Untitled"
            self.current_file = None
        
        # Add the tab
        self.notebook.AddPage(editor, tab_title, True)
        
        # Bind editor events
        editor.Bind(stc.EVT_STC_CHANGE, self.on_text_change)
        editor.Bind(stc.EVT_STC_SAVEPOINTREACHED, self.on_save_point)
        editor.Bind(stc.EVT_STC_SAVEPOINTLEFT, self.on_save_point_left)
        
        return editor
        
    def setup_editor_style(self, editor):
        """Set up the editor styling"""
        # Set colors
        editor.StyleSetBackground(stc.STC_STYLE_DEFAULT, wx.Colour(30, 30, 30))
        editor.StyleSetForeground(stc.STC_STYLE_DEFAULT, wx.Colour(212, 212, 212))
        editor.StyleClearAll()
        
        # Set font
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        editor.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
        
        # Set margin
        editor.SetMarginWidth(1, 50)
        editor.StyleSetBackground(1, wx.Colour(45, 45, 48))
        editor.StyleSetForeground(1, wx.Colour(150, 150, 150))
        
        # Enable line numbers
        editor.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        
        # Set selection color
        editor.SetSelBackground(True, wx.Colour(51, 153, 255))
        editor.SetSelForeground(True, wx.Colour(255, 255, 255))
        
        # Set caret color
        editor.SetCaretForeground(wx.Colour(212, 212, 212))
        editor.SetCaretWidth(2)
        
        # Set edge line
        editor.SetEdgeMode(stc.STC_EDGE_LINE)
        editor.SetEdgeColumn(80)
        editor.SetEdgeColour(wx.Colour(60, 60, 60))
        
        # Enable auto-indent
        editor.SetUseTabs(False)
        editor.SetTabWidth(4)
        editor.SetIndent(4)
        editor.SetUseHorizontalScrollBar(True)
        editor.SetUseVerticalScrollBar(True)
        
    def setup_syntax_highlighting(self):
        """Set up syntax highlighting"""
        # Define syntax highlighting styles
        self.syntax_styles = {
            'keyword': (wx.Colour(86, 156, 214), wx.Colour(30, 30, 30)),
            'string': (wx.Colour(214, 157, 133), wx.Colour(30, 30, 30)),
            'comment': (wx.Colour(87, 166, 74), wx.Colour(30, 30, 30)),
            'number': (wx.Colour(181, 206, 168), wx.Colour(30, 30, 30)),
            'function': (wx.Colour(220, 220, 170), wx.Colour(30, 30, 30)),
            'operator': (wx.Colour(180, 180, 180), wx.Colour(30, 30, 30)),
            'preprocessor': (wx.Colour(155, 155, 155), wx.Colour(30, 30, 30)),
        }
        
    def apply_syntax_highlighting(self, editor, file_path):
        """Apply syntax highlighting based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            self.setup_python_highlighting(editor)
        elif ext == '.cs':
            self.setup_csharp_highlighting(editor)
        elif ext == '.js':
            self.setup_javascript_highlighting(editor)
        elif ext == '.html':
            self.setup_html_highlighting(editor)
        elif ext == '.css':
            self.setup_css_highlighting(editor)
        elif ext == '.json':
            self.setup_json_highlighting(editor)
        elif ext == '.xml':
            self.setup_xml_highlighting(editor)
        elif ext in ['.cpp', '.c', '.h', '.hpp']:
            self.setup_cpp_highlighting(editor)
        else:
            self.setup_generic_highlighting(editor)
            
    def setup_python_highlighting(self, editor):
        """Set up Python syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_PYTHON)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_P_WORD, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_P_STRING, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_P_COMMENTLINE, self.syntax_styles['comment'][0])
        editor.StyleSetForeground(stc.STC_P_NUMBER, self.syntax_styles['number'][0])
        editor.StyleSetForeground(stc.STC_P_OPERATOR, self.syntax_styles['operator'][0])
        
    def setup_csharp_highlighting(self, editor):
        """Set up C# syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_CPP)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_C_WORD, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_C_STRING, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_C_COMMENTLINE, self.syntax_styles['comment'][0])
        editor.StyleSetForeground(stc.STC_C_NUMBER, self.syntax_styles['number'][0])
        editor.StyleSetForeground(stc.STC_C_OPERATOR, self.syntax_styles['operator'][0])
        
    def setup_javascript_highlighting(self, editor):
        """Set up JavaScript syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_CPP)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_C_WORD, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_C_STRING, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_C_COMMENTLINE, self.syntax_styles['comment'][0])
        editor.StyleSetForeground(stc.STC_C_NUMBER, self.syntax_styles['number'][0])
        editor.StyleSetForeground(stc.STC_C_OPERATOR, self.syntax_styles['operator'][0])
        
    def setup_html_highlighting(self, editor):
        """Set up HTML syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_HTML)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_H_TAG, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_H_ATTRIBUTE, self.syntax_styles['function'][0])
        editor.StyleSetForeground(stc.STC_H_VALUE, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_H_COMMENT, self.syntax_styles['comment'][0])
        
    def setup_css_highlighting(self, editor):
        """Set up CSS syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_CSS)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_CSS_TAG, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_CSS_CLASS, self.syntax_styles['function'][0])
        editor.StyleSetForeground(stc.STC_CSS_VALUE, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_CSS_COMMENT, self.syntax_styles['comment'][0])
        
    def setup_json_highlighting(self, editor):
        """Set up JSON syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_JSON)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_JSON_KEYWORD, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_JSON_STRING, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_JSON_NUMBER, self.syntax_styles['number'][0])
        editor.StyleSetForeground(stc.STC_JSON_OPERATOR, self.syntax_styles['operator'][0])
        
    def setup_xml_highlighting(self, editor):
        """Set up XML syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_XML)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_H_TAG, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_H_ATTRIBUTE, self.syntax_styles['function'][0])
        editor.StyleSetForeground(stc.STC_H_VALUE, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_H_COMMENT, self.syntax_styles['comment'][0])
        
    def setup_cpp_highlighting(self, editor):
        """Set up C++ syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_CPP)
        
        # Set styles
        editor.StyleSetForeground(stc.STC_C_WORD, self.syntax_styles['keyword'][0])
        editor.StyleSetForeground(stc.STC_C_STRING, self.syntax_styles['string'][0])
        editor.StyleSetForeground(stc.STC_C_COMMENTLINE, self.syntax_styles['comment'][0])
        editor.StyleSetForeground(stc.STC_C_NUMBER, self.syntax_styles['number'][0])
        editor.StyleSetForeground(stc.STC_C_OPERATOR, self.syntax_styles['operator'][0])
        
    def setup_generic_highlighting(self, editor):
        """Set up generic syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_NULL)
        
    def setup_drag_drop(self):
        """Set up native drag and drop"""
        # Enable file drop on the frame
        self.SetDropTarget(FileDropTarget(self))
        print("✅ Native drag and drop enabled")
        
    def setup_professional_behavior(self):
        """Set up professional window behavior"""
        # Set window properties
        self.SetTitle("Anora Editor - Professional Code Editor")
        self.SetIcon(wx.ArtProvider.GetIcon(wx.ART_FRAME_ICON))
        
        # Enable professional window hints
        try:
            # Set window class for proper taskbar grouping
            self.SetName("AnoraEditor")
        except:
            pass
            
    def setup_advanced_features(self):
        """Set up advanced features from previous version"""
        # Set up bracket matching
        self.setup_bracket_matching()
        
        # Set up auto-completion
        self.setup_auto_completion()
        
        # Set up code folding
        self.setup_code_folding()
        
        # Set up multiple cursors
        self.setup_multiple_cursors()
        
        # Set up minimap
        self.setup_minimap()
        
        print("✅ Advanced features initialized")
        
    def setup_windows_features(self):
        """Set up Windows-specific features"""
        # Set up Windows drag and drop
        self.setup_windows_drag_drop()
        
        # Set up file associations
        self.setup_file_associations()
        
        # Set up registry entries
        self.setup_registry_entries()
        
        # Set up clipboard monitoring
        self.setup_windows_clipboard_monitor()
        
        # Set up file system monitoring
        self.setup_windows_file_system_watcher()
        
        print("✅ Windows-specific features initialized")
        
    def setup_auto_save(self):
        """Set up auto-save functionality"""
        if self.settings['auto_save']:
            self.auto_save_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_auto_save, self.auto_save_timer)
            self.auto_save_timer.Start(self.settings['auto_save_interval'] * 1000)
            print("✅ Auto-save enabled")
            
    def setup_file_monitoring(self):
        """Set up file monitoring for external changes"""
        self.file_monitor_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_external_changes, self.file_monitor_timer)
        self.file_monitor_timer.Start(self.external_check_interval)
        print("✅ File monitoring enabled")
        
    def setup_clipboard_monitoring(self):
        """Set up clipboard monitoring"""
        self.clipboard_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.check_clipboard_changes, self.clipboard_timer)
        self.clipboard_timer.Start(1000)  # Check every second
        print("✅ Clipboard monitoring enabled")
        
    def setup_bracket_matching(self):
        """Set up bracket matching"""
        # This will be implemented in the editor setup
        pass
        
    def setup_auto_completion(self):
        """Set up auto-completion"""
        # This will be implemented in the editor setup
        pass
        
    def setup_code_folding(self):
        """Set up code folding"""
        # This will be implemented in the editor setup
        pass
        
    def setup_multiple_cursors(self):
        """Set up multiple cursors"""
        # This will be implemented in the editor setup
        pass
        
    def setup_minimap(self):
        """Set up minimap"""
        # This will be implemented in the editor setup
        pass
        
    def setup_windows_drag_drop(self):
        """Set up Windows-specific drag and drop"""
        if WINDOWS_AVAILABLE:
            try:
                # Enable Windows drag and drop
                windll.shell32.DragAcceptFiles(self.GetHandle(), True)
                print("✅ Windows drag and drop enabled")
            except:
                print("⚠️ Windows drag and drop not available")
                
    def setup_file_associations(self):
        """Set up file associations"""
        if WINDOWS_AVAILABLE:
            try:
                # Register file associations
                extensions = ['.py', '.cs', '.js', '.html', '.css', '.json', '.xml', '.cpp', '.c', '.h', '.hpp']
                for ext in extensions:
                    self.register_file_association(ext)
                print("✅ File associations set up")
            except:
                print("⚠️ File associations not available")
                
    def setup_registry_entries(self):
        """Set up registry entries"""
        if WINDOWS_AVAILABLE:
            try:
                # Register in Windows registry
                self.register_in_registry()
                print("✅ Registry entries created")
            except:
                print("⚠️ Registry entries not available")
                
    def setup_windows_clipboard_monitor(self):
        """Set up Windows clipboard monitoring"""
        if WINDOWS_AVAILABLE:
            try:
                # Start clipboard monitoring thread
                self.clipboard_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
                self.clipboard_thread.start()
                print("✅ Windows clipboard monitoring enabled")
            except:
                print("⚠️ Windows clipboard monitoring not available")
                
    def setup_windows_file_system_watcher(self):
        """Set up Windows file system watcher"""
        if WINDOWS_AVAILABLE:
            try:
                # Start file system monitoring thread
                self.fs_watcher_thread = threading.Thread(target=self.monitor_file_system, daemon=True)
                self.fs_watcher_thread.start()
                print("✅ Windows file system monitoring enabled")
            except:
                print("⚠️ Windows file system monitoring not available")
            
    def bind_events(self):
        """Bind all events"""
        # Menu events
        self.Bind(wx.EVT_MENU, self.on_new, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_save_as, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_undo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_MENU, self.on_redo, id=wx.ID_REDO)
        self.Bind(wx.EVT_MENU, self.on_cut, id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, self.on_copy, id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, self.on_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, self.on_select_all, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_replace, id=wx.ID_REPLACE)
        self.Bind(wx.EVT_MENU, self.on_find_next, id=self.id_find_next)
        self.Bind(wx.EVT_MENU, self.on_find_prev, id=self.id_find_prev)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_help, id=wx.ID_HELP)
        
        # Toolbar events
        self.toolbar.Bind(wx.EVT_TOOL, self.on_new, id=wx.ID_NEW)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_open, id=wx.ID_OPEN)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_save, id=wx.ID_SAVE)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_find, id=wx.ID_FIND)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_replace, id=wx.ID_REPLACE)
        
        # Notebook events
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_tab_changed)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_tab_close)
        
        # Window events
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_MOVE, self.on_move)
        
        # Keyboard shortcuts
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Advanced event handlers
        self.Bind(wx.EVT_TIMER, self.on_auto_save, self.auto_save_timer)
        self.Bind(wx.EVT_TIMER, self.check_external_changes, self.file_monitor_timer)
        self.Bind(wx.EVT_TIMER, self.check_clipboard_changes, self.clipboard_timer)
        
        # Window events
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)
        self.Bind(wx.EVT_ICONIZE, self.on_iconize)
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)
        self.Bind(wx.EVT_RESTORE, self.on_restore)
        
        # Advanced keyboard shortcuts
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        
    def on_text_change(self, event):
        """Handle text change events"""
        self.modified = True
        self.update_title()
        self.update_status("Modified")
        event.Skip()
        
    def on_save_point(self, event):
        """Handle save point reached"""
        self.modified = False
        self.update_title()
        self.update_status("Saved")
        event.Skip()
        
    def on_save_point_left(self, event):
        """Handle save point left"""
        self.modified = True
        self.update_title()
        self.update_status("Modified")
        event.Skip()
        
    def on_new(self, event):
        """Create a new file"""
        self.create_new_tab()
        
    def on_open(self, event):
        """Open a file"""
        with wx.FileDialog(self, "Open file", wildcard="All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            paths = fileDialog.GetPaths()
            for pathname in paths:
                self.open_file(pathname)
                
    def open_file(self, file_path):
        """Open a file in a new tab"""
        if os.path.exists(file_path):
            self.create_new_tab(file_path)
            
    def on_save(self, event):
        """Save the current file"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        if not self.current_file:
            self.on_save_as(event)
        else:
            self.save_file(current_editor, self.current_file)
            
    def on_save_as(self, event):
        """Save file as"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        with wx.FileDialog(self, "Save file", wildcard="All files (*.*)|*.*",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            self.save_file(current_editor, pathname)
            
    def save_file(self, editor, file_path):
        """Save file content"""
        try:
            content = editor.GetText()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = file_path
            self.modified = False
            self.update_title()
            self.add_recent_file(file_path)
            
            # Update tab title
            current_page = self.notebook.GetSelection()
            if current_page >= 0:
                self.notebook.SetPageText(current_page, os.path.basename(file_path))
                
            self.update_status(f"Saved: {file_path}")
            
        except Exception as e:
            wx.MessageBox(f"Error saving file: {e}", "Error", wx.OK | wx.ICON_ERROR)
            
    def on_find(self, event):
        """Show find dialog"""
        self.show_search_panel()
        
    def on_replace(self, event):
        """Show replace dialog"""
        self.show_search_panel()
        
    def on_find_next(self, event):
        """Find next occurrence"""
        self.cmd_find()
        
    def on_find_prev(self, event):
        """Find previous occurrence"""
        self.cmd_find(forward=False)
        
    def show_search_panel(self):
        """Show the search panel"""
        self.search_panel.Show()
        self.Layout()
        self.find_input.SetFocus()
        
    def hide_search_panel(self, event=None):
        """Hide the search panel"""
        self.search_panel.Hide()
        self.Layout()
        
    def cmd_find(self, event=None, forward=True):
        """Find text in the current editor"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        search_text = self.find_input.GetValue()
        if not search_text:
            return
            
        # Get current position
        current_pos = current_editor.GetCurrentPos()
        
        if forward:
            # Search forward
            pos = current_editor.FindText(current_pos, current_editor.GetLength(), search_text)
            if pos == -1:
                # Wrap around to beginning
                pos = current_editor.FindText(0, current_pos, search_text)
        else:
            # Search backward
            pos = current_editor.FindText(0, current_pos, search_text, stc.STC_FINDREV)
            if pos == -1:
                # Wrap around to end
                pos = current_editor.FindText(current_pos, current_editor.GetLength(), search_text, stc.STC_FINDREV)
                
        if pos != -1:
            current_editor.SetSelection(pos, pos + len(search_text))
            current_editor.ScrollToLine(current_editor.LineFromPosition(pos))
            self.update_status(f"Found at position {pos}")
        else:
            self.update_status("Text not found")
            
    def cmd_replace(self, event=None):
        """Replace current occurrence"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        search_text = self.find_input.GetValue()
        replace_text = self.replace_input.GetValue()
        
        if not search_text:
            return
            
        # Get current selection
        start, end = current_editor.GetSelection()
        selected_text = current_editor.GetTextRange(start, end)
        
        if selected_text == search_text:
            current_editor.Replace(start, end, replace_text)
            self.cmd_find()  # Find next occurrence
        else:
            self.cmd_find()  # Find first occurrence
            
    def cmd_replace_all(self, event=None):
        """Replace all occurrences"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        search_text = self.find_input.GetValue()
        replace_text = self.replace_input.GetValue()
        
        if not search_text:
            return
            
        # Replace all occurrences
        current_editor.BeginUndoAction()
        
        pos = 0
        count = 0
        while True:
            pos = current_editor.FindText(pos, current_editor.GetLength(), search_text)
            if pos == -1:
                break
            current_editor.Replace(pos, pos + len(search_text), replace_text)
            pos += len(replace_text)
            count += 1
            
        current_editor.EndUndoAction()
        self.update_status(f"Replaced {count} occurrences")
        
    def on_tab_changed(self, event):
        """Handle tab change"""
        current_page = self.notebook.GetSelection()
        if current_page >= 0:
            editor = self.notebook.GetPage(current_page)
            # Update current file and status
            self.update_status(f"Tab {current_page + 1}")
        event.Skip()
        
    def on_tab_close(self, event):
        """Handle tab close"""
        # Check if file is modified and ask to save
        current_page = event.GetSelection()
        if current_page >= 0:
            editor = self.notebook.GetPage(current_page)
            if editor.GetModify():
                result = wx.MessageBox("Save changes before closing?", "Save Changes",
                                     wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
                if result == wx.YES:
                    self.on_save(None)
                elif result == wx.CANCEL:
                    event.Veto()
                    return
        event.Skip()
        
    def on_close(self, event):
        """Handle window close"""
        # Check for unsaved changes
        if self.modified:
            result = wx.MessageBox("Save changes before closing?", "Save Changes",
                                 wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            if result == wx.YES:
                self.on_save(None)
            elif result == wx.CANCEL:
                return
                
        self.save_recent_files()
        self.Destroy()
        
    def on_resize(self, event):
        """Handle window resize"""
        event.Skip()
        
    def on_move(self, event):
        """Handle window move"""
        event.Skip()
        
    def on_key_down(self, event):
        """Handle keyboard shortcuts"""
        key = event.GetKeyCode()
        
        if key == wx.WXK_F11:
            self.toggle_fullscreen()
        elif key == wx.WXK_ESCAPE:
            if self.search_panel.IsShown():
                self.hide_search_panel()
            else:
                # Clear selection
                current_editor = self.get_current_editor()
                if current_editor:
                    current_editor.SetSelection(current_editor.GetCurrentPos(), current_editor.GetCurrentPos())
        else:
            event.Skip()
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.IsFullScreen():
            self.ShowFullScreen(False)
        else:
            self.ShowFullScreen(True)
            
    def get_current_editor(self):
        """Get the current editor"""
        current_page = self.notebook.GetSelection()
        if current_page >= 0:
            return self.notebook.GetPage(current_page)
        return None
        
    def update_title(self):
        """Update the window title"""
        title = "Anora Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.modified:
            title += " *"
        self.SetTitle(title)
        
    def update_status(self, message):
        """Update the status bar"""
        self.status_bar.SetStatusText(message)
        
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        
    def load_recent_files(self):
        """Load recent files from file"""
        try:
            if os.path.exists('recent_files.txt'):
                with open('recent_files.txt', 'r') as f:
                    self.recent_files = [line.strip() for line in f.readlines()]
        except:
            self.recent_files = []
            
    def save_recent_files(self):
        """Save recent files to file"""
        try:
            with open('recent_files.txt', 'w') as f:
                for file_path in self.recent_files:
                    f.write(f"{file_path}\n")
        except:
            pass
            
    def on_file_dropped(self, file_path):
        """Handle file drop"""
        print(f"🔥 File dropped: {file_path}")
        if os.path.exists(file_path):
            self.open_file(file_path)
            self.update_status(f"Opened: {file_path}")
            
    # Menu action handlers
    def on_exit(self, event):
        """Exit the application"""
        self.Close()
        
    def on_undo(self, event):
        """Undo action"""
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.Undo()
            
    def on_redo(self, event):
        """Redo action"""
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.Redo()
            
    def on_cut(self, event):
        """Cut action"""
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.Cut()
            
    def on_copy(self, event):
        """Copy action"""
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.Copy()
            
    def on_paste(self, event):
        """Paste action"""
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.Paste()
            
    def on_select_all(self, event):
        """Select all action"""
        current_editor = self.get_current_editor()
        if current_editor:
            current_editor.SelectAll()
            
    def on_about(self, event):
        """Show about dialog"""
        wx.MessageBox("Anora Editor\nProfessional Code Editor\nBuilt with wxPython\n\nVersion 1.0", 
                     "About Anora Editor", wx.OK | wx.ICON_INFORMATION)
                     
    def on_help(self, event):
        """Show help"""
        wx.MessageBox("Anora Editor Help\n\n"
                     "File Operations:\n"
                     "Ctrl+N - New file\n"
                     "Ctrl+O - Open file\n"
                     "Ctrl+S - Save file\n"
                     "Ctrl+Shift+S - Save as\n\n"
                     "Editing:\n"
                     "Ctrl+Z - Undo\n"
                     "Ctrl+Y - Redo\n"
                     "Ctrl+X - Cut\n"
                     "Ctrl+C - Copy\n"
                     "Ctrl+V - Paste\n"
                     "Ctrl+A - Select all\n\n"
                     "Search:\n"
                     "Ctrl+F - Find\n"
                     "Ctrl+H - Replace\n"
                     "F3 - Find next\n"
                     "Shift+F3 - Find previous\n\n"
                     "View:\n"
                     "F11 - Toggle fullscreen\n"
                     "Escape - Clear selection\n\n"
                     "Drag and drop files from Windows Explorer to open them!",
                     "Help", wx.OK | wx.ICON_INFORMATION)
                     
    # Advanced features from previous version
    def on_auto_save(self, event):
        """Handle auto-save"""
        if self.settings['auto_save'] and self.modified and self.current_file:
            current_editor = self.get_current_editor()
            if current_editor:
                self.save_file(current_editor, self.current_file)
                self.update_status("Auto-saved")
                
    def check_external_changes(self, event):
        """Check for external file changes"""
        current_time = time.time()
        if current_time - self.last_external_check > self.external_check_interval / 1000:
            self.last_external_check = current_time
            
            for file_path in self.files:
                if os.path.exists(file_path):
                    try:
                        current_mtime = os.path.getmtime(file_path)
                        if file_path in self.external_changes:
                            if current_mtime > self.external_changes[file_path]:
                                self.notify_external_change(file_path)
                        self.external_changes[file_path] = current_mtime
                    except:
                        pass
                        
    def check_clipboard_changes(self, event):
        """Check for clipboard changes"""
        try:
            if WINDOWS_AVAILABLE:
                current_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                if current_clipboard and current_clipboard not in self.clipboard_history:
                    self.clipboard_history.append(current_clipboard)
                    if len(self.clipboard_history) > self.max_clipboard_items:
                        self.clipboard_history.pop(0)
        except:
            pass
            
    def notify_external_change(self, file_path):
        """Notify user of external file change"""
        result = wx.MessageBox(f"File '{os.path.basename(file_path)}' has been modified externally.\nReload?", 
                             "External Change", wx.YES_NO | wx.ICON_QUESTION)
        if result == wx.YES:
            self.reload_file(file_path)
            
    def reload_file(self, file_path):
        """Reload file from disk"""
        current_editor = self.get_current_editor()
        if current_editor and self.current_file == file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                current_editor.SetText(content)
                self.modified = False
                self.update_title()
                self.update_status(f"Reloaded: {file_path}")
            except Exception as e:
                wx.MessageBox(f"Error reloading file: {e}", "Error", wx.OK | wx.ICON_ERROR)
                
    def on_activate(self, event):
        """Handle window activation"""
        event.Skip()
        
    def on_iconize(self, event):
        """Handle window iconize"""
        event.Skip()
        
    def on_maximize(self, event):
        """Handle window maximize"""
        event.Skip()
        
    def on_restore(self, event):
        """Handle window restore"""
        event.Skip()
        
    def on_char_hook(self, event):
        """Handle advanced keyboard shortcuts"""
        key = event.GetKeyCode()
        modifiers = event.GetModifiers()
        
        # Ctrl+Shift+O - Open folder
        if key == ord('O') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.open_folder()
        # Ctrl+Shift+S - Save all
        elif key == ord('S') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.save_all_files()
        # Ctrl+Shift+N - New window
        elif key == ord('N') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.new_window()
        # Ctrl+Shift+W - Close all
        elif key == ord('W') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.close_all_files()
        # Ctrl+Shift+T - Reopen closed tab
        elif key == ord('T') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.reopen_closed_tab()
        # Ctrl+Shift+L - Select all occurrences
        elif key == ord('L') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.select_all_occurrences()
        # Ctrl+Shift+K - Delete line
        elif key == ord('K') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.delete_line()
        # Ctrl+Shift+D - Duplicate line
        elif key == ord('D') and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.duplicate_line()
        # Ctrl+Shift+Up - Move line up
        elif key == wx.WXK_UP and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.move_line_up()
        # Ctrl+Shift+Down - Move line down
        elif key == wx.WXK_DOWN and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.move_line_down()
        # Ctrl+Shift+Enter - Insert line above
        elif key == wx.WXK_RETURN and modifiers == wx.MOD_CONTROL | wx.MOD_SHIFT:
            self.insert_line_above()
        # Ctrl+Enter - Insert line below
        elif key == wx.WXK_RETURN and modifiers == wx.MOD_CONTROL:
            self.insert_line_below()
        else:
            event.Skip()
            
    def open_folder(self):
        """Open folder in new tabs"""
        with wx.DirDialog(self, "Select folder") as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                folder_path = dirDialog.GetPath()
                self.open_folder_files(folder_path)
                
    def open_folder_files(self, folder_path):
        """Open all files in folder"""
        extensions = ['.py', '.cs', '.js', '.html', '.css', '.json', '.xml', '.cpp', '.c', '.h', '.hpp', '.txt']
        for ext in extensions:
            for file_path in glob.glob(os.path.join(folder_path, f"*{ext}")):
                self.open_file(file_path)
                
    def save_all_files(self):
        """Save all open files"""
        for i in range(self.notebook.GetPageCount()):
            editor = self.notebook.GetPage(i)
            if editor.GetModify():
                # Get file path for this tab
                # This would need to be tracked per tab
                pass
                
    def new_window(self):
        """Open new window"""
        subprocess.Popen([sys.executable, 'anora_editor.py'])
        
    def close_all_files(self):
        """Close all files"""
        result = wx.MessageBox("Close all files?", "Confirm", wx.YES_NO | wx.ICON_QUESTION)
        if result == wx.YES:
            self.notebook.DeleteAllPages()
            self.create_new_tab()
            
    def reopen_closed_tab(self):
        """Reopen last closed tab"""
        # This would need to track closed tabs
        pass
        
    def select_all_occurrences(self):
        """Select all occurrences of current word"""
        current_editor = self.get_current_editor()
        if current_editor:
            # Get current word
            pos = current_editor.GetCurrentPos()
            word_start = current_editor.WordStartPosition(pos, True)
            word_end = current_editor.WordEndPosition(pos, True)
            word = current_editor.GetTextRange(word_start, word_end)
            
            if word:
                # Find all occurrences
                pos = 0
                while True:
                    pos = current_editor.FindText(pos, current_editor.GetLength(), word)
                    if pos == -1:
                        break
                    current_editor.AddSelection(pos, pos + len(word))
                    pos += len(word)
                    
    def delete_line(self):
        """Delete current line"""
        current_editor = self.get_current_editor()
        if current_editor:
            line = current_editor.GetCurrentLine()
            line_start = current_editor.PositionFromLine(line)
            line_end = current_editor.GetLineEndPosition(line)
            current_editor.DeleteRange(line_start, line_end - line_start + 1)
            
    def duplicate_line(self):
        """Duplicate current line"""
        current_editor = self.get_current_editor()
        if current_editor:
            line = current_editor.GetCurrentLine()
            line_start = current_editor.PositionFromLine(line)
            line_end = current_editor.GetLineEndPosition(line)
            line_text = current_editor.GetTextRange(line_start, line_end)
            current_editor.InsertText(line_end, '\n' + line_text)
            
    def move_line_up(self):
        """Move current line up"""
        current_editor = self.get_current_editor()
        if current_editor:
            line = current_editor.GetCurrentLine()
            if line > 0:
                # Get current line text
                line_start = current_editor.PositionFromLine(line)
                line_end = current_editor.GetLineEndPosition(line)
                line_text = current_editor.GetTextRange(line_start, line_end)
                
                # Get previous line text
                prev_line_start = current_editor.PositionFromLine(line - 1)
                prev_line_end = current_editor.GetLineEndPosition(line - 1)
                prev_line_text = current_editor.GetTextRange(prev_line_start, prev_line_end)
                
                # Swap lines
                current_editor.BeginUndoAction()
                current_editor.DeleteRange(prev_line_start, prev_line_end - prev_line_start)
                current_editor.InsertText(prev_line_start, line_text)
                current_editor.DeleteRange(line_start, line_end - line_start)
                current_editor.InsertText(line_start, prev_line_text)
                current_editor.EndUndoAction()
                
    def move_line_down(self):
        """Move current line down"""
        current_editor = self.get_current_editor()
        if current_editor:
            line = current_editor.GetCurrentLine()
            if line < current_editor.GetLineCount() - 1:
                # Get current line text
                line_start = current_editor.PositionFromLine(line)
                line_end = current_editor.GetLineEndPosition(line)
                line_text = current_editor.GetTextRange(line_start, line_end)
                
                # Get next line text
                next_line_start = current_editor.PositionFromLine(line + 1)
                next_line_end = current_editor.GetLineEndPosition(line + 1)
                next_line_text = current_editor.GetTextRange(next_line_start, next_line_end)
                
                # Swap lines
                current_editor.BeginUndoAction()
                current_editor.DeleteRange(next_line_start, next_line_end - next_line_start)
                current_editor.InsertText(next_line_start, line_text)
                current_editor.DeleteRange(line_start, line_end - line_start)
                current_editor.InsertText(line_start, next_line_text)
                current_editor.EndUndoAction()
                
    def insert_line_above(self):
        """Insert line above current line"""
        current_editor = self.get_current_editor()
        if current_editor:
            line = current_editor.GetCurrentLine()
            line_start = current_editor.PositionFromLine(line)
            current_editor.InsertText(line_start, '\n')
            current_editor.SetCurrentPos(line_start)
            
    def insert_line_below(self):
        """Insert line below current line"""
        current_editor = self.get_current_editor()
        if current_editor:
            line = current_editor.GetCurrentLine()
            line_end = current_editor.GetLineEndPosition(line)
            current_editor.InsertText(line_end, '\n')
            current_editor.SetCurrentPos(line_end + 1)
            
    # Windows-specific methods
    def register_file_association(self, extension):
        """Register file association in Windows"""
        if WINDOWS_AVAILABLE:
            try:
                # Register file association
                key_path = f"Software\\Classes\\{extension}"
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    winreg.SetValue(key, "", winreg.REG_SZ, "AnoraEditor")
                    
                # Register command
                command_key_path = f"Software\\Classes\\{extension}\\shell\\open\\command"
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_key_path) as key:
                    exe_path = os.path.abspath(sys.argv[0])
                    winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            except:
                pass
                
    def register_in_registry(self):
        """Register Anora Editor in Windows registry"""
        if WINDOWS_AVAILABLE:
            try:
                # Register application
                key_path = "Software\\AnoraEditor"
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    winreg.SetValue(key, "DisplayName", winreg.REG_SZ, "Anora Editor")
                    winreg.SetValue(key, "Version", winreg.REG_SZ, "1.0")
                    winreg.SetValue(key, "InstallPath", winreg.REG_SZ, os.path.dirname(os.path.abspath(__file__)))
            except:
                pass
                
    def monitor_clipboard(self):
        """Monitor Windows clipboard"""
        if WINDOWS_AVAILABLE:
            while True:
                try:
                    time.sleep(1)
                    # Check clipboard changes
                    pass
                except:
                    break
                    
    def monitor_file_system(self):
        """Monitor file system changes"""
        if WINDOWS_AVAILABLE:
            while True:
                try:
                    time.sleep(2)
                    # Check file system changes
                    pass
                except:
                    break
                    
    # Settings management
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('anora_settings.json'):
                with open('anora_settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except:
            pass
            
    def save_settings(self):
        """Save settings to file"""
        try:
            with open('anora_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass


class FileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window
        
    def OnDropFiles(self, x, y, filenames):
        """Handle file drop"""
        for filename in filenames:
            self.window.on_file_dropped(filename)
        return True


def main():
    """Main application entry point"""
    app = wx.App()
    
    # Create and show the main window
    frame = AnoraEditor()
    frame.Show()
    
    # Start the event loop
    app.MainLoop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Always write exceptions to a log file for Windows users
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anora_editor.log')
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write('\n=== Unhandled exception ===\n')
                traceback.print_exc(file=f)
        except Exception:
            pass
        raise