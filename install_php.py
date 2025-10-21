#!/usr/bin/env python3
"""
PHP Installation Script for Server Administrator
Downloads and installs PHP directly to the workspace
"""

import os
import sys
import urllib.request
import ssl
import zipfile
import tempfile
import shutil

def install_php():
    """Install PHP directly to the workspace"""
    print("🐘 Installing PHP for Server Administrator...")
    
    # Create php directory
    php_dir = os.path.join(os.getcwd(), 'php')
    if not os.path.exists(php_dir):
        os.makedirs(php_dir)
    
    # Try multiple PHP sources
    php_sources = [
        {
            'name': 'PHP 8.2.12 (Official)',
            'url': 'https://windows.php.net/downloads/releases/php-8.2.12-Win32-vs16-x64.zip',
            'filename': 'php-8.2.12-Win32-vs16-x64.zip'
        },
        {
            'name': 'PHP 8.1.25 (Official)',
            'url': 'https://windows.php.net/downloads/releases/php-8.1.25-Win32-vs16-x64.zip',
            'filename': 'php-8.1.25-Win32-vs16-x64.zip'
        },
        {
            'name': 'PHP 8.0.30 (Official)',
            'url': 'https://windows.php.net/downloads/releases/php-8.0.30-Win32-vs16-x64.zip',
            'filename': 'php-8.0.30-Win32-vs16-x64.zip'
        }
    ]
    
    for source in php_sources:
        try:
            print(f"📥 Trying {source['name']}...")
            
            # Create SSL context to ignore certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Download PHP
            php_zip_path = os.path.join(php_dir, source['filename'])
            
            try:
                with urllib.request.urlopen(source['url'], context=ssl_context, timeout=30) as response:
                    with open(php_zip_path, 'wb') as f:
                        f.write(response.read())
                print(f"✅ Downloaded {source['filename']}")
            except Exception as e:
                print(f"❌ Failed to download {source['name']}: {str(e)}")
                continue
            
            # Extract PHP
            try:
                with zipfile.ZipFile(php_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(php_dir)
                print(f"✅ Extracted {source['filename']}")
            except Exception as e:
                print(f"❌ Failed to extract {source['filename']}: {str(e)}")
                continue
            
            # Find PHP directory
            php_extracted_dir = None
            for item in os.listdir(php_dir):
                if item.startswith('php-') and os.path.isdir(os.path.join(php_dir, item)):
                    php_extracted_dir = os.path.join(php_dir, item)
                    break
            
            if not php_extracted_dir:
                print(f"❌ Could not find PHP directory in {source['filename']}")
                continue
            
            # Move PHP files to php directory
            for item in os.listdir(php_extracted_dir):
                src = os.path.join(php_extracted_dir, item)
                dst = os.path.join(php_dir, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Clean up extracted directory
            shutil.rmtree(php_extracted_dir)
            os.remove(php_zip_path)
            
            # Test PHP installation
            php_exe = os.path.join(php_dir, 'php.exe')
            if os.path.exists(php_exe):
                print(f"✅ PHP installed successfully!")
                print(f"📍 PHP location: {php_exe}")
                
                # Test PHP
                try:
                    import subprocess
                    result = subprocess.run([php_exe, '--version'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"🎉 PHP working: {result.stdout.split()[1]}")
                        return True
                    else:
                        print(f"⚠️  PHP installed but not working properly")
                        continue
                except Exception as e:
                    print(f"⚠️  PHP installed but test failed: {str(e)}")
                    continue
            else:
                print(f"❌ PHP executable not found after installation")
                continue
                
        except Exception as e:
            print(f"❌ Error with {source['name']}: {str(e)}")
            continue
    
    print("❌ All PHP installation attempts failed")
    print("📋 Manual installation required:")
    print("1. Download PHP from: https://windows.php.net/download/")
    print("2. Extract to the 'php' folder in this directory")
    print("3. Ensure php.exe is in the php folder")
    return False

if __name__ == "__main__":
    install_php()