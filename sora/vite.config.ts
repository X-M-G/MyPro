import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
// import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    // vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    // 1. 允许通过 IP 访问（关键），否则默认只支持 localhost
    host: '0.0.0.0',

    // 2. 固定端口，防止自动跳到 5174
    port: 5173,
    strictPort: true,

    // 3. 安全白名单（Vite 5.1+ 新特性）
    // 如果不加这个，通过 Nginx 转发 IP 访问时可能会报 "Invalid Host header"
    allowedHosts: [
      '139.196.201.225',
      '82.156.32.183',     // 确保包含你最新的 IP
      'localhost',
      'www.soragen.cloud',  
      'soragen.cloud',      // 建议加上根域名
    ],

    // 4. Proxy Configuration for Local Development
    // This allows you to use /api locally without Nginx.
    // Requests to http://localhost:5173/api/... will be forwarded to http://127.0.0.1:8000/api/...
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/captcha': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/captcha': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },

      '/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})