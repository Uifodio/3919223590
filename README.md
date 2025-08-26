# AAA File Manager (Electron + Vite + React + TypeScript)

Professional Windows file manager with built-in code editor, drag & drop, ZIP, search, and Inbox — now powered by Electron.

## Requirements
- Windows 10/11 x64
- Node.js 20+

## Quick Start (dev)
```bash
npm i
npm run dev
```
- A dev window opens. The renderer is served by Vite, Electron starts automatically.

## Build (Windows)
```bash
npm run dist
```
- Produces an installer under `dist/`.

## Features (Phase 1 implemented)
- File list with multi-select, drag out to external apps, drop-in to copy
- Folder open dialog, quick navigation path input
- Copy with .bak on overwrite, delete to Recycle Bin
- ZIP list/extract/write-back (basic)
- Monaco editor scaffold (tabs, advanced editing coming next)

## Roadmap (Phase 2+)
- Tree view, search (name + content) with cancel
- Built-in editor tabs, autosave, find/replace, syntax highlighting
- Inbox (monitored folder) and quick replace workflow
- Settings JSON + recents, theme switch
- Context menu actions and keyboard shortcuts

## Structure
```
/electron
  main.ts         # Electron main process (window, IPC, fs, zip)
  preload.ts      # Secure bridge APIs exposed to renderer
/src
  main.tsx        # React entry
  renderer/
    App.tsx       # UI shell (toolbar, tree, list, editor, status)
/vite.config.ts   # Vite + electron plugin
/package.json     # scripts: dev/build/dist
```

## Notes
- Drag to external apps uses Electron startDrag and OS file paths.
- ZIP is handled via adm-zip. Large archives may need streaming optimizations later.