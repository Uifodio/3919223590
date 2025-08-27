#!/usr/bin/env python3
"""
Test script to verify syntax highlighting works
"""

import tkinter as tk
from tkinter import scrolledtext
import os

def test_syntax_highlighting():
    """Test syntax highlighting with a simple window"""
    
    root = tk.Tk()
    root.title("Syntax Highlighting Test")
    root.geometry("600x400")
    
    # Create text widget
    text = scrolledtext.ScrolledText(
        root,
        bg='#1e1e1e',
        fg='#d4d4d4',
        font=('Consolas', 10),
        wrap=tk.NONE
    )
    text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Configure tags for syntax highlighting
    text.tag_configure("keyword", foreground="#569cd6", font=('Consolas', 10, 'bold'))
    text.tag_configure("string", foreground="#ce9178", font=('Consolas', 10))
    text.tag_configure("comment", foreground="#6a9955", font=('Consolas', 10, 'italic'))
    text.tag_configure("number", foreground="#b5cea8", font=('Consolas', 10))
    text.tag_configure("function", foreground="#dcdcaa", font=('Consolas', 10, 'bold'))
    
    # Sample Python code
    python_code = '''#!/usr/bin/env python3
# This is a Python comment
def hello_world():
    """This is a docstring"""
    message = "Hello, World!"
    number = 42
    if number > 40:
        print(message)
        return True
    else:
        return False

class TestClass:
    def __init__(self):
        self.value = 100
        
    def get_value(self):
        return self.value

# Test the function
result = hello_world()
print(f"Result: {result}")
'''
    
    # Sample C# code
    csharp_code = '''using UnityEngine;

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
'''
    
    # Insert the code
    text.insert("1.0", "=== Python Code ===\n")
    text.insert(tk.END, python_code)
    text.insert(tk.END, "\n\n=== C# Code ===\n")
    text.insert(tk.END, csharp_code)
    
    # Simple syntax highlighting
    def highlight_python():
        # Highlight Python keywords
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'break', 'continue', 'pass', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global', 'nonlocal']
        
        for keyword in keywords:
            start = "2.0"  # Start after the header
            while True:
                pos = text.search(keyword, start, tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                text.tag_add("keyword", pos, end)
                start = end
    
    def highlight_csharp():
        # Highlight C# keywords
        keywords = ['public', 'private', 'protected', 'internal', 'class', 'struct', 'interface', 'enum', 'namespace', 'using', 'static', 'readonly', 'const', 'virtual', 'override', 'abstract', 'sealed', 'partial', 'async', 'await', 'var', 'void', 'int', 'string', 'bool', 'float', 'double', 'if', 'else', 'for', 'while', 'foreach', 'switch', 'case', 'default', 'break', 'continue', 'return', 'throw', 'try', 'catch', 'finally', 'new', 'this', 'base', 'null', 'true', 'false']
        
        # Find the start of C# code
        csharp_start = text.search("=== C# Code ===", "1.0", tk.END)
        if csharp_start:
            start = f"{csharp_start}+1l"
            
            for keyword in keywords:
                current_start = start
                while True:
                    pos = text.search(keyword, current_start, tk.END)
                    if not pos:
                        break
                    end = f"{pos}+{len(keyword)}c"
                    text.tag_add("keyword", pos, end)
                    current_start = end
    
    def highlight_strings():
        # Highlight strings (simple approach)
        start = "1.0"
        while True:
            pos = text.search('"', start, tk.END)
            if not pos:
                break
            # Find the end quote
            end_pos = text.search('"', f"{pos}+1c", tk.END)
            if end_pos:
                end = f"{end_pos}+1c"
                text.tag_add("string", pos, end)
                start = end
            else:
                start = f"{pos}+1c"
    
    def highlight_comments():
        # Highlight comments
        start = "1.0"
        while True:
            pos = text.search('#', start, tk.END)
            if not pos:
                break
            # Find end of line
            line_end = text.index(f"{pos} lineend")
            text.tag_add("comment", pos, line_end)
            start = line_end
    
    # Apply highlighting
    highlight_python()
    highlight_csharp()
    highlight_strings()
    highlight_comments()
    
    # Add a button to test highlighting
    def test_highlight():
        # Clear existing tags
        for tag in ["keyword", "string", "comment", "number", "function"]:
            text.tag_remove(tag, "1.0", tk.END)
        
        # Reapply highlighting
        highlight_python()
        highlight_csharp()
        highlight_strings()
        highlight_comments()
    
    button = tk.Button(root, text="Test Highlighting", command=test_highlight)
    button.pack(pady=5)
    
    print("Syntax highlighting test window opened!")
    print("You should see:")
    print("- Keywords in blue and bold")
    print("- Strings in orange")
    print("- Comments in green and italic")
    
    root.mainloop()

if __name__ == "__main__":
    test_syntax_highlighting()