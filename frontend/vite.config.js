// vite.config.js

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  // Настройка разрешения алиасов для импортов
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  // Настройка сервера разработки
  server: {
    port: 3000,
    // Настройка прокси для API запросов во время разработки
    proxy: {
      '/api': {
        target: 'http://api:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    // Автоматическое открытие браузера при запуске
    open: true,
    // Горячая замена модулей
    hmr: true
  },
  
  // Настройка сборки
  build: {
    // Генерация source maps
    sourcemap: true,
    // Настройка минификации
    minify: 'terser',
    // Целевые браузеры
    target: 'es2015',
    // Выходная директория
    outDir: 'dist'
  }
});