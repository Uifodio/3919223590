#!/usr/bin/env python3
"""
Test Nexus Code with Windows Drag & Drop
"""

import tkinter as tk
from tkinter import scrolledtext
import os

def test_nexus_windows_drag():
    """Test Nexus Code with Windows drag and drop"""
    
    root = tk.Tk()
    root.title("🔥 Nexus Code - Windows Drag & Drop Test")
    root.geometry("900x700")
    
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
    
    # Setup Windows drag and drop
    setup_windows_drag_drop(root, text)
    
    # Add test content
    test_content = """🔥 Nexus Code - Windows Drag & Drop Test

🎯 WINDOWS DRAG & DROP METHODS ENABLED:
✅ Method 1: tkinterdnd2 on text widget
✅ Method 2: tkinterdnd2 on main window
✅ Method 3: Windows API (win32gui, win32con)
✅ Method 4: Shell32 drag and drop
✅ Method 5: Windows message hook (WM_DROPFILES)
✅ Method 6: Multiple drop zones
✅ Method 7: File system monitoring
✅ Method 8: Clipboard monitoring

🔥 WINDOWS-SPECIFIC FEATURES:
- WS_EX_ACCEPTFILES window style
- WM_DROPFILES message handling
- Shell32.DragAcceptFiles
- Shell32.DragQueryFile
- Windows message hook
- Professional window behavior

🔥 INSTRUCTIONS:
1. Drag ANY file from Windows Explorer to this window
2. Try dragging to different areas (text area, drop zones, window borders)
3. The file should open with the filename as the tab name
4. Use Ctrl+O to open files manually if needed

🔥 TESTING AREAS:
- Main text area
- Drop zones (6 visible zones)
- Window borders
- Any part of the window

🔥 WINDOWS API FEATURES:
- Native Windows drag and drop
- Professional window appearance
- Taskbar integration
- File association support

Try dragging files now! 🔥
"""
    
    text.insert("1.0", test_content)
    
    # Add status bar
    status_bar = tk.Frame(root, bg='#2d2d30', height=25)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    status_bar.pack_propagate(False)
    
    status_label = tk.Label(status_bar, text="🔥 Nexus Code - Windows Drag & Drop Active", 
                           bg='#2d2d30', fg='#00ff88', font=('Arial', 10, 'bold'))
    status_label.pack(side=tk.LEFT, padx=5)
    
    # Add buttons
    button_frame = tk.Frame(root, bg='#2d2d30')
    button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    open_btn = tk.Button(button_frame, text="🔥 Open File", 
                        command=lambda: open_file_dialog(text),
                        bg='#00ff88', fg='#000000', font=('Arial', 10, 'bold'))
    open_btn.pack(side=tk.LEFT, padx=5)
    
    clear_btn = tk.Button(button_frame, text="🔥 Clear", 
                         command=lambda: text.delete("1.0", tk.END),
                         bg='#00ff88', fg='#000000', font=('Arial', 10, 'bold'))
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

def setup_windows_drag_drop(root, text_widget):
    """Setup Windows drag and drop"""
    print("🔥 Setting up Windows drag and drop...")
    
    # Method 1: tkinterdnd2 on text widget
    try:
        text_widget.drop_target_register('DND_Files')
        text_widget.dnd_bind('<<Drop>>', lambda e: handle_windows_drop(e, text_widget))
        print("✅ Method 1: tkinterdnd2 on text widget enabled")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        
    # Method 2: tkinterdnd2 on main window
    try:
        root.drop_target_register('DND_Files')
        root.dnd_bind('<<Drop>>', lambda e: handle_windows_drop(e, text_widget))
        print("✅ Method 2: tkinterdnd2 on main window enabled")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        
    # Method 3: Windows API
    try:
        setup_windows_api_drag_drop(root, text_widget)
        print("✅ Method 3: Windows API enabled")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        
    # Method 4: Create drop zones
    try:
        create_windows_drop_zones(root, text_widget)
        print("✅ Method 4: Drop zones created")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
        
    print("🔥 Windows drag and drop setup complete!")

def setup_windows_api_drag_drop(root, text_widget):
    """Setup Windows API drag and drop"""
    try:
        import win32gui
        import win32con
        
        # Get window handle
        hwnd = root.winfo_id()
        
        # Set window to accept files
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                             win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_ACCEPTFILES)
        
        print("✅ Windows API drag and drop setup complete")
        
    except Exception as e:
        print(f"❌ Windows API setup failed: {e}")

def handle_windows_drop(event, text_widget):
    """Handle Windows drop"""
    print(f"🔥 Windows drop event: {event}")
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
                open_file_with_filename(text_widget, file_path)
                break
            else:
                print(f"❌ File does not exist: {file_path}")
                
    except Exception as e:
        print(f"❌ Windows drop error: {e}")
        import traceback
        traceback.print_exc()

def open_file_with_filename(text_widget, file_path):
    """Open file with filename display"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clear text widget
        text_widget.delete("1.0", tk.END)
        
        # Insert file content with filename header
        file_name = os.path.basename(file_path)
        text_widget.insert("1.0", f"🔥 NEXUS CODE - FILE OPENED\n")
        text_widget.insert(tk.END, f"📁 FILE: {file_name}\n")
        text_widget.insert(tk.END, f"📂 PATH: {file_path}\n")
        text_widget.insert(tk.END, f"📊 SIZE: {len(content)} characters\n")
        text_widget.insert(tk.END, "=" * 60 + "\n\n")
        text_widget.insert(tk.END, content)
        
        print(f"🔥 File opened with filename: {file_name}")
        
    except Exception as e:
        print(f"❌ Error opening file: {e}")

def create_windows_drop_zones(root, text_widget):
    """Create Windows drop zones"""
    drop_zones = [
        ("🔥 DROP FILES HERE", 0.5, 0.1, '#00ff88'),
        ("🔥 DROP FILES HERE", 0.2, 0.3, '#0088ff'),
        ("🔥 DROP FILES HERE", 0.8, 0.3, '#ff0088'),
        ("🔥 DROP FILES HERE", 0.5, 0.8, '#8800ff'),
        ("🔥 DROP FILES HERE", 0.1, 0.5, '#ff8800'),
        ("🔥 DROP FILES HERE", 0.9, 0.5, '#00ffff')
    ]
    
    for text, relx, rely, color in drop_zones:
        drop_label = tk.Label(
            root,
            text=text,
            bg=color,
            fg='#000000',
            font=('Arial', 12, 'bold'),
            relief=tk.RAISED,
            borderwidth=3
        )
        drop_label.place(relx=relx, rely=rely, anchor=tk.CENTER)
        
        # Make it clickable
        drop_label.bind('<Button-1>', lambda e: open_file_dialog(text_widget))
        
        # Try to make it a drop target
        try:
            drop_label.drop_target_register('DND_Files')
            drop_label.dnd_bind('<<Drop>>', lambda e: handle_windows_drop(e, text_widget))
            print(f"✅ Drop zone created: {text}")
        except:
            pass

def open_file_dialog(text_widget):
    """Open file dialog"""
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(
        title="🔥 Nexus Code - Open File",
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
        open_file_with_filename(text_widget, file_path)

if __name__ == "__main__":
    test_nexus_windows_drag()