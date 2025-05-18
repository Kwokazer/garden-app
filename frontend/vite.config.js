
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    // Проксирование API запросов к бэкенду FastAPI
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // URL вашего FastAPI сервера
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'), // Оставляем /api в пути
        // Логирование для отладки
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('Проксирование запроса:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('Ответ от сервера:', proxyRes.statusCode, req.url);
          });
        }
      },
    },
    // CORS настройки
    cors: {
      origin: ['http://localhost:3000', 'http://localhost:5173'],
      credentials: true
    }
  },
  // Настройки сборки
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Разделение вендорского кода
          'vendor': ['vue', 'vue-router', 'pinia'],
          'bootstrap': ['bootstrap']
        }
      }
    }
  }
})