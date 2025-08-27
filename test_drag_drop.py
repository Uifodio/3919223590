#!/usr/bin/env python3
"""
Test drag and drop functionality in Nova Editor
"""

import tkinter as tk
from tkinter import scrolledtext
import os

def test_drag_drop():
    """Test drag and drop with multiple methods"""
    
    root = tk.Tk()
    root.title("Drag & Drop Test")
    root.geometry("600x400")
    
    # Create text widget
    text = scrolledtext.ScrolledText(
        root,
        bg='#1e1e1e',
        fg='#d4d4d4',
        font=('Consolas', 10)
    )
    text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Test different drag and drop methods
    methods = [
        ("tkinterdnd2 on text widget", test_tkinterdnd2_text),
        ("tkinterdnd2 on main window", test_tkinterdnd2_main),
        ("Windows API", test_windows_api),
        ("Fallback button", test_fallback)
    ]
    
    text.insert("1.0", "Drag & Drop Test\n\n")
    
    for method_name, method_func in methods:
        text.insert(tk.END, f"Testing: {method_name}\n")
        try:
            result = method_func(root, text)
            text.insert(tk.END, f"  ✅ {method_name}: {result}\n")
        except Exception as e:
            text.insert(tk.END, f"  ❌ {method_name}: {e}\n")
        text.insert(tk.END, "\n")
    
    text.insert(tk.END, "Instructions:\n")
    text.insert(tk.END, "1. Try dragging a file from Windows Explorer\n")
    text.insert(tk.END, "2. Drop it onto this window\n")
    text.insert(tk.END, "3. Check which method works\n")
    
    root.mainloop()

def test_tkinterdnd2_text(root, text_widget):
    """Test tkinterdnd2 on text widget"""
    try:
        text_widget.drop_target_register('DND_Files')
        text_widget.dnd_bind('<<Drop>>', lambda e: handle_drop(e, text_widget))
        return "Enabled"
    except Exception as e:
        return f"Failed: {e}"

def test_tkinterdnd2_main(root, text_widget):
    """Test tkinterdnd2 on main window"""
    try:
        root.drop_target_register('DND_Files')
        root.dnd_bind('<<Drop>>', lambda e: handle_drop(e, text_widget))
        return "Enabled"
    except Exception as e:
        return f"Failed: {e}"

def test_windows_api(root, text_widget):
    """Test Windows API drag and drop"""
    try:
        import win32gui
        import win32con
        
        hwnd = root.winfo_id()
        current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_style = current_style | win32con.WS_EX_ACCEPTFILES
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
        
        return "Enabled"
    except Exception as e:
        return f"Failed: {e}"

def test_fallback(root, text_widget):
    """Test fallback button"""
    try:
        button = tk.Button(root, text="Open File", command=lambda: open_file_dialog(text_widget))
        button.pack(pady=5)
        return "Button added"
    except Exception as e:
        return f"Failed: {e}"

def handle_drop(event, text_widget):
    """Handle file drop"""
    try:
        files = event.data
        if isinstance(files, str):
            files = [files]
        
        for file_path in files:
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", f"Dropped file: {os.path.basename(file_path)}\n\n")
                text_widget.insert(tk.END, content)
                break
    except Exception as e:
        text_widget.insert(tk.END, f"Drop error: {e}\n")

def open_file_dialog(text_widget):
    """Open file dialog"""
    from tkinter import filedialog
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", f"Opened file: {os.path.basename(file_path)}\n\n")
        text_widget.insert(tk.END, content)

if __name__ == "__main__":
    test_drag_drop()