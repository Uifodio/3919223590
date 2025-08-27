#!/usr/bin/env python3
"""
Final test for Nova Editor - Drag & Drop + Syntax Highlighting
"""

import tkinter as tk
from tkinter import scrolledtext
import os

def test_nova_editor():
    """Test Nova Editor functionality"""
    
    root = tk.Tk()
    root.title("Nova Editor - Final Test")
    root.geometry("800x600")
    
    # Create text widget with Nova Editor styling
    text = scrolledtext.ScrolledText(
        root,
        bg='#1e1e1e',
        fg='#d4d4d4',
        font=('Consolas', 10),
        wrap=tk.NONE
    )
    text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Configure syntax highlighting tags
    text.tag_configure("keyword", foreground="#569cd6", font=('Consolas', 10, 'bold'))
    text.tag_configure("string", foreground="#ce9178", font=('Consolas', 10))
    text.tag_configure("comment", foreground="#6a9955", font=('Consolas', 10, 'italic'))
    text.tag_configure("number", foreground="#b5cea8", font=('Consolas', 10))
    text.tag_configure("function", foreground="#dcdcaa", font=('Consolas', 10, 'bold'))
    
    # Setup drag and drop
    setup_drag_drop(root, text)
    
    # Add test content
    test_content = """Nova Editor - Final Test

Instructions:
1. Drag any file from Windows Explorer to this window
2. The file should open with syntax highlighting
3. Try dragging Python, C#, JavaScript, HTML files

Test Python Code:
def hello_world():
    print("Hello, World!")
    return True

Test C# Code:
public class TestScript : MonoBehaviour
{
    void Start()
    {
        Debug.Log("Hello from Unity!");
    }
}

Test JavaScript Code:
function testFunction() {
    console.log("Hello from JavaScript!");
    return true;
}

Test HTML Code:
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>

Try dragging files now!
"""
    
    text.insert("1.0", test_content)
    
    # Apply syntax highlighting to test content
    apply_test_highlighting(text)
    
    root.mainloop()

def setup_drag_drop(root, text_widget):
    """Setup drag and drop for testing"""
    try:
        # Try tkinterdnd2
        text_widget.drop_target_register('DND_Files')
        text_widget.dnd_bind('<<Drop>>', lambda e: handle_drop(e, text_widget))
        print("✅ Drag and drop enabled")
    except:
        try:
            # Try main window
            root.drop_target_register('DND_Files')
            root.dnd_bind('<<Drop>>', lambda e: handle_drop(e, text_widget))
            print("✅ Main window drag and drop enabled")
        except:
            print("❌ Drag and drop not available")
            # Add fallback button
            button = tk.Button(root, text="Open File", command=lambda: open_file_dialog(text_widget))
            button.pack(pady=5)

def handle_drop(event, text_widget):
    """Handle file drops"""
    print(f"Drop event: {event}")
    print(f"Drop data: {event.data}")
    
    try:
        files = event.data
        if isinstance(files, str):
            # Handle single file path
            if files.startswith('{'):
                # Handle multiple files in braces
                files = files.strip('{}').split('} {')
            else:
                files = [files]
        
        print(f"Processing files: {files}")
        
        for file_path in files:
            # Clean up the file path
            file_path = file_path.strip()
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            
            print(f"Processing file: {file_path}")
            
            if os.path.isfile(file_path):
                print(f"File exists: {file_path}")
                open_file_in_widget(file_path, text_widget)
                break
            else:
                print(f"File does not exist: {file_path}")
                
    except Exception as e:
        print(f"Drop error: {e}")
        import traceback
        traceback.print_exc()

def open_file_in_widget(file_path, text_widget):
    """Open a file in the text widget with syntax highlighting"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clear the text widget
        text_widget.delete("1.0", tk.END)
        
        # Insert file content
        text_widget.insert("1.0", f"=== {os.path.basename(file_path)} ===\n\n")
        text_widget.insert(tk.END, content)
        
        # Apply syntax highlighting based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        apply_syntax_highlighting(text_widget, ext)
        
        print(f"✅ Opened file: {file_path}")
        
    except Exception as e:
        print(f"Error opening file: {e}")

def apply_syntax_highlighting(text_widget, file_extension):
    """Apply syntax highlighting based on file extension"""
    print(f"Applying syntax highlighting for: {file_extension}")
    
    if file_extension == '.py':
        highlight_python(text_widget)
    elif file_extension == '.cs':
        highlight_csharp(text_widget)
    elif file_extension == '.js':
        highlight_javascript(text_widget)
    elif file_extension == '.html':
        highlight_html(text_widget)
    else:
        highlight_generic(text_widget)

def highlight_python(text_widget):
    """Highlight Python code"""
    keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global', 'nonlocal', 'print']
    
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
    for quote in ['"', "'"]:
        start = "1.0"
        while True:
            pos = text_widget.search(quote, start, tk.END)
            if not pos:
                break
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
        line_end = text_widget.index(f"{pos} lineend")
        text_widget.tag_add("comment", pos, line_end)
        start = line_end

def highlight_csharp(text_widget):
    """Highlight C# code"""
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

def highlight_javascript(text_widget):
    """Highlight JavaScript code"""
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

def highlight_html(text_widget):
    """Highlight HTML code"""
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

def highlight_generic(text_widget):
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
    for comment_char in ['#', '//']:
        start = "1.0"
        while True:
            pos = text_widget.search(comment_char, start, tk.END)
            if not pos:
                break
            end = text_widget.index(f"{pos} lineend")
            text_widget.tag_add("comment", pos, end)
            start = end

def apply_test_highlighting(text_widget):
    """Apply highlighting to test content"""
    # Highlight Python section
    python_start = text_widget.search("Test Python Code:", "1.0", tk.END)
    if python_start:
        python_end = text_widget.search("Test C# Code:", python_start, tk.END)
        if python_end:
            # Apply Python highlighting to this section
            highlight_python(text_widget)
    
    # Highlight C# section
    csharp_start = text_widget.search("Test C# Code:", "1.0", tk.END)
    if csharp_start:
        csharp_end = text_widget.search("Test JavaScript Code:", csharp_start, tk.END)
        if csharp_end:
            # Apply C# highlighting to this section
            highlight_csharp(text_widget)
    
    # Highlight JavaScript section
    js_start = text_widget.search("Test JavaScript Code:", "1.0", tk.END)
    if js_start:
        js_end = text_widget.search("Test HTML Code:", js_start, tk.END)
        if js_end:
            # Apply JavaScript highlighting to this section
            highlight_javascript(text_widget)
    
    # Highlight HTML section
    html_start = text_widget.search("Test HTML Code:", "1.0", tk.END)
    if html_start:
        # Apply HTML highlighting to this section
        highlight_html(text_widget)

def open_file_dialog(text_widget):
    """Open file dialog as fallback"""
    from tkinter import filedialog
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
        open_file_in_widget(file_path, text_widget)

if __name__ == "__main__":
    test_nova_editor()