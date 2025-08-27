#!/usr/bin/env python3
"""
Test script for line number synchronization
"""
import tkinter as tk
from tkinter import scrolledtext
import time

def test_line_numbers():
    root = tk.Tk()
    root.title("Line Number Test")
    root.geometry("600x400")
    
    # Create frame
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Line numbers
    line_frame = tk.Frame(frame)
    line_frame.pack(side=tk.LEFT, fill=tk.Y)
    
    line_numbers = tk.Text(line_frame, width=6, padx=6, takefocus=0,
                          border=0, background='#2d2d30', foreground='#cccccc',
                          state='disabled', font=('Consolas', 10), wrap=tk.NONE)
    line_numbers.pack(side=tk.LEFT, fill=tk.Y)
    
    # Add scrollbar to line numbers
    line_scrollbar = tk.Scrollbar(line_frame, orient=tk.VERTICAL, command=line_numbers.yview)
    line_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    line_numbers.configure(yscrollcommand=line_scrollbar.set)
    
    # Main text widget
    text_widget = scrolledtext.ScrolledText(frame, font=('Consolas', 10), wrap=tk.NONE)
    text_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    # Sync function
    def sync_scroll(*args):
        text_widget.yview(*args)
        try:
            line_numbers.yview_moveto(text_widget.yview()[0])
        except Exception:
            pass
    
    def force_sync(*args):
        try:
            line_numbers.yview_moveto(text_widget.yview()[0])
        except Exception:
            pass
    
    # Configure scrollbar
    text_widget.configure(yscrollcommand=sync_scroll)
    
    # Bind events
    text_widget.bind('<Configure>', force_sync)
    text_widget.bind('<KeyRelease>', force_sync)
    text_widget.bind('<ButtonRelease-1>', force_sync)
    text_widget.bind('<MouseWheel>', force_sync)
    text_widget.bind('<Button-4>', force_sync)
    text_widget.bind('<Button-5>', force_sync)
    text_widget.bind('<Key>', force_sync)
    text_widget.bind('<Button-1>', force_sync)
    text_widget.bind('<B1-Motion>', force_sync)
    
    # Update line numbers function
    def update_line_numbers():
        content = text_widget.get("1.0", tk.END)
        lines = content.count('\n')
        current_scroll = text_widget.yview()[0]
        
        line_numbers.config(state='normal')
        line_numbers.delete("1.0", tk.END)
        for i in range(1, lines + 1):
            line_numbers.insert(tk.END, f"{i:4d}\n")
        line_numbers.config(state='disabled')
        
        try:
            line_numbers.yview_moveto(current_scroll)
        except Exception:
            pass
    
    # Bind text changes
    text_widget.bind('<KeyRelease>', lambda e: update_line_numbers())
    
    # Add test content
    test_content = ""
    for i in range(1, 101):
        test_content += f"Line {i}: This is test content for line number synchronization testing.\n"
    
    text_widget.insert("1.0", test_content)
    update_line_numbers()
    
    print("Line number test window opened. Test scrolling and typing.")
    print("Line numbers should stay perfectly synchronized.")
    
    root.mainloop()

if __name__ == "__main__":
    test_line_numbers()