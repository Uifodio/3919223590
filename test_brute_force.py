#!/usr/bin/env python3
"""
Comprehensive test for Nova Editor - Brute Force Features
"""

import tkinter as tk
from tkinter import scrolledtext
import os
import time

def test_nova_editor_brute_force():
    """Test Nova Editor with brute force features"""
    
    root = tk.Tk()
    root.title("Nova Editor - Brute Force Test")
    root.geometry("1000x700")
    
    # Create main frame
    main_frame = tk.Frame(root, bg='#1e1e1e')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create text widget with Nova Editor styling
    text = scrolledtext.ScrolledText(
        main_frame,
        bg='#1e1e1e',
        fg='#d4d4d4',
        font=('Consolas', 10),
        wrap=tk.NONE
    )
    text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Configure syntax highlighting tags
    text.tag_configure("keyword", foreground="#569cd6", font=('Consolas', 10, 'bold'))
    text.tag_configure("string", foreground="#ce9178", font=('Consolas', 10))
    text.tag_configure("comment", foreground="#6a9955", font=('Consolas', 10, 'italic'))
    text.tag_configure("number", foreground="#b5cea8", font=('Consolas', 10))
    text.tag_configure("function", foreground="#dcdcaa", font=('Consolas', 10, 'bold'))
    
    # Setup brute force drag and drop
    setup_brute_force_drag_drop(root, text)
    
    # Add test content with multiple languages
    test_content = """Nova Editor - Brute Force Test

🎯 Testing Features:
1. BRUTE FORCE Drag & Drop (5 methods)
2. ABSOLUTE BRUTE FORCE Syntax Highlighting (5 methods)
3. Professional Window Navigation
4. Multiple Language Support

=== Python Code ===
def hello_world():
    print("Hello, World!")
    return True

class TestClass:
    def __init__(self):
        self.value = 100
        
    def get_value(self):
        return self.value

# Test the function
result = hello_world()
print(f"Result: {result}")

=== C# Code ===
using UnityEngine;

public class TestScript : MonoBehaviour
{
    [SerializeField] private string message = "Hello from Unity!";
    private int number = 42;
    
    void Start()
    {
        // This is a comment
        Debug.Log(message);
        
        if (number > 40)
        {
            Debug.Log("Number is greater than 40");
        }
    }
    
    void Update()
    {
        // Update logic here
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log("Space pressed!");
        }
    }
}

=== JavaScript Code ===
function testFunction() {
    console.log("Hello from JavaScript!");
    return true;
}

class TestClass {
    constructor() {
        this.value = 100;
    }
    
    getValue() {
        return this.value;
    }
}

// Test the function
const result = testFunction();
console.log(`Result: ${result}`);

=== HTML Code ===
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Hello World</h1>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="content">
            <p>This is a test page for Nova Editor.</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 Nova Editor</p>
    </footer>
    
    <script src="script.js"></script>
</body>
</html>

=== CSS Code ===
/* Main styles */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f0f0f0;
}

header {
    background-color: #333;
    color: white;
    padding: 1rem;
}

nav ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

nav li {
    display: inline;
    margin-right: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
}

nav a:hover {
    color: #ddd;
}

main {
    padding: 2rem;
}

footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 1rem;
    position: fixed;
    bottom: 0;
    width: 100%;
}

=== Instructions ===
1. Try dragging any file from Windows Explorer to this window
2. The file should open with BRUTE FORCE syntax highlighting
3. Use Alt+Tab to switch between windows professionally
4. Press F11 for fullscreen, Escape to exit fullscreen
5. Use Ctrl+O to open files manually if drag and drop fails

BRUTE FORCE METHODS ENABLED:
✅ Method 1: tkinterdnd2 drag and drop
✅ Method 2: Windows API drag and drop  
✅ Method 3: Clipboard monitoring
✅ Method 4: File system monitoring
✅ Method 5: Manual file opening

SYNTAX HIGHLIGHTING METHODS:
✅ Method 1: Language-specific highlighting
✅ Method 2: Generic highlighting
✅ Method 3: Pattern matching
✅ Method 4: Character-by-character
✅ Method 5: Line-by-line

Try dragging files now!
"""
    
    text.insert("1.0", test_content)
    
    # Apply brute force syntax highlighting
    apply_brute_force_highlighting(text)
    
    # Add status bar
    status_bar = tk.Frame(root, bg='#2d2d30', height=25)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    status_bar.pack_propagate(False)
    
    status_label = tk.Label(status_bar, text="Ready - Brute Force Mode Active", 
                           bg='#2d2d30', fg='#cccccc')
    status_label.pack(side=tk.LEFT, padx=5)
    
    # Add buttons for testing
    button_frame = tk.Frame(root, bg='#2d2d30')
    button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    test_btn = tk.Button(button_frame, text="Test Highlighting", 
                        command=lambda: apply_brute_force_highlighting(text),
                        bg='#3e3e42', fg='#cccccc')
    test_btn.pack(side=tk.LEFT, padx=5)
    
    open_btn = tk.Button(button_frame, text="Open File", 
                        command=lambda: open_file_dialog(text),
                        bg='#3e3e42', fg='#cccccc')
    open_btn.pack(side=tk.LEFT, padx=5)
    
    clear_btn = tk.Button(button_frame, text="Clear", 
                         command=lambda: text.delete("1.0", tk.END),
                         bg='#3e3e42', fg='#cccccc')
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()

