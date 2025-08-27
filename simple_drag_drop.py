#!/usr/bin/env python3
"""
Simple drag and drop implementation for Nova Editor
"""

import tkinter as tk
from tkinter import scrolledtext
import os
import sys

class SimpleDragDrop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nova Editor - Drag & Drop Test")
        self.root.geometry("800x600")
        
        # Create text widget
        self.text = scrolledtext.ScrolledText(
            self.root,
            bg='#1e1e1e',
            fg='#d4d4d4',
            font=('Consolas', 10),
            wrap=tk.NONE
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind drag and drop events
        self.text.bind('<Drop>', self.on_drop)
        self.text.bind('<DragEnter>', self.on_drag_enter)
        self.text.bind('<DragLeave>', self.on_drag_leave)
        
        # Add instructions
        instructions = """Drag and Drop Test

Instructions:
1. Drag any file from File Explorer
2. Drop it onto this text area
3. The file should open and display its contents

Supported file types:
- .py (Python)
- .cs (C#)
- .js (JavaScript)
- .html (HTML)
- .css (CSS)
- .json (JSON)
- And many more!

Try dragging a file now!
"""
        
        self.text.insert("1.0", instructions)
        
    def on_drop(self, event):
        """Handle file drops"""
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
                        self.open_file(file_path)
                        
        except Exception as e:
            print(f"Drop error: {e}")
            
    def on_drag_enter(self, event):
        """Handle drag enter"""
        event.widget.config(cursor="hand2")
        print("Drag entered")
        
    def on_drag_leave(self, event):
        """Handle drag leave"""
        event.widget.config(cursor="")
        print("Drag left")
        
    def open_file(self, file_path):
        """Open a file and display its contents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clear the text widget
            self.text.delete("1.0", tk.END)
            
            # Insert file content
            self.text.insert("1.0", f"=== {os.path.basename(file_path)} ===\n\n")
            self.text.insert(tk.END, content)
            
            print(f"Opened file: {file_path}")
            
        except Exception as e:
            print(f"Error opening file: {e}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleDragDrop()
    app.run()