#!/usr/bin/env python3
"""
Anora Editor - Professional Code Editor
Built with wxPython for extreme professionalism and native Windows integration
"""

import wx
import wx.stc as stc
import wx.aui
import os
import sys
import re
import time
import threading
from pathlib import Path

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
        
        # Create the UI
        self.create_ui()
        
        # Set up native drag and drop
        self.setup_drag_drop()
        
        # Set up syntax highlighting
        self.setup_syntax_highlighting()
        
        # Set up professional window behavior
        self.setup_professional_behavior()
        
        # Center the window
        self.Center()
        
        # Bind events
        self.bind_events()
        
        # Load recent files
        self.load_recent_files()
        
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
        search_menu.Append(wx.ID_FIND, "&Find\tCtrl+F", "Find text")
        search_menu.Append(wx.ID_REPLACE, "&Replace\tCtrl+H", "Replace text")
        search_menu.Append(wx.ID_FINDNEXT, "Find &Next\tF3", "Find next occurrence")
        search_menu.Append(wx.ID_FINDPREV, "Find &Previous\tShift+F3", "Find previous occurrence")
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
        self.find_text = wx.TextCtrl(self.search_panel, style=wx.TE_PROCESS_ENTER)
        self.find_text.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.find_text.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # Replace label and text
        replace_label = wx.StaticText(self.search_panel, label="Replace:")
        replace_label.SetForegroundColour(wx.Colour(212, 212, 212))
        self.replace_text = wx.TextCtrl(self.search_panel, style=wx.TE_PROCESS_ENTER)
        self.replace_text.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.replace_text.SetForegroundColour(wx.Colour(212, 212, 212))
        
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
        search_sizer.Add(self.find_text, 1, wx.EXPAND | wx.ALL, 5)
        search_sizer.Add(replace_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        search_sizer.Add(self.replace_text, 1, wx.EXPAND | wx.ALL, 5)
        search_sizer.Add(find_btn, 0, wx.ALL, 5)
        search_sizer.Add(replace_btn, 0, wx.ALL, 5)
        search_sizer.Add(replace_all_btn, 0, wx.ALL, 5)
        search_sizer.Add(close_btn, 0, wx.ALL, 5)
        
        self.search_panel.SetSizer(search_sizer)
        
        # Bind events
        close_btn.Bind(wx.EVT_BUTTON, self.hide_search_panel)
        find_btn.Bind(wx.EVT_BUTTON, self.find_text)
        replace_btn.Bind(wx.EVT_BUTTON, self.replace_text)
        replace_all_btn.Bind(wx.EVT_BUTTON, self.replace_all_text)
        
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
        self.Bind(wx.EVT_MENU, self.on_find_next, id=wx.ID_FINDNEXT)
        self.Bind(wx.EVT_MENU, self.on_find_prev, id=wx.ID_FINDPREV)
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
        self.find_text()
        
    def on_find_prev(self, event):
        """Find previous occurrence"""
        self.find_text(forward=False)
        
    def show_search_panel(self):
        """Show the search panel"""
        self.search_panel.Show()
        self.Layout()
        self.find_text.SetFocus()
        
    def hide_search_panel(self, event=None):
        """Hide the search panel"""
        self.search_panel.Hide()
        self.Layout()
        
    def find_text(self, event=None, forward=True):
        """Find text in the current editor"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        search_text = self.find_text.GetValue()
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
            
    def replace_text(self, event=None):
        """Replace current occurrence"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        search_text = self.find_text.GetValue()
        replace_text = self.replace_text.GetValue()
        
        if not search_text:
            return
            
        # Get current selection
        start, end = current_editor.GetSelection()
        selected_text = current_editor.GetTextRange(start, end)
        
        if selected_text == search_text:
            current_editor.Replace(start, end, replace_text)
            self.find_text()  # Find next occurrence
        else:
            self.find_text()  # Find first occurrence
            
    def replace_all_text(self, event=None):
        """Replace all occurrences"""
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        search_text = self.find_text.GetValue()
        replace_text = self.replace_text.GetValue()
        
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
    main()