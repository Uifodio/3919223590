#!/usr/bin/env python3
"""
Simple Drag & Drop Test for Anora Editor
"""

import tkinter as tk
from tkinter import scrolledtext
import os

def test_simple_drag_drop():
    """Simple drag and drop test"""
    
    root = tk.Tk()
    root.title("🔥 Anora Editor - Simple Drag & Drop Test")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = tk.Frame(root, bg='#1e1e1e')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create text widget
    text = scrolledtext.ScrolledText(
        main_frame,
        bg='#1e1e1e',
        fg='#d4d4d4',
        font=('Consolas', 10),
        wrap=tk.NONE
    )
    text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Add test content
    test_content = """🔥 Anora Editor - Simple Drag & Drop Test

🎯 SIMPLE DRAG & DROP TEST:
✅ Basic tkinterdnd2 setup
✅ File drop handling
✅ File opening with filename
✅ Professional dark theme

🔥 INSTRUCTIONS:
1. Drag ANY file from Windows Explorer to this window
2. The file should open and display its content
3. The filename should be shown in the header

🔥 TESTING:
- Try dragging different file types
- Check if files open correctly
- Verify filename display

🔥 FEATURES:
- Dark theme
- Professional appearance
- File content display
- Filename header

Try dragging files now! 🔥
"""
    
    text.insert("1.0", test_content)
    
    # Setup simple drag and drop
    setup_simple_drag_drop(root, text)
    
    # Add status bar
    status_bar = tk.Frame(root, bg='#2d2d30', height=25)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    status_bar.pack_propagate(False)
    
    status_label = tk.Label(status_bar, text="🔥 Anora Editor - Simple Drag & Drop Active", 
                           bg='#2d2d30', fg='#00ff88', font=('Arial', 10, 'bold'))
    status_label.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

def setup_simple_drag_drop(root, text_widget):
    """Setup simple drag and drop"""
    print("🔥 Setting up simple drag and drop...")
    
    try:
        # Method 1: tkinterdnd2 on text widget
        text_widget.drop_target_register('DND_Files')
        text_widget.dnd_bind('<<Drop>>', lambda e: handle_simple_drop(e, text_widget))
        print("✅ Simple drag and drop setup complete")
        
    except Exception as e:
        print(f"❌ Simple drag and drop failed: {e}")
        # Fallback: manual file opening
        setup_manual_file_opening(root, text_widget)

def handle_simple_drop(event, text_widget):
    """Handle simple drop"""
    print(f"🔥 Drop event: {event}")
    print(f"🔥 Drop data: {event.data}")
    
    try:
        files = event.data
        if isinstance(files, str):
            if files.startswith('{'):
                files = files.strip('{}').split('} {')
            else:
                files = [files]
        
        print(f"🔥 Processing files: {files}")
        
        for file_path in files:
            file_path = file_path.strip()
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            
            print(f"🔥 Processing file: {file_path}")
            
            if os.path.isfile(file_path):
                print(f"🔥 File exists: {file_path}")
                open_file_simple(text_widget, file_path)
                break
            else:
                print(f"❌ File does not exist: {file_path}")
                
    except Exception as e:
        print(f"❌ Drop error: {e}")
        import traceback
        traceback.print_exc()

def open_file_simple(text_widget, file_path):
    """Open file with simple display"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clear text widget
        text_widget.delete("1.0", tk.END)
        
        # Insert file content with filename header
        file_name = os.path.basename(file_path)
        text_widget.insert("1.0", f"🔥 ANORA EDITOR - FILE OPENED\n")
        text_widget.insert(tk.END, f"📁 FILE: {file_name}\n")
        text_widget.insert(tk.END, f"📂 PATH: {file_path}\n")
        text_widget.insert(tk.END, f"📊 SIZE: {len(content)} characters\n")
        text_widget.insert(tk.END, "=" * 60 + "\n\n")
        text_widget.insert(tk.END, content)
        
        print(f"🔥 File opened: {file_name}")
        
    except Exception as e:
        print(f"❌ Error opening file: {e}")

def setup_manual_file_opening(root, text_widget):
    """Setup manual file opening as fallback"""
    print("🔥 Setting up manual file opening...")
    
    # Add button for manual file opening
    button_frame = tk.Frame(root, bg='#2d2d30')
    button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    open_btn = tk.Button(button_frame, text="🔥 Open File", 
                        command=lambda: open_file_dialog(text_widget),
                        bg='#00ff88', fg='#000000', font=('Arial', 10, 'bold'))
    open_btn.pack(side=tk.LEFT, padx=5)
    
    print("✅ Manual file opening setup complete")

def open_file_dialog(text_widget):
    """Open file dialog"""
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(
        title="🔥 Anora Editor - Open File",
        filetypes=[
            ("All Files", "*.*"),
            ("Python Files", "*.py"),
            ("C# Files", "*.cs"),
            ("JavaScript Files", "*.js"),
            ("HTML Files", "*.html"),
            ("CSS Files", "*.css"),
            ("JSON Files", "*.json"),
            ("Text Files", "*.txt")
        ]
    )
    if file_path:
        open_file_simple(text_widget, file_path)

if __name__ == "__main__":
    test_simple_drag_drop()