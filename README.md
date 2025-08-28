# React + Electron Sample Project

A sample desktop application built with React and Electron, demonstrating modern development practices and secure communication between processes.

## Features

- ⚛️ **React 18** with modern hooks and functional components
- 🖥️ **Electron** for cross-platform desktop applications
- 🔒 **Secure preload script** with context isolation
- 🚀 **Hot reload** in development mode
- 📦 **Production build** support with electron-builder
- 🎨 **Modern UI** with responsive design and animations
- 🔧 **TypeScript-ready** structure (can be easily converted)

## Project Structure

```
react-electron-sample/
├── public/
│   ├── electron.js          # Main Electron process
│   ├── preload.js           # Secure preload script
│   └── index.html           # HTML entry point
├── src/
│   ├── App.js               # Main React component
│   ├── App.css              # Component styles
│   ├── index.js             # React entry point
│   └── index.css            # Global styles
├── package.json             # Dependencies and scripts
└── README.md                # This file
```

## Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development mode:**
   ```bash
   npm run electron-dev
   ```
   This will start both the React development server and Electron app.

## Available Scripts

- `npm start` - Start React development server only
- `npm run electron` - Start Electron app (requires built React app)
- `npm run electron-dev` - Start both React dev server and Electron
- `npm run build` - Build React app for production
- `npm run electron-pack` - Package the app for distribution

## Development Workflow

1. **Development Mode:**
   - Run `npm run electron-dev`
   - React app runs on `http://localhost:3000`
   - Electron loads the React app from the dev server
   - Hot reload works for both React and Electron

2. **Production Build:**
   - Run `npm run build` to create production build
   - Run `npm run electron` to test production build
   - Run `npm run electron-pack` to create distributable packages

## Security Features

- **Context Isolation**: Enabled by default
- **Node Integration**: Disabled for security
- **Remote Module**: Disabled
- **Preload Script**: Secure communication bridge between processes

## Communication Between Processes

The app demonstrates secure communication between the main Electron process and React renderer:

- **Main Process** → **Renderer**: Through preload script APIs
- **Renderer** → **Main Process**: Through exposed electronAPI methods

## Building for Distribution

```bash
# Build React app
npm run build

# Package for distribution
npm run electron-pack
```

The packaged app will be available in the `dist/` folder.

## Customization

- Modify `public/electron.js` to change Electron window settings
- Update `public/preload.js` to expose additional APIs
- Customize React components in `src/` folder
- Modify build configuration in `package.json`

## Troubleshooting

- **App won't start**: Ensure all dependencies are installed with `npm install`
- **Electron can't find React app**: Make sure React dev server is running on port 3000
- **Build errors**: Check that all required files exist and paths are correct

## Next Steps

Once you've verified this sample project works:

1. Customize the UI and functionality
2. Add your specific business logic
3. Implement additional Electron features (menus, system tray, etc.)
4. Add testing framework (Jest, React Testing Library)
5. Set up CI/CD pipeline
6. Configure code quality tools (ESLint, Prettier)

## License

This project is open source and available under the MIT License.

