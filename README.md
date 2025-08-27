# Simple Kivy Counter App

A basic Kivy application that demonstrates a simple counter with increment, decrement, and reset functionality.

## Features

- Simple counter interface
- Increment (+) and decrement (-) buttons
- Reset button
- Clean, modern UI

## Prerequisites

Before running this application, you need to install Python and Kivy on your Windows system.

### Installing Python

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, make sure to check "Add Python to PATH"
3. Verify installation by opening Command Prompt and typing: `python --version`

### Installing Kivy

There are several ways to install Kivy on Windows:

#### Method 1: Using pip (Recommended)
```bash
pip install kivy
```

#### Method 2: Using conda
```bash
conda install kivy -c conda-forge
```

#### Method 3: Using the official Kivy installer
1. Download the Kivy installer from [kivy.org](https://kivy.org/doc/stable/installation/installation-windows.html)
2. Run the installer and follow the instructions

## Running the Application

### Method 1: Direct Python execution
```bash
python main.py
```

### Method 2: Using the requirements file
```bash
pip install -r requirements.txt
python main.py
```

## Compiling to Executable (.exe)

To create a standalone executable file, we'll use PyInstaller. Here's how:

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Create the executable
```bash
pyinstaller --onefile --windowed --name CounterApp main.py
```

#### PyInstaller Options Explained:
- `--onefile`: Creates a single executable file
- `--windowed`: Prevents the console window from appearing (Windows-specific)
- `--name CounterApp`: Sets the name of the output executable

### Step 3: Find your executable
The compiled executable will be in the `dist/` folder. You can run it directly by double-clicking `CounterApp.exe`.

## Alternative Compilation Methods

### Using Auto-py-to-exe (GUI Tool)
1. Install auto-py-to-exe: `pip install auto-py-to-exe`
2. Run: `auto-py-to-exe`
3. Select your `main.py` file
4. Choose "One File" and "Window Based"
5. Click "Convert"

### Using cx_Freeze
1. Install cx_Freeze: `pip install cx_Freeze`
2. Create a `setup.py` file:

```python
from cx_Freeze import setup, Executable

setup(
    name="CounterApp",
    version="1.0",
    description="Simple Kivy Counter App",
    executables=[Executable("main.py", base="Win32GUI")]
)
```

3. Run: `python setup.py build`

## Troubleshooting

### Common Issues:

1. **"No module named 'kivy'" error**
   - Make sure Kivy is properly installed: `pip install kivy`
   - Try reinstalling: `pip uninstall kivy && pip install kivy`

2. **PyInstaller can't find Kivy modules**
   - Use: `pyinstaller --onefile --windowed --hidden-import kivy main.py`

3. **Executable is too large**
   - This is normal for Kivy apps as they include many dependencies
   - Consider using `--onedir` instead of `--onefile` for smaller size

4. **App doesn't start**
   - Try running from command line to see error messages
   - Check if all dependencies are included

### Performance Tips:

- Use `--onedir` instead of `--onefile` for faster startup
- Exclude unnecessary modules with `--exclude-module`
- Use UPX compression: `pip install upx` then add `--upx-dir=path/to/upx`

## Project Structure

```
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── dist/               # Compiled executable (after PyInstaller)
└── build/              # Build files (after PyInstaller)
```

## Next Steps

Once you have this basic app working, you can:

1. Add more complex UI elements
2. Implement data persistence
3. Add animations and transitions
4. Create more sophisticated layouts
5. Add networking capabilities
6. Implement database integration

## Resources

- [Kivy Documentation](https://kivy.org/doc/stable/)
- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Kivy Examples](https://github.com/kivy/kivy/tree/master/examples)
- [KivyMD (Material Design for Kivy)](https://kivymd.readthedocs.io/)