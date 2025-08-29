# 2D Animation Application - Unity Project

A comprehensive 2D animation application built in Unity with full-featured drawing tools, timeline management, and export capabilities.

## 🎨 Features

### Core Drawing Features
- **Freehand brush** with pen pressure sensitivity
- **Onion skinning** (previous & next frame visibility)
- **Custom brushes** (size, opacity, hardness, texture)
- **Multiple tools**: Eraser, fill bucket, transform (move/scale/rotate)
- **Selection tools** (lasso, rectangle, magic wand)
- **Canvas navigation**: Zoom, pan, rotate with multitouch or hotkeys

### Timeline & Layers
- **Frame-by-frame timeline** with frame exposure controls
- **Multiple layers** (bitmap & vector)
- **Layer blending modes** (normal, multiply, add, etc.)
- **Keyframe system** (insert, duplicate, delete, drag)
- **Onion skin toggles** (before/after frame count)
- **Playback controls** (play, pause, loop, FPS adjustment)

### Audio Support
- **Import audio files** (WAV/MP3/AIFF)
- **Display audio waveform** in timeline
- **Frame-accurate audio playback** with scrubbing
- **Sync animation** to dialogue/music

### Exporting
- **Multiple formats**: MP4, MOV, AVI, PNG sequence, JPEG sequence, GIF, XFL
- **Export settings**: Resolution scaling, transparent background, frame rate selection
- **Render range** (entire timeline or selection)

### User Experience
- **Undo/redo system**
- **Customizable keyboard shortcuts**
- **Autosave & crash recovery**
- **Cross-platform support** (Windows, macOS, iOS, Android)
- **Multi-touch gestures** for tablets
- **Adjustable canvas background color**
- **Dockable/undockable panels**

## 🏗️ Project Structure

```
AnimationApp/
├── Assets/
│   ├── Scripts/
│   │   ├── Core/           # Main application logic
│   │   ├── Drawing/        # Drawing tools and canvas management
│   │   ├── Timeline/       # Timeline and layer management
│   │   ├── Audio/          # Audio playback and waveform
│   │   ├── Export/         # Export functionality
│   │   ├── UI/             # User interface components
│   │   └── Utils/          # Utility scripts
│   ├── Scenes/             # Unity scenes
│   ├── Prefabs/            # UI prefabs
│   ├── Materials/          # Shaders and materials
│   ├── Textures/           # Textures and sprites
│   ├── Audio/              # Audio files
│   └── Animations/         # Animation clips
└── ProjectSettings/        # Unity project settings
```

## 🚀 Getting Started

### Prerequisites
- Unity 2022.3.21f1 or later
- .NET 4.x or later

### Installation
1. Clone or download this repository
2. Open the project in Unity
3. Open the `MainScene` in `Assets/Scenes/`
4. Press Play to start the application

### Basic Usage
1. **Drawing**: Select the brush tool and draw on the canvas
2. **Timeline**: Use the timeline panel to navigate between frames
3. **Layers**: Create and manage layers in the properties panel
4. **Playback**: Use the playback controls to preview your animation
5. **Export**: Use the export window to save your animation

## 🎯 Key Components

### Core Systems
- **AnimationApp**: Main application controller
- **CanvasManager**: Handles drawing canvas and frame management
- **TimelineManager**: Manages timeline, playback, and onion skinning
- **LayerManager**: Handles layer creation, visibility, and blending
- **ToolManager**: Manages drawing tools and their settings
- **AudioManager**: Handles audio playback and waveform display
- **ExportManager**: Manages export functionality

### Drawing Tools
- **BrushTool**: Freehand drawing with customizable brushes
- **EraserTool**: Erase areas with different eraser types
- **FillTool**: Flood fill and pattern fill
- **TransformTool**: Move, scale, and rotate selections
- **SelectionTool**: Rectangle, lasso, and magic wand selection
- **HandTool**: Pan the canvas
- **ZoomTool**: Zoom in/out on the canvas

### UI Components
- **MainMenuBar**: File, edit, view, layer, timeline, window, help menus
- **ToolbarPanel**: Quick access to tools and actions
- **TimelinePanel**: Frame navigation and playback controls
- **PropertiesPanel**: Layer management and properties
- **StatusBar**: Current tool, frame info, zoom level, status

## 🎨 Customization

### Adding New Tools
1. Create a new tool class inheriting from `MonoBehaviour`
2. Implement the required methods (`Initialize`, `OnMouseDown`, etc.)
3. Add the tool to the `ToolManager`
4. Create UI components for the tool settings

### Adding New Export Formats
1. Create a new export method in `ExportManager`
2. Implement the export logic
3. Add the format to the `ExportFormat` enum
4. Update the export window UI

### Custom Brushes
1. Create brush textures in the `Textures` folder
2. Assign textures to the `BrushTool`
3. Adjust brush settings (size, opacity, hardness)

## 🔧 Performance Optimizations

- **GPU-accelerated brush strokes** and playback
- **Memory optimization** for handling thousands of frames
- **Multi-threaded exporting** and preview rendering
- **Optimized caching** for onion skinning and playback

## 📱 Platform Support

- **Windows**: Full support with keyboard and mouse input
- **macOS**: Full support with keyboard and mouse input
- **iOS**: Touch-optimized interface with gesture support
- **Android**: Touch-optimized interface with gesture support

## 🐛 Known Issues

- Some advanced brush features require additional shader implementation
- Export to XFL format is placeholder (requires Flash/Animate integration)
- Multi-touch gestures need platform-specific implementation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Unity Technologies for the Unity engine
- The open-source community for inspiration and resources
- All contributors and testers

---

**Note**: This is a comprehensive 2D animation application with professional-grade features. The codebase is structured for extensibility and maintainability, making it easy to add new features or customize existing ones.