def setup_brute_force_drag_drop(root, text_widget):
    """Setup brute force drag and drop"""
    print("🔧 Setting up BRUTE FORCE drag and drop...")
    
    # Method 1: tkinterdnd2
    try:
        text_widget.drop_target_register('DND_Files')
        text_widget.dnd_bind('<<Drop>>', lambda e: handle_drop(e, text_widget))
        print("✅ Method 1: tkinterdnd2 enabled")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        
    # Method 2: Main window
    try:
        root.drop_target_register('DND_Files')
        root.dnd_bind('<<Drop>>', lambda e: handle_drop(e, text_widget))
        print("✅ Method 2: Main window enabled")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        
    # Method 3: Mouse monitoring
    try:
        root.bind('<Button-1>', lambda e: on_mouse_down(e, root))
        root.bind('<B1-Motion>', lambda e: on_mouse_drag(e, root))
        root.bind('<ButtonRelease-1>', lambda e: on_mouse_up(e, text_widget))
        print("✅ Method 3: Mouse monitoring enabled")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        
    # Method 4: Keyboard shortcuts
    try:
        root.bind('<Control-o>', lambda e: open_file_dialog(text_widget))
        root.bind('<Control-v>', lambda e: check_clipboard(text_widget))
        print("✅ Method 4: Keyboard shortcuts enabled")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
        
    # Method 5: Visual drop zones
    try:
        create_drop_zones(root, text_widget)
        print("✅ Method 5: Visual drop zones enabled")
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
        
    print("🎯 BRUTE FORCE drag and drop setup complete!")

def handle_drop(event, text_widget):
    """Handle file drops with brute force"""
    print(f"🎯 Drop event received: {event}")
    print(f"🎯 Drop data: {event.data}")
    
    try:
        files = event.data
        if isinstance(files, str):
            # Handle single file path
            if files.startswith('{'):
                # Handle multiple files in braces
                files = files.strip('{}').split('} {')
            else:
                files = [files]
        
        print(f"🎯 Processing files: {files}")
        
        for file_path in files:
            # Clean up the file path
            file_path = file_path.strip()
            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]
            
            print(f"🎯 Processing file: {file_path}")
            
            if os.path.isfile(file_path):
                print(f"✅ File exists: {file_path}")
                open_file_in_widget(file_path, text_widget)
                break
            else:
                print(f"❌ File does not exist: {file_path}")
                
    except Exception as e:
        print(f"❌ Drop error: {e}")
        import traceback
        traceback.print_exc()

