#!/usr/bin/env python3
"""
Anora Code Editor - Final Launcher
A professional code editor designed for Unity development
"""

import sys
import os
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        # Try to install pygments
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygments"])
        print("✓ Pygments installed successfully")
    except subprocess.CalledProcessError:
        print("⚠ Pygments installation failed - syntax highlighting will be disabled")
    
    try:
        # Try to install pillow
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        print("✓ Pillow installed successfully")
    except subprocess.CalledProcessError:
        print("⚠ Pillow installation failed - some UI features may be limited")

def create_sample_files():
    """Create sample files for testing"""
    samples = {
        "sample.py": '''#!/usr/bin/env python3
"""
Sample Python file for testing Anora Editor
"""

import os
import sys
from typing import List, Dict

class SampleClass:
    """A sample class to demonstrate syntax highlighting"""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
        
    def add_item(self, item: str) -> None:
        """Add an item to the data list"""
        self.data.append(item)
        print(f"Added {item} to {self.name}")
        
    def get_items(self) -> List[str]:
        """Get all items from the data list"""
        return self.data.copy()

def main():
    """Main function"""
    sample = SampleClass("Test")
    sample.add_item("Hello")
    sample.add_item("World")
    
    for item in sample.get_items():
        print(f"Item: {item}")

if __name__ == "__main__":
    main()
''',
        "sample.cs": '''using System;
using System.Collections.Generic;

namespace SampleProject
{
    public class SampleClass
    {
        private string name;
        private List<string> data;
        
        public SampleClass(string name)
        {
            this.name = name;
            this.data = new List<string>();
        }
        
        public void AddItem(string item)
        {
            data.Add(item);
            Console.WriteLine($"Added {item} to {name}");
        }
        
        public List<string> GetItems()
        {
            return new List<string>(data);
        }
    }
    
    class Program
    {
        static void Main(string[] args)
        {
            var sample = new SampleClass("Test");
            sample.AddItem("Hello");
            sample.AddItem("World");
            
            foreach (var item in sample.GetItems())
            {
                Console.WriteLine($"Item: {item}");
            }
        }
    }
}''',
        "sample.js": '''// Sample JavaScript file for testing Anora Editor

class SampleClass {
    constructor(name) {
        this.name = name;
        this.data = [];
    }
    
    addItem(item) {
        this.data.push(item);
        console.log(`Added ${item} to ${this.name}`);
    }
    
    getItems() {
        return [...this.data];
    }
}

function main() {
    const sample = new SampleClass("Test");
    sample.addItem("Hello");
    sample.addItem("World");
    
    for (const item of sample.getItems()) {
        console.log(`Item: ${item}`);
    }
}

// Run the main function
main();
''',
        "sample.html": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample HTML</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .code-block {
            background: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Anora Editor</h1>
        <p>This is a sample HTML file to test the editor's capabilities.</p>
        
        <h2>Features</h2>
        <ul>
            <li>Syntax highlighting</li>
            <li>Dark theme</li>
            <li>Multiple tabs</li>
            <li>Search and replace</li>
            <li>Professional UI</li>
        </ul>
        
        <div class="code-block">
            <pre><code>
// Sample code block
function hello() {
    console.log("Hello, Anora!");
}
            </code></pre>
        </div>
    </div>
    
    <script>
        // Sample JavaScript
        function showMessage() {
            alert("Anora Editor is working perfectly!");
        }
        
        // Add event listener
        document.addEventListener('DOMContentLoaded', function() {
            console.log("Page loaded successfully");
        });
    </script>
</body>
</html>'''
    }
    
    print("Creating sample files...")
    for filename, content in samples.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Created {filename}")
        else:
            print(f"⚠ {filename} already exists")

def main():
    """Main launcher function"""
    print("Anora Code Editor - Professional Unity Development Editor")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
        
    # Install dependencies
    install_dependencies()
    
    # Create sample files
    create_sample_files()
    
    print("\n" + "=" * 60)
    print("🎉 Setup complete! Launching Anora Editor...")
    print("=" * 60)
    
    # Launch the editor
    try:
        # Import and run the editor
        from anora_editor_advanced import AnoraEditor
        
        print("Starting Anora Editor...")
        print("Features:")
        print("  • Dark theme with VS Code-style colors")
        print("  • Smooth animations and professional UI")
        print("  • Syntax highlighting for multiple languages")
        print("  • Multi-tab support with session persistence")
        print("  • Advanced search and replace")
        print("  • Unity-focused design")
        print()
        
        editor = AnoraEditor()
        editor.run()
        
    except ImportError as e:
        print(f"❌ Error importing editor: {e}")
        print("Make sure anora_editor_advanced.py is in the same directory")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error launching editor: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()