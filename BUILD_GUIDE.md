# 🚀 Super File Manager - Build Guide

## 📋 Prerequisites

Before building Super File Manager, ensure you have the following installed:

### Required Software
- **Node.js 16+** - Download from [https://nodejs.org/](https://nodejs.org/)
- **npm** - Usually comes with Node.js

### Optional Software
- **Git** - For version control (optional but recommended)

## 🛠️ Automated Build Process

### Windows Users
1. **Download the project** from GitHub
2. **Extract the ZIP file** to a folder
3. **Double-click `build.bat`** - That's it!

The script will automatically:
- ✅ Check if Node.js is installed
- ✅ Verify project structure
- ✅ Clean previous builds
- ✅ Install all dependencies
- ✅ Build the React application
- ✅ Package the Electron app
- ✅ Open the output folder

### Linux/macOS Users
1. **Download the project** from GitHub
2. **Extract the ZIP file** to a folder
3. **Open terminal** in the project folder
4. **Run**: `./build.sh`

The script will automatically handle everything just like the Windows version.

## 📊 Build Process Details

### Step-by-Step Breakdown

| Step | Description | Duration |
|------|-------------|----------|
| 1/8 | Check Node.js & npm installation | ~5 seconds |
| 2/8 | Verify project structure | ~2 seconds |
| 3/8 | Clean previous builds | ~10 seconds |
| 4/8 | Install dependencies | ~2-5 minutes |
| 5/8 | Verify critical dependencies | ~5 seconds |
| 6/8 | Build React application | ~30-60 seconds |
| 7/8 | Build Electron application | ~1-3 minutes |
| 8/8 | Verify build output | ~5 seconds |

### Expected Output Files

After successful build, you'll find these files in the `dist/` folder:

#### Windows
- `Super File Manager Setup X.X.X.exe` - Installer
- `win-unpacked/` - Portable version

#### Linux
- `Super File Manager-X.X.X.AppImage` - AppImage
- `linux-unpacked/` - Portable version

#### macOS
- `Super File Manager-X.X.X.dmg` - DMG installer
- `mac/` - Portable version

## 🔍 Troubleshooting

### Common Issues & Solutions

#### ❌ "Node.js is not installed"
**Solution**: Download and install Node.js from [https://nodejs.org/](https://nodejs.org/)

#### ❌ "npm is not available"
**Solution**: Reinstall Node.js (npm comes with it)

#### ❌ "package.json not found"
**Solution**: Make sure you're running the script from the project root directory

#### ❌ "Build output not found"
**Solution**: Check the log file for detailed error messages

#### ❌ "Dependencies failed to install"
**Solution**: 
- Check your internet connection
- Try running `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then run build again

#### ❌ "Electron build failed"
**Solution**:
- Ensure you have sufficient disk space (at least 2GB free)
- Check if antivirus is blocking the build process
- Try running as administrator (Windows)

### Log Files

Both build scripts create detailed log files:
- **Windows**: `build_log_YYYYMMDD_HHMMSS.txt`
- **Linux/macOS**: `build_log_YYYYMMDD_HHMMSS.txt`

These logs contain:
- ✅ All command outputs
- ✅ Error messages
- ✅ Build timestamps
- ✅ System information

## 🎯 Manual Build Process

If you prefer to build manually or need to troubleshoot:

### 1. Install Dependencies
```bash
npm install
```

### 2. Build React App
```bash
npm run build
```

### 3. Build Electron App
```bash
npm run build:electron
```

### 4. Platform-Specific Builds
```bash
# Windows
npm run dist:win

# Linux
npm run dist:linux

# macOS
npm run dist:mac

# All platforms
npm run dist
```

## 🔧 Development Mode

For development and testing:

```bash
# Start development server
npm run dev

# This will:
# - Start Vite dev server on port 5173
# - Launch Electron with hot reload
# - Open DevTools automatically
```

## 📦 Build Configuration

The build process uses these configuration files:

- `package.json` - Dependencies and scripts
- `vite.config.js` - Vite build configuration
- `electron.main.js` - Electron main process
- `electron-builder` - Packaging configuration

## 🎮 Unity Integration Setup

After building, set up Unity integration:

1. **Open Unity**
2. **Go to**: Edit → Preferences → External Tools
3. **Set "External Script Editor"** to the Super File Manager executable
4. **Unity scripts will now open** in Super File Manager

## 📱 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Node.js**: 16.0.0+

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **RAM**: 8GB
- **Storage**: 5GB free space
- **Node.js**: 18.0.0+

## 🆘 Getting Help

If you encounter issues:

1. **Check the log file** for detailed error messages
2. **Verify prerequisites** are installed correctly
3. **Try the manual build process** to isolate the issue
4. **Check system requirements** match your setup

## 🎉 Success Indicators

When the build completes successfully, you'll see:

```
========================================
  BUILD COMPLETED SUCCESSFULLY!
========================================

✓ Node.js: v18.17.0
✓ npm: 9.6.7
✓ Dependencies: Installed
✓ React Build: Completed
✓ Electron Build: Completed
✓ Build Output: Found

Build artifacts are in the 'dist' directory
```

---

**🎯 Ready to build? Just run `build.bat` (Windows) or `./build.sh` (Linux/macOS)!**