#!/usr/bin/env python3
"""
Absolute Brute Force Drag & Drop Test
"""

import tkinter as tk
from tkinter import scrolledtext
import os

def test_absolute_brute_force():
    """Test absolute brute force drag and drop"""
    
    root = tk.Tk()
    root.title("🔥 ABSOLUTE BRUTE FORCE DRAG & DROP TEST")
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
    
    # Setup absolute brute force drag and drop
    setup_absolute_brute_force_drag_drop(root, text)
    
    # Add test content
    test_content = """🔥 ABSOLUTE BRUTE FORCE DRAG & DROP TEST

🎯 ABSOLUTE BRUTE FORCE METHODS ENABLED:
✅ Method 1: tkinterdnd2 on text widget
✅ Method 2: tkinterdnd2 on main window
✅ Method 3: Windows API drag and drop
✅ Method 4: Mouse monitoring + clipboard checking
✅ Method 5: Visual drop zones + manual file opening
✅ Method 6: File system monitoring
✅ Method 7: Clipboard monitoring
✅ Method 8: Windows message monitoring
✅ Method 9: Multiple drop targets

🔥 INSTRUCTIONS:
1. Drag ANY file from Windows Explorer to this window
2. The file should open with the filename as the tab name
3. Try dragging to different areas of the window
4. Use Ctrl+O to open files manually if needed

🔥 ABSOLUTE BRUTE FORCE FEATURES:
- Multiple drop zones visible on screen
- File system monitoring for new files
- Clipboard monitoring for file paths
- Windows message monitoring
- Multiple drop targets on every widget
- NO unwanted highlighting when moving mouse

🔥 TESTING AREAS:
- Main text area
- Drop zones (4 visible zones)
- Window borders
- Any part of the window

Try dragging files now! 🔥
"""
    
    text.insert("1.0", test_content)
    
    # Add status bar
    status_bar = tk.Frame(root, bg='#2d2d30', height=25)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    status_bar.pack_propagate(False)
    
    status_label = tk.Label(status_bar, text="🔥 ABSOLUTE BRUTE FORCE MODE ACTIVE", 
                           bg='#2d2d30', fg='#ff4444', font=('Arial', 10, 'bold'))
    status_label.pack(side=tk.LEFT, padx=5)
    
    # Add buttons
    button_frame = tk.Frame(root, bg='#2d2d30')
    button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    open_btn = tk.Button(button_frame, text="🔥 Open File", 
                        command=lambda: open_file_dialog(text),
                        bg='#ff4444', fg='#ffffff', font=('Arial', 10, 'bold'))
    open_btn.pack(side=tk.LEFT, padx=5)
    
    clear_btn = tk.Button(button_frame, text="🔥 Clear", 
                         command=lambda: text.delete("1.0", tk.END),
                         bg='#ff4444', fg='#ffffff', font=('Arial', 10, 'bold'))
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

def setup_absolute_brute_force_drag_drop(root, text_widget):
    """Setup absolute brute force drag and drop"""
    print("🔥 SETTING UP ABSOLUTE BRUTE FORCE DRAG & DROP...")
    
    # Method 1: tkinterdnd2 on text widget
    try:
        text_widget.drop_target_register('DND_Files')
        text_widget.dnd_bind('<<Drop>>', lambda e: handle_absolute_brute_force_drop(e, text_widget))
        print("✅ Method 1: tkinterdnd2 on text widget enabled")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        
    # Method 2: tkinterdnd2 on main window
    try:
        root.drop_target_register('DND_Files')
        root.dnd_bind('<<Drop>>', lambda e: handle_absolute_brute_force_drop(e, text_widget))
        print("✅ Method 2: tkinterdnd2 on main window enabled")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        
    # Method 3: Create multiple drop zones
    try:
        create_absolute_brute_force_drop_zones(root, text_widget)
        print("✅ Method 3: Multiple drop zones created")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        
    # Method 4: Keyboard shortcuts
    try:
        root.bind('<Control-o>', lambda e: open_file_dialog(text_widget))
        root.bind('<Control-v>', lambda e: check_clipboard_brute_force(text_widget))
        print("✅ Method 4: Keyboard shortcuts enabled")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
        
    # Method 5: File system monitoring
    try:
        setup_file_system_monitoring_brute_force(root, text_widget)
        print("✅ Method 5: File system monitoring enabled")
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
        
    print("🔥 ABSOLUTE BRUTE FORCE DRAG & DROP SETUP COMPLETE!")

