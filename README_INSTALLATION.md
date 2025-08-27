# Anora Editor - Installation Guide

## Drag and Drop Feature
✅ **Added**: Drag files from File Explorer directly onto Anora Editor window to open them in new tabs.

## Windows File Associations

### Quick Install (Recommended)
1. **Run PowerShell as Administrator**
2. **Navigate to Anora Editor folder**
3. **Run the enhanced installer**:
   ```powershell
   .\install_windows_default_editor_enhanced.ps1
   ```
4. **Restart File Explorer** or log out/in

### What This Does
- Registers Anora Editor for: `.txt`, `.py`, `.cs`, `.js`, `.html`, `.css`, `.json`, `.c`, `.cpp`, `.h`, `.xml`, `.md`
- Adds "Open with Anora Editor" to right-click context menu
- Sets as default editor for text files
- Enables double-click to open files directly

### Manual Installation (Alternative)
If the enhanced installer doesn't work:
```powershell
.\install_windows_default_editor.ps1
```

## Linux File Associations
```bash
chmod +x install_linux_default_editor.sh
./install_linux_default_editor.sh
```

## Testing File Associations
1. **Double-click** any `.py`, `.cs`, `.js` file in File Explorer
2. **Right-click** file → "Open with Anora Editor"
3. **Drag and drop** files onto Anora Editor window
4. **Command line**: `python3 anora_editor.py file.py`

## Troubleshooting
- **Files don't open**: Restart File Explorer or log out/in
- **Python not found**: Add Python to PATH or use full path in installer
- **Permission denied**: Run PowerShell as Administrator
- **Drag/drop not working**: Ensure TkinterDnD2 is installed (included in requirements)

## Features Now Available
✅ **Drag and Drop**: Drop files onto editor window  
✅ **Double-click**: Open files directly from File Explorer  
✅ **Right-click**: "Open with Anora Editor" context menu  
✅ **Command line**: `anora_editor.py file.py`  
✅ **Multiple files**: Drag multiple files at once  

Your Anora Editor is now a **full Windows application** that integrates seamlessly with File Explorer!