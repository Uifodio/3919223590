@echo off
echo Building Super File Manager...

echo Installing dependencies...
npm install

echo Building React app...
npm run build

echo Building Electron app...
npm run build:electron

echo Build complete!
pause