# 🎯 Make Anora Editor Your Default Code Editor

## 🚀 **Complete Setup Guide**

This guide will make Anora Editor your default editor for all code files, replacing Visual Studio and other editors.

## 📋 **Step-by-Step Installation**

### **Step 1: Build the Application**
```bash
# Build the Windows version
python3 build_windows.py
```

### **Step 2: Create the Installer**
```bash
# Create Windows installer with registry associations
python3 install_windows.py
```

### **Step 3: Install as Administrator**
1. Right-click `install_anora_windows.bat`
2. Select "Run as administrator"
3. Follow the installation prompts

## 🎯 **What the Installer Does**

### **File Associations Registered:**
- **Python**: `.py` files
- **C#**: `.cs` files (Unity scripts)
- **JavaScript**: `.js` files
- **C/C++**: `.cpp`, `.c`, `.h` files
- **Web**: `.html`, `.css`, `.xml`, `.json` files
- **Config**: `.yml`, `.yaml`, `.toml`, `.ini` files
- **Scripts**: `.sh`, `.bat`, `.ps1` files
- **And 20+ more file types**

### **Windows Integration:**
- ✅ Installs to `C:\Program Files\AnoraEditor\`
- ✅ Creates desktop shortcut
- ✅ Creates start menu entry
- ✅ Registers file associations in Windows registry
- ✅ Makes Anora Editor appear in "Open with" menus

## 🎉 **After Installation**

### **Double-Click to Open:**
- Double-click any `.py`, `.cs`, `.js`, `.html` file
- It will automatically open in Anora Editor
- No more Visual Studio!

### **Right-Click Menu:**
- Right-click any code file
- Select "Open with" → "Anora Editor"
- Or "Open with" → "Choose another app" → "Anora Editor"

### **Set as Default:**
1. Right-click any code file
2. Select "Open with" → "Choose another app"
3. Select "Anora Editor"
4. Check "Always use this app to open .[extension] files"
5. Click "OK"

## 🔧 **Manual Registry Setup (Advanced)**

If you want to manually set up file associations:

### **For C# Files (.cs):**
```batch
reg add "HKEY_CLASSES_ROOT\.cs" /ve /d "AnoraEditorCS" /f
reg add "HKEY_CLASSES_ROOT\AnoraEditorCS" /ve /d "Anora Editor - C# File" /f
reg add "HKEY_CLASSES_ROOT\AnoraEditorCS\shell\open\command" /ve /d "\"C:\Program Files\AnoraEditor\AnoraEditor_Windows.exe\" \"%1\"" /f
```

### **For Python Files (.py):**
```batch
reg add "HKEY_CLASSES_ROOT\.py" /ve /d "AnoraEditorPY" /f
reg add "HKEY_CLASSES_ROOT\AnoraEditorPY" /ve /d "Anora Editor - Python File" /f
reg add "HKEY_CLASSES_ROOT\AnoraEditorPY\shell\open\command" /ve /d "\"C:\Program Files\AnoraEditor\AnoraEditor_Windows.exe\" \"%1\"" /f
```

## 🎯 **Unity Integration**

### **Set Anora Editor as Unity's External Editor:**
1. Open Unity
2. Go to Edit → Preferences
3. Select External Tools
4. Set "External Script Editor" to:
   ```
   C:\Program Files\AnoraEditor\AnoraEditor_Windows.exe
   ```
5. Click "Regenerate project files"

### **Benefits:**
- ✅ Double-click scripts in Unity Project window
- ✅ Opens in Anora Editor instead of Visual Studio
- ✅ Fast, lightweight editing
- ✅ Professional syntax highlighting
- ✅ Always on top mode for Unity workflow

## 🔍 **Verify Installation**

### **Check File Associations:**
1. Open File Explorer
2. Navigate to any code file
3. Right-click and check "Open with" menu
4. "Anora Editor" should appear

### **Test Double-Click:**
1. Find any `.py`, `.cs`, or `.js` file
2. Double-click it
3. Should open in Anora Editor

### **Check Registry:**
1. Press `Win + R`
2. Type `regedit`
3. Navigate to `HKEY_CLASSES_ROOT`
4. Look for `AnoraEditor` entries

## 🚀 **Drag & Drop Enhancement**

### **Enhanced Drag & Drop:**
- Drag any file from File Explorer to Anora Editor
- Creates new tab with file name
- Smart tab management (switches to existing if already open)
- Works with multiple files at once

### **From Unity:**
- Drag scripts from Unity Project window to Anora Editor
- Instant editing without Unity's external editor setting

## 🎨 **Professional Features**

### **Syntax Highlighting:**
- **Real-time highlighting** as you type
- **20+ programming languages** supported
- **VS Code-style colors** with proper contrast
- **Language-specific features** (comments, formatting)

### **Code Intelligence:**
- **Auto-detection** of file types
- **Smart indentation** based on language
- **Code formatting** with proper structure
- **Comment toggling** with Ctrl+/

## 🔧 **Troubleshooting**

### **If Files Don't Open:**
1. Run installer as Administrator
2. Check if Anora Editor is in Program Files
3. Verify registry entries
4. Restart File Explorer

### **If Unity Doesn't Use Anora Editor:**
1. Set external editor in Unity preferences
2. Regenerate project files
3. Restart Unity

### **If Drag & Drop Doesn't Work:**
1. Ensure tkinterdnd2 is installed
2. Check Windows permissions
3. Try running as Administrator

## 🎉 **Success Indicators**

You'll know it's working when:
- ✅ Double-clicking `.cs` files opens Anora Editor
- ✅ Right-click shows "Open with Anora Editor"
- ✅ Unity scripts open in Anora Editor
- ✅ Drag & drop creates new tabs instantly
- ✅ Syntax highlighting works beautifully
- ✅ No more Visual Studio for simple edits!

## 🚀 **Pro Tips**

### **Quick Access:**
- Pin Anora Editor to taskbar
- Use Windows search to find "Anora Editor"
- Create keyboard shortcuts

### **Workflow Optimization:**
- Use "Always on Top" mode for Unity
- Keep Anora Editor compact for overlay editing
- Use Ctrl+Tab for quick tab switching

---

**🎯 With this setup, Anora Editor becomes your primary code editor, replacing Visual Studio for all your coding needs!**