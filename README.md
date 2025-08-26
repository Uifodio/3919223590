# AAA File Manager (Windows)

A modern, developer-focused file manager for Windows 11 with a built-in code editor, ZIP-as-folder navigation, fast search, drag-and-drop to external apps, and a monitored Inbox for quick replace workflows.

## Key Features
- Built-in editor: syntax highlighting, line numbers, autosave, undo/redo, find/replace
- File explorer: tree + list, multi-select, copy/move/rename/delete (Recycle Bin), duplicate
- Multi-window: launch multiple independent windows
- Drag & drop: between windows, to external apps (Unity, VS, browsers), from Inbox
- Progress bars for long operations
- ZIP handling: browse ZIP like folders, open/edit entries, write-back with .bak
- Fast search: by name and in-file content with cancellation
- Recent locations menu
- Monitored Inbox (Downloads by default): drag files into projects quickly
- Dark theme by default
- Settings JSON stored in %APPDATA%\AAAFileManager\settings.json

## Requirements
- Windows 10/11 x64
- .NET 9 SDK (9.0.304 or newer) if building from source

## Quick Start (no IDE)
1. Download or clone this repo to Windows.
2. Double-click `StartAAAFileManager.bat`.
   - First run will build a self-contained `win-x64` app into `dist/AAAFileManager/`.
   - Subsequent runs launch immediately from `dist`.

## Build from Source (CLI)
```bat
cd scripts
publish_win64.bat
```
Then run:
```bat
..\dist\AAAFileManager\AAAFileManager.exe
```

## Build/Run (Visual Studio)
- Open the solution (comingled simple layout):
  - Open folder `src/AAAFileManager` in Visual Studio and set `AAAFileManager` as startup project
  - Press F5 to run (Debug) or Build > Publish for a release package

## Usage Guide
- Left tree: browse drives and folders. Double-click folders in the list to enter.
- Editor Tabs: double-click a text/code file to open. Edits autosave every few seconds and on Save.
- Search: expand Search at bottom of file list to search by name and/or content.
- Drag & Drop:
  - From file list to: desktop, apps (Unity/VS/Browser), or another AAA window.
  - Into file list: copies into the current folder. If a single target file is selected, dropping a file replaces it with a `.bak` backup.
  - Inbox pane: shows latest files from your monitored folder (default Downloads). Drag from Inbox into your project.
- ZIPs:
  - Double-click a `.zip` file to open it like a folder.
  - Double-click an entry to edit; saves write back into the ZIP with a `.bak` of the zip.
  - Paste or drop files into a ZIP view to add/update entries.

## Settings
- Config file: `%APPDATA%\AAAFileManager\settings.json`
- Options: theme, editor font size, monitored folder path, recent items count.

## Notes / Limits
- Rename/Delete inside ZIP is not implemented in this version.
- Content search of ZIP extracts to temp to scan.

## Folder Structure
```
/StartAAAFileManager.bat
/scripts/publish_win64.bat
/src/AAAFileManager/
  AAAFileManager.csproj
  App.xaml / App.xaml.cs
  MainWindow.xaml / MainWindow.xaml.cs
  Controls/
    EditorTab.xaml (+ .cs)
    SearchPane.xaml (+ .cs)
  Models/
    FileItem.cs
  Services/
    FileOperationService.cs
    SettingsService.cs
    PathUtils.cs
    ZipFileSystem.cs
  Themes/
    Dark.xaml
```

## License
MIT