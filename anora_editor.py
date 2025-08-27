#!/usr/bin/env python3
"""
Anora Editor - Professional Code Editor
Built with wxPython for native Windows integration
"""

import wx
import wx.stc as stc
import os
import sys
import re
from pathlib import Path

class AnoraEditor(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Anora Editor - Professional Code Editor", 
                        size=(1200, 800))
        
        # Set up the main frame
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        self.SetForegroundColour(wx.Colour(212, 212, 212))
        
        # Initialize variables
        self.current_file = None
        self.modified = False
        self.files = []
        
        # Create the UI
        self.create_ui()
        
        # Set up native drag and drop
        self.setup_drag_drop()
        
        # Set up syntax highlighting
        self.setup_syntax_highlighting()
        
        # Center the window
        self.Center()
        
        # Bind events
        self.bind_events()
        
        print("🔥 Anora Editor (wxPython) - Professional Code Editor Started!")
        
    def create_ui(self):
        """Create the user interface"""
        # Create main panel
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(30, 30, 30))
        
        # Create main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create toolbar
        self.create_toolbar()
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        
        # Create notebook for tabs
        self.notebook = wx.aui.AuiNotebook(self.panel, style=wx.aui.AUI_NB_TOP | 
                                         wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_TAB_MOVE |
                                         wx.aui.AUI_NB_SCROLL_BUTTONS)
        self.notebook.SetArtProvider(wx.aui.AuiDefaultTabArt())
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        
        # Create status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready")
        
        # Set the main sizer
        self.panel.SetSizer(main_sizer)
        
        # Create initial tab
        self.create_new_tab()
        
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
        
        self.toolbar.Realize()
        
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
        
    def setup_generic_highlighting(self, editor):
        """Set up generic syntax highlighting"""
        editor.SetLexer(stc.STC_LEX_NULL)
        
    def setup_drag_drop(self):
        """Set up native drag and drop"""
        # Enable file drop on the frame
        self.SetDropTarget(FileDropTarget(self))
        print("✅ Native drag and drop enabled")
        
    def bind_events(self):
        """Bind all events"""
        # Menu events
        self.Bind(wx.EVT_MENU, self.on_new, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_replace, id=wx.ID_REPLACE)
        
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
        
    def on_text_change(self, event):
        """Handle text change events"""
        self.modified = True
        self.update_title()
        event.Skip()
        
    def on_save_point(self, event):
        """Handle save point reached"""
        self.modified = False
        self.update_title()
        event.Skip()
        
    def on_save_point_left(self, event):
        """Handle save point left"""
        self.modified = True
        self.update_title()
        event.Skip()
        
    def on_new(self, event):
        """Create a new file"""
        self.create_new_tab()
        
    def on_open(self, event):
        """Open a file"""
        with wx.FileDialog(self, "Open file", wildcard="All files (*.*)|*.*",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
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
            
            # Update tab title
            current_page = self.notebook.GetSelection()
            if current_page >= 0:
                self.notebook.SetPageText(current_page, os.path.basename(file_path))
                
            self.status_bar.SetStatusText(f"Saved: {file_path}")
            
        except Exception as e:
            wx.MessageBox(f"Error saving file: {e}", "Error", wx.OK | wx.ICON_ERROR)
            
    def on_find(self, event):
        """Show find dialog"""
        current_editor = self.get_current_editor()
        if current_editor:
            self.show_find_dialog(current_editor)
            
    def on_replace(self, event):
        """Show replace dialog"""
        current_editor = self.get_current_editor()
        if current_editor:
            self.show_replace_dialog(current_editor)
            
    def show_find_dialog(self, editor):
        """Show find dialog"""
        find_dialog = wx.FindReplaceDialog(self, wx.FindReplaceData())
        find_dialog.Show()
        
    def show_replace_dialog(self, editor):
        """Show replace dialog"""
        replace_dialog = wx.FindReplaceDialog(self, wx.FindReplaceData(), "Replace")
        replace_dialog.Show()
        
    def on_tab_changed(self, event):
        """Handle tab change"""
        current_page = self.notebook.GetSelection()
        if current_page >= 0:
            editor = self.notebook.GetPage(current_page)
            # Update current file and status
            self.status_bar.SetStatusText(f"Tab {current_page + 1}")
        event.Skip()
        
    def on_tab_close(self, event):
        """Handle tab close"""
        # Check if file is modified and ask to save
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
                
        self.Destroy()
        
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
        
    def on_file_dropped(self, file_path):
        """Handle file drop"""
        print(f"🔥 File dropped: {file_path}")
        if os.path.exists(file_path):
            self.open_file(file_path)
            self.status_bar.SetStatusText(f"Opened: {file_path}")


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