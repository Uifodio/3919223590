# Anora Editor - Installation Guide

This guide will help you install Anora Editor on your system.

## Prerequisites

- **Python 3.7 or higher**
- **Internet connection** (for downloading dependencies)

## Quick Installation

### Windows

1. **Download Python** (if not already installed):
   - Go to https://python.org
   - Download Python 3.7+ for Windows
   - **Important**: Check "Add Python to PATH" during installation

2. **Download Anora Editor**:
   - Extract the ZIP file to any folder
   - Open Command Prompt in that folder

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the editor**:
   ```cmd
   python anora_editor.py
   ```
   Or double-click `run_anora.bat`

### Linux (Ubuntu/Debian)

1. **Install Python and dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   ```

2. **Download and extract Anora Editor**:
   ```bash
   # Extract to your preferred location
   cd /path/to/anora-editor
   ```

3. **Install Python packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Make scripts executable**:
   ```bash
   chmod +x *.sh *.py
   ```

5. **Run the editor**:
   ```bash
   ./run_anora.sh
   ```

### macOS

1. **Install Python** (if not already installed):
   ```bash
   brew install python3
   ```

2. **Install tkinter**:
   ```bash
   brew install python-tk
   ```

3. **Download and extract Anora Editor**:
   ```bash
   cd /path/to/anora-editor
   ```

4. **Install Python packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Make scripts executable**:
   ```bash
   chmod +x *.sh *.py
   ```

6. **Run the editor**:
   ```bash
   ./run_anora.sh
   ```

## File Associations (Optional)

### Windows
Run PowerShell as Administrator:
```powershell
.\install_windows_default_editor.ps1
```

### Linux
```bash
./install_linux_default_editor.sh
```

## Troubleshooting

### "Python not found" Error

**Windows**:
- Make sure Python is added to PATH
- Try `python` or `python3` command
- Reinstall Python with "Add to PATH" checked

**Linux/macOS**:
- Install Python: `sudo apt install python3` (Ubuntu)
- Use `python3` instead of `python`

### "tkinter not available" Error

**Ubuntu/Debian**:
```bash
sudo apt install python3-tk
```

**CentOS/RHEL**:
```bash
sudo yum install python3-tkinter
```

**macOS**:
```bash
brew install python-tk
```

**Windows**:
- Usually included with Python
- Try reinstalling Python

### "pygments not available" Error

```bash
pip install pygments
# or
pip3 install pygments
```

### Permission Errors (Linux/macOS)

```bash
chmod +x *.sh *.py
```

### Virtual Environment (Recommended)

Create a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python3 -m venv anora_env

# Activate it
# Windows:
anora_env\Scripts\activate
# Linux/macOS:
source anora_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run editor
python anora_editor.py
```

## Testing Installation

Run the test script to verify everything works:

```bash
python3 test_anora.py
```

## Manual Installation

If automatic installation fails:

1. **Install Python manually**:
   - Download from https://python.org
   - Follow installation instructions

2. **Install tkinter manually**:
   - See troubleshooting section above

3. **Install pygments manually**:
   ```bash
   pip install pygments
   ```

4. **Test the installation**:
   ```bash
   python3 -c "import tkinter; import pygments; print('All dependencies available!')"
   ```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test script: `python3 test_anora.py`
3. Check Python version: `python3 --version`
4. Verify dependencies: `pip list | grep -E "(tkinter|pygments)"`

## System Requirements

- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **Python**: 3.7 or higher
- **RAM**: 512MB minimum, 2GB recommended
- **Storage**: 50MB free space
- **Display**: 1024x768 minimum resolution

## Performance Tips

- Close unnecessary tabs for better performance
- Use the "Always on Top" feature for Unity integration
- Restart the editor if it becomes slow
- Keep Python and dependencies updated