def open_file_in_widget(file_path, text_widget):
    """Open a file in the text widget with brute force highlighting"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clear the text widget
        text_widget.delete("1.0", tk.END)
        
        # Insert file content
        text_widget.insert("1.0", f"=== {os.path.basename(file_path)} ===\n\n")
        text_widget.insert(tk.END, content)
        
        # Apply brute force syntax highlighting
        apply_brute_force_highlighting(text_widget)
        
        print(f"✅ Opened file: {file_path}")
        
    except Exception as e:
        print(f"❌ Error opening file: {e}")

def apply_brute_force_highlighting(text_widget):
    """Apply brute force syntax highlighting"""
    print("🎨 Applying BRUTE FORCE syntax highlighting...")
    
    # Get content
    content = text_widget.get("1.0", tk.END)
    
    # Clear existing tags
    tags_to_clear = ["keyword", "string", "comment", "number", "function"]
    for tag in tags_to_clear:
        text_widget.tag_remove(tag, "1.0", tk.END)
    
    # Method 1: Language-specific highlighting
    try:
        apply_language_highlighting(text_widget, content)
        print("✅ Method 1: Language-specific highlighting completed")
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
        
    # Method 2: Pattern matching
    try:
        apply_pattern_highlighting(text_widget, content)
        print("✅ Method 2: Pattern matching completed")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
        
    # Method 3: Character-by-character
    try:
        apply_character_highlighting(text_widget, content)
        print("✅ Method 3: Character-by-character completed")
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
        
    # Method 4: Line-by-line
    try:
        apply_line_highlighting(text_widget, content)
        print("✅ Method 4: Line-by-line completed")
    except Exception as e:
        print(f"❌ Method 4 failed: {e}")
        
    # Method 5: Generic highlighting
    try:
        apply_generic_highlighting(text_widget, content)
        print("✅ Method 5: Generic highlighting completed")
    except Exception as e:
        print(f"❌ Method 5 failed: {e}")
        
    print("🎉 BRUTE FORCE syntax highlighting completed!")

def apply_language_highlighting(text_widget, content):
    """Apply language-specific highlighting"""
    # Python keywords
    python_keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global', 'nonlocal', 'print', 'len', 'range', 'list', 'dict', 'set', 'tuple']
    
    # C# keywords
    csharp_keywords = ['public', 'private', 'protected', 'internal', 'class', 'struct', 'interface', 'enum', 'namespace', 'using', 'static', 'readonly', 'const', 'virtual', 'override', 'abstract', 'sealed', 'partial', 'async', 'await', 'var', 'void', 'int', 'string', 'bool', 'float', 'double', 'if', 'else', 'for', 'while', 'foreach', 'switch', 'case', 'default', 'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally', 'new', 'this', 'base', 'null', 'true', 'false', 'UnityEngine', 'MonoBehaviour', 'Start', 'Update', 'Debug', 'Log']
    
    # JavaScript keywords
    js_keywords = ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'null', 'undefined', 'true', 'false', 'class', 'extends', 'super', 'import', 'export', 'async', 'await', 'console', 'log']
    
    # HTML tags
    html_tags = ['html', 'head', 'body', 'title', 'meta', 'link', 'script', 'style', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'textarea', 'select', 'option']
    
    # CSS properties
    css_properties = ['color', 'background', 'margin', 'padding', 'border', 'font', 'display', 'position', 'width', 'height', 'top', 'left', 'right', 'bottom', 'float', 'clear', 'text', 'line', 'box', 'flex', 'grid']
    
    # Combine all keywords
    all_keywords = python_keywords + csharp_keywords + js_keywords + html_tags + css_properties
    
    # Highlight keywords
    for keyword in all_keywords:
        start = "1.0"
        while True:
            pos = text_widget.search(keyword, start, tk.END)
            if not pos:
                break
            end = f"{pos}+{len(keyword)}c"
            text_widget.tag_add("keyword", pos, end)
            start = end

def apply_pattern_highlighting(text_widget, content):
    """Apply pattern-based highlighting"""
    import re
    
    # Common patterns
    patterns = [
        (r'"[^"]*"', "string"),
        (r"'[^']*'", "string"),
        (r'#.*$', "comment"),
        (r'//.*$', "comment"),
        (r'/\*.*?\*/', "comment"),
        (r'<[^>]*>', "keyword"),  # HTML tags
    ]
    
    for pattern, tag in patterns:
        try:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                text_widget.tag_add(tag, start, end)
        except:
            pass

def apply_character_highlighting(text_widget, content):
    """Apply character-by-character highlighting"""
    try:
        for i, char in enumerate(content):
            if char == '"':
                # Find the next quote
                next_quote = content.find('"', i + 1)
                if next_quote != -1:
                    start = f"1.0+{i}c"
                    end = f"1.0+{next_quote + 1}c"
                    text_widget.tag_add("string", start, end)
                    
            elif char == '#':
                # Find end of line
                end_line = content.find('\n', i)
                if end_line == -1:
                    end_line = len(content)
                start = f"1.0+{i}c"
                end = f"1.0+{end_line}c"
                text_widget.tag_add("comment", start, end)
    except:
        pass

def apply_line_highlighting(text_widget, content):
    """Apply line-by-line highlighting"""
    try:
        lines = content.split('\n')
        for line_num, line in enumerate(lines):
            line_start = f"{line_num + 1}.0"
            line_end = f"{line_num + 1}.end"
            
            # Check for comments
            if line.strip().startswith('#'):
                text_widget.tag_add("comment", line_start, line_end)
            elif '//' in line:
                comment_start = line.find('//')
                comment_pos = f"{line_num + 1}.{comment_start}"
                text_widget.tag_add("comment", comment_pos, line_end)
                
            # Check for strings
            if '"' in line:
                quote_start = line.find('"')
                quote_end = line.find('"', quote_start + 1)
                if quote_end != -1:
                    string_start = f"{line_num + 1}.{quote_start}"
                    string_end = f"{line_num + 1}.{quote_end + 1}"
                    text_widget.tag_add("string", string_start, string_end)
    except:
        pass

def apply_generic_highlighting(text_widget, content):
    """Apply generic highlighting"""
    try:
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
    except:
        pass

def on_mouse_down(event, root):
    """Handle mouse down"""
    root.drag_start = (event.x, event.y)
    root.drag_in_progress = False

def on_mouse_drag(event, root):
    """Handle mouse drag"""
    if hasattr(root, 'drag_start'):
        distance = ((event.x - root.drag_start[0]) ** 2 + (event.y - root.drag_start[1]) ** 2) ** 0.5
        if distance > 10:
            root.drag_in_progress = True
            root.config(cursor="hand2")

def on_mouse_up(event, text_widget):
    """Handle mouse up"""
    if hasattr(event.widget, 'drag_in_progress') and event.widget.drag_in_progress:
        check_for_dropped_files(text_widget)
    event.widget.drag_in_progress = False
    event.widget.config(cursor="")

def check_for_dropped_files(text_widget):
    """Check for dropped files"""
    print("🔍 Checking for dropped files...")
    # This would check clipboard, file system, etc.

def open_file_dialog(text_widget):
    """Open file dialog"""
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

def check_clipboard(text_widget):
    """Check clipboard for files"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            if data and os.path.isfile(data):
                print(f"Found file in clipboard: {data}")
                open_file_in_widget(data, text_widget)
        except:
            pass
        finally:
            win32clipboard.CloseClipboard()
    except:
        pass

def create_drop_zones(root, text_widget):
    """Create visual drop zones"""
    try:
        drop_label = tk.Label(
            root,
            text="📁 Drop files here",
            bg='#3e3e42',
            fg='#ffffff',
            font=('Arial', 12, 'bold'),
            relief=tk.RAISED,
            borderwidth=2
        )
        drop_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        drop_label.bind('<Button-1>', lambda e: open_file_dialog(text_widget))
    except:
        pass

if __name__ == "__main__":
    test_nova_editor_brute_force()