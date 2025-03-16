/// <reference types="node" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src/client'),
        },
    },
    server: {
        port: 5173,
        proxy: {
            '/ws/room': {
                target: 'http://localhost:8000',
                ws: true,
                changeOrigin: true
            }
        }
    }
});
