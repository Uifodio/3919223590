#!/usr/bin/env python3
"""
Modern Server Administrator - Demo Script
Creates sample files and demonstrates the application
"""

import os
import shutil
from pathlib import Path

def create_demo_structure():
    """Create demo folder structure and files"""
    print("🚀 Creating demo structure...")
    
    # Create demo website folder
    demo_folder = "demo_website"
    os.makedirs(demo_folder, exist_ok=True)
    
    # Create sample HTML file
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Website - Modern Server Admin</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 30px;
            opacity: 0.9;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .feature h3 {
            margin-top: 0;
            color: #4ecdc4;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Demo Website</h1>
        <p>This is a sample website created by Modern Server Administrator</p>
        <p>Your server is running successfully!</p>
        
        <div class="features">
            <div class="feature">
                <h3>⚡ Fast</h3>
                <p>Lightning fast server performance</p>
            </div>
            <div class="feature">
                <h3>🔒 Secure</h3>
                <p>Built-in security features</p>
            </div>
            <div class="feature">
                <h3>📱 Modern</h3>
                <p>Beautiful, responsive design</p>
            </div>
            <div class="feature">
                <h3>🛠️ Easy</h3>
                <p>Simple server management</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    with open(os.path.join(demo_folder, "index.html"), "w") as f:
        f.write(html_content)
    
    # Create sample PHP file
    php_content = """<?php
echo "<h1>PHP Server Test</h1>";
echo "<p>Current time: " . date('Y-m-d H:i:s') . "</p>";
echo "<p>PHP Version: " . phpversion() . "</p>";
echo "<p>Server is running successfully!</p>";
?>"""
    
    with open(os.path.join(demo_folder, "test.php"), "w") as f:
        f.write(php_content)
    
    # Create sample CSS file
    css_content = """/* Demo CSS File */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f0f0f0;
}

.header {
    background: linear-gradient(45deg, #0078d4, #00bcf2);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.content {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}"""
    
    with open(os.path.join(demo_folder, "style.css"), "w") as f:
        f.write(css_content)
    
    # Create sample JavaScript file
    js_content = """// Demo JavaScript File
console.log('Modern Server Administrator - Demo Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded successfully');
    
    // Add some interactive features
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            alert('Button clicked! Server is working perfectly.');
        });
    });
});"""
    
    with open(os.path.join(demo_folder, "script.js"), "w") as f:
        f.write(js_content)
    
    # Create a sample text file
    with open(os.path.join(demo_folder, "readme.txt"), "w") as f:
        f.write("""Modern Server Administrator - Demo Files
========================================

This folder contains sample files to test the server functionality:

- index.html: Main demo webpage
- test.php: PHP test file (if PHP server is used)
- style.css: CSS stylesheet
- script.js: JavaScript file
- readme.txt: This file

You can upload more files using the Modern Server Administrator interface.
The server will serve all files in this directory.
""")
    
    print(f"✓ Demo website created in '{demo_folder}' folder")
    print(f"✓ Created sample files: index.html, test.php, style.css, script.js, readme.txt")
    
    return demo_folder

def create_startup_script():
    """Create a startup script for easy launching"""
    startup_content = """#!/bin/bash
# Modern Server Administrator - Startup Script

echo "🚀 Modern Server Administrator"
echo "=============================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask, psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
fi

echo "✓ Dependencies ready"

# Create demo folder if it doesn't exist
if [ ! -d "demo_website" ]; then
    echo "Creating demo website..."
    python3 demo.py
fi

echo ""
echo "Starting Modern Server Administrator..."
echo "The application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python3 web_server_admin.py
"""
    
    with open("start.sh", "w") as f:
        f.write(startup_content)
    
    os.chmod("start.sh", 0o755)
    print("✓ Created startup script: start.sh")

def main():
    """Main demo function"""
    print("🚀 Modern Server Administrator - Demo Setup")
    print("=" * 50)
    
    # Create demo structure
    demo_folder = create_demo_structure()
    
    # Create startup script
    create_startup_script()
    
    print("\n" + "=" * 50)
    print("🎉 Demo setup complete!")
    print("\nTo start the application:")
    print("1. Run: python3 web_server_admin.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Or use the startup script: ./start.sh")
    print("\nDemo website folder:", demo_folder)
    print("You can use this folder to test the server functionality.")

if __name__ == "__main__":
    main()