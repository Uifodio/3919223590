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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
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
            background: rgba(30, 41, 59, 0.8);
            padding: 3rem;
            border-radius: 1rem;
            backdrop-filter: blur(10px);
            border: 1px solid #334155;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        p {
            font-size: 1.25rem;
            margin-bottom: 2rem;
            color: #cbd5e1;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .feature {
            background: rgba(51, 65, 85, 0.5);
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #475569;
        }
        .feature h3 {
            margin-top: 0;
            color: #6366f1;
        }
        .status {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: 600;
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Demo Website</h1>
        <p>This is a sample website created by Modern Server Administrator</p>
        <div class="status">Server Running Successfully</div>
        
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
    
    # Create sample CSS file
    css_content = """/* Demo CSS File - Modern Server Administrator */
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    margin: 0;
    padding: 2rem;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: var(--bg-secondary);
    padding: 2rem;
    border-radius: 1rem;
    border: 1px solid #334155;
}

.header {
    text-align: center;
    margin-bottom: 3rem;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(45deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

.header p {
    font-size: 1.125rem;
    color: var(--text-secondary);
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.feature {
    background: rgba(51, 65, 85, 0.5);
    padding: 2rem;
    border-radius: 0.75rem;
    border: 1px solid #475569;
    text-align: center;
    transition: transform 0.3s ease;
}

.feature:hover {
    transform: translateY(-4px);
}

.feature h3 {
    color: var(--primary);
    margin-bottom: 1rem;
    font-size: 1.25rem;
}

.feature p {
    color: var(--text-secondary);
    font-size: 0.875rem;
}"""
    
    with open(os.path.join(demo_folder, "style.css"), "w") as f:
        f.write(css_content)
    
    # Create sample JavaScript file
    js_content = """// Demo JavaScript File - Modern Server Administrator
console.log('Modern Server Administrator - Demo Script Loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded successfully');
    
    // Add interactive features
    const features = document.querySelectorAll('.feature');
    features.forEach(feature => {
        feature.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Add loading animation
    const status = document.querySelector('.status');
    if (status) {
        status.style.animation = 'pulse 2s infinite';
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
`;
document.head.appendChild(style);"""
    
    with open(os.path.join(demo_folder, "script.js"), "w") as f:
        f.write(js_content)
    
    # Create a sample text file
    with open(os.path.join(demo_folder, "readme.txt"), "w") as f:
        f.write("""Modern Server Administrator - Demo Files
========================================

This folder contains sample files to test the server functionality:

- index.html: Main demo webpage with modern design
- index.php: PHP demo page with server information
- style.css: Modern CSS with custom properties
- script.js: Interactive JavaScript features
- readme.txt: This file

You can test different server types:
- PHP Server: For PHP applications
- HTTP Server: For static websites
- Node.js Server: For JavaScript applications

The server will serve all files in this directory.
Access your server at: http://localhost:[PORT]
""")
    
    print(f"✓ Demo website created in '{demo_folder}' folder")
    print(f"✓ Created sample files: index.html, index.php, style.css, script.js, readme.txt")
    
    return demo_folder

def create_startup_script():
    """Create a startup script for easy launching"""
    startup_content = """#!/bin/bash
# Modern Server Administrator - Startup Script

echo "🚀 Modern Server Administrator - Professional Edition"
echo "======================================================"
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

# Check PHP availability
echo "Checking PHP availability..."
if command -v php &> /dev/null; then
    echo "✓ PHP found: $(php --version | head -n1)"
else
    echo "⚠️  PHP not found - PHP servers will not work"
    echo "   Install PHP to enable PHP server support"
fi

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
    print("🚀 Modern Server Administrator - Professional Demo Setup")
    print("=" * 60)
    
    # Create demo structure
    demo_folder = create_demo_structure()
    
    # Create startup script
    create_startup_script()
    
    print("\n" + "=" * 60)
    print("🎉 Demo setup complete!")
    print("\nTo start the application:")
    print("1. Run: python3 web_server_admin.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Or use the startup script: ./start.sh")
    print("\nDemo website folder:", demo_folder)
    print("You can use this folder to test the server functionality.")
    print("\nRecommended test:")
    print("- Select the demo_website folder")
    print("- Choose port 8000")
    print("- Select 'PHP Server' type")
    print("- Click 'Add Server'")
    print("- Click 'Open Browser' to view your PHP site")

if __name__ == "__main__":
    main()