import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  base: '/', // 生产环境根路径
  build: {
    outDir: 'dist', // 打包输出目录
  },
   server: {
    proxy: {
      // 配置/api前缀的请求代理到后端服务器
      '/api': {
        target: 'http://localhost:5000', // 后端端口
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
         logLevel: 'debug',
      }
    }
  },
  resolve: {
    alias: {
      //'@': fileURLToPath(new URL('./src', import.meta.url)),
      '@': path.resolve(__dirname, 'src') 
    },
  },
})