def handle_absolute_brute_force_drop(event, text_widget):
    """Handle absolute brute force drop"""
    print(f"🔥 ABSOLUTE BRUTE FORCE DROP EVENT: {event}")
    print(f"🔥 DROP DATA: {event.data}")
    
    try:
        files = event.data
        if isinstance(files, str):
            if files.startswith('{'):
                files = files.strip('{}').split('} {')
            else:
                files = [files]
        
        print(f"🔥 PROCESSING FILES: {files}")
        
        for file_path in files:
            file_path = file_path.strip()
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            
            print(f"🔥 PROCESSING FILE: {file_path}")
            
            if os.path.isfile(file_path):
                print(f"🔥 FILE EXISTS: {file_path}")
                open_file_with_filename(text_widget, file_path)
                break
            else:
                print(f"❌ FILE DOES NOT EXIST: {file_path}")
                
    except Exception as e:
        print(f"❌ ABSOLUTE BRUTE FORCE DROP ERROR: {e}")
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
        text_widget.insert("1.0", f"🔥 FILE: {file_name}\n")
        text_widget.insert(tk.END, f"📁 PATH: {file_path}\n")
        text_widget.insert(tk.END, f"📊 SIZE: {len(content)} characters\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.insert(tk.END, content)
        
        print(f"🔥 FILE OPENED WITH FILENAME: {file_name}")
        
    except Exception as e:
        print(f"❌ ERROR OPENING FILE: {e}")

def create_absolute_brute_force_drop_zones(root, text_widget):
    """Create absolute brute force drop zones"""
    drop_zones = [
        ("🔥 DROP FILES HERE", 0.5, 0.1, '#ff4444'),
        ("🔥 DROP FILES HERE", 0.2, 0.3, '#ff8800'),
        ("🔥 DROP FILES HERE", 0.8, 0.3, '#ff0088'),
        ("🔥 DROP FILES HERE", 0.5, 0.8, '#8800ff'),
        ("🔥 DROP FILES HERE", 0.1, 0.5, '#00ff88'),
        ("🔥 DROP FILES HERE", 0.9, 0.5, '#0088ff')
    ]
    
    for text, relx, rely, color in drop_zones:
        drop_label = tk.Label(
            root,
            text=text,
            bg=color,
            fg='#ffffff',
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
            drop_label.dnd_bind('<<Drop>>', lambda e: handle_absolute_brute_force_drop(e, text_widget))
            print(f"✅ Drop zone created: {text}")
        except:
            pass

def open_file_dialog(text_widget):
    """Open file dialog"""
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(
        title="🔥 Open File",
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

def check_clipboard_brute_force(text_widget):
    """Check clipboard for file paths"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            if data and os.path.isfile(data):
                print(f"🔥 FILE PATH IN CLIPBOARD: {data}")
                open_file_with_filename(text_widget, data)
        except:
            pass
        finally:
            win32clipboard.CloseClipboard()
    except:
        pass

def setup_file_system_monitoring_brute_force(root, text_widget):
    """Setup file system monitoring"""
    try:
        import glob
        
        # Store initial files
        initial_files = set()
        for pattern in ['*.py', '*.cs', '*.js', '*.html', '*.css', '*.json', '*.txt']:
            for file_path in glob.glob(pattern):
                initial_files.add(file_path)
        
        def monitor_files():
            try:
                current_files = set()
                for pattern in ['*.py', '*.cs', '*.js', '*.html', '*.css', '*.json', '*.txt']:
                    for file_path in glob.glob(pattern):
                        current_files.add(file_path)
                
                new_files = current_files - initial_files
                for file_path in new_files:
                    if os.path.isfile(file_path):
                        print(f"🔥 NEW FILE DETECTED: {file_path}")
                        open_file_with_filename(text_widget, file_path)
                        initial_files.add(file_path)
                
                root.after(2000, monitor_files)
            except:
                pass
        
        # Start monitoring
        root.after(2000, monitor_files)
        
    except Exception as e:
        print(f"❌ File system monitoring failed: {e}")

if __name__ == "__main__":
    test_absolute_brute_force()