# Quick Start Guide - Kivy Counter App

## 🚀 Get Started in 3 Steps

### Step 1: Setup (Windows)
```bash
# Run the setup script
setup_windows.bat
```

### Step 2: Run the App
```bash
# Activate environment
kivy_env\Scripts\activate.bat

# Run the app
python main.py
```

### Step 3: Compile to EXE
```bash
# Make sure environment is activated
kivy_env\Scripts\activate.bat

# Compile
pyinstaller CounterApp.spec

# Find your exe in dist/CounterApp.exe
```

## 🎯 What You'll See

- A simple counter app with +, -, and Reset buttons
- Clean, modern UI built with Kivy
- Works on Windows, Linux, and Mac

## 🔧 Troubleshooting

**"No module named 'kivy'" error:**
- Make sure you ran the setup script
- Activate the virtual environment: `kivy_env\Scripts\activate.bat`

**App doesn't start:**
- Run `python test_installation.py` to check your setup
- Make sure you're in the virtual environment

**Compilation fails:**
- Install PyInstaller: `pip install pyinstaller`
- Use the spec file: `pyinstaller CounterApp.spec`

## 📁 Files Explained

- `main.py` - The main application
- `setup_windows.bat` - Windows setup script
- `CounterApp.spec` - PyInstaller configuration
- `test_installation.py` - Test your setup
- `debug.py` - Detailed diagnostics

## 🎉 Success!

Once you have this working, you can:
1. Modify `main.py` to add features
2. Create your own Kivy apps
3. Compile any Kivy app to exe using the same process

Happy coding! 🐍