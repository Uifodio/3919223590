# 🔧 Anora Editor - Troubleshooting Guide

## DLL Error Solutions

If you're getting the error "The original 380 could not be located in the dynamic link library", here are the solutions:

### 🎯 **Solution 1: Install Visual C++ Redistributable (Most Common Fix)**

**Download and install Visual C++ Redistributable 2015-2022:**

1. **For 64-bit Windows:**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Run the installer as Administrator

2. **For 32-bit Windows:**
   - Download: https://aka.ms/vs/17/release/vc_redist.x86.exe
   - Run the installer as Administrator

3. **For maximum compatibility, install both versions**

### 🎯 **Solution 2: Use Alternative Build Methods**

Try these different build scripts:

```bash
# Method 1: Alternative build (directory mode - most compatible)
python3 build_exe_alternative.py

# Method 2: Windows-specific build
python3 build_windows.py

# Method 3: Simple build (minimal dependencies)
python3 build_exe.py
```

### 🎯 **Solution 3: Run as Administrator**

1. Right-click on the executable
2. Select "Run as administrator"
3. This often fixes DLL permission issues

### 🎯 **Solution 4: Check Windows Defender/Firewall**

1. **Windows Defender:**
   - Open Windows Security
   - Go to "Virus & threat protection"
   - Click "Manage settings"
   - Add the Anora Editor folder to exclusions

2. **Windows Firewall:**
   - Open Windows Defender Firewall
   - Click "Allow an app or feature through Windows Defender Firewall"
   - Add Anora Editor to the allowed list

### 🎯 **Solution 5: Use Portable Package**

The portable package includes all dependencies and is more reliable:

1. Run: `python3 build_exe_alternative.py`
2. Use the `AnoraEditor_Portable` folder
3. Run `launch_anora.bat` from that folder

### 🎯 **Solution 6: Manual Dependency Installation**

If the above doesn't work, manually install dependencies:

```bash
# Install required packages
pip install pygments
pip install pyinstaller

# Or on Ubuntu/Debian:
sudo apt install python3-pygments python3-tk
```

## 🚀 **Recommended Build Process**

### **Step 1: Try the Windows-Specific Build**
```bash
python3 build_windows.py
```

This creates a Windows-optimized package with:
- Directory mode (more reliable than single file)
- All necessary dependencies included
- Windows-specific launcher
- Comprehensive error handling

### **Step 2: Use the Portable Package**
1. Look for `AnoraEditor_Windows_Package` folder
2. Copy the entire folder to your desired location
3. Run `launch_anora.bat` from that folder

### **Step 3: If Still Having Issues**
1. Install Visual C++ Redistributable (see Solution 1)
2. Run as Administrator
3. Check Windows Defender/Firewall settings

## 🔍 **Diagnostic Information**

### **Check Your System:**
```bash
# Check Python version
python --version

# Check if tkinter is available
python -c "import tkinter; print('Tkinter OK')"

# Check if pygments is available
python -c "import pygments; print('Pygments OK')"
```

### **Common Error Messages and Solutions:**

| Error Message | Solution |
|---------------|----------|
| "The original 380 could not be located" | Install Visual C++ Redistributable |
| "api-ms-win-core-libraryloader-l1-1-0.dll" | Install Visual C++ Redistributable |
| "vcruntime140.dll" | Install Visual C++ Redistributable |
| "msvcp140.dll" | Install Visual C++ Redistributable |
| "Access denied" | Run as Administrator |
| "Windows Defender blocked" | Add to Windows Defender exclusions |
| "Firewall blocked" | Allow through Windows Firewall |

## 🛠️ **Alternative Solutions**

### **Option 1: Run from Source (No Executable)**
```bash
# Install dependencies
pip install pygments

# Run directly
python3 anora_editor.py
```

### **Option 2: Use Python Launcher**
```bash
# Use the smart launcher
python3 launch_anora.py
```

### **Option 3: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv anora_env

# Activate (Windows)
anora_env\Scripts\activate

# Activate (Linux/Mac)
source anora_env/bin/activate

# Install dependencies
pip install pygments

# Run editor
python anora_editor.py
```

## 📞 **Getting Help**

If none of the above solutions work:

1. **Check the error message** - Copy the exact error text
2. **Note your system details:**
   - Windows version
   - Python version
   - Whether you're on 32-bit or 64-bit
3. **Try running from source** first to isolate the issue
4. **Check if it's a PyInstaller issue** or a dependency issue

## 🎯 **Success Indicators**

You'll know it's working when:
- ✅ The editor launches with a dark theme
- ✅ You can create new tabs
- ✅ Syntax highlighting works for C# files
- ✅ The "📌 Pin" button works for always-on-top
- ✅ Search and replace functionality works

## 🚀 **Quick Fix Summary**

**Most likely to work:**
1. Install Visual C++ Redistributable 2015-2022
2. Use `python3 build_windows.py`
3. Run the portable package as Administrator

**If still having issues:**
1. Run from source: `python3 anora_editor.py`
2. Check Windows Defender/Firewall settings
3. Try on a different Windows machine

---

**💡 Remember: The portable package is usually the most reliable option for Windows users!**