import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import electron from 'vite-plugin-electron';
import renderer from 'vite-plugin-electron-renderer';

export default defineConfig({
  plugins: [
    react(),
    electron({
      main: {
        entry: 'electron/main.ts',
        vite: { build: { outDir: 'dist-electron/main', minify: false } }
      },
      preload: {
        input: { preload: 'electron/preload.ts' },
        vite: { build: { outDir: 'dist-electron/preload', minify: false } }
      }
    }),
    renderer()
  ],
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});