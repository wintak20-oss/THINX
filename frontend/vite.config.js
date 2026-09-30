import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 80,
    strictPort: true,
    watch: {
      usePolling: true,
      interval: 1000
    },
    hmr: {
      // Use websocket port for HMR
      clientPort: 80,
      // Timeout for HMR connection
      timeout: 30000
    }
  },
  // Optimize dependency pre-bundling
  optimizeDeps: {
    exclude: ['vue']
  }
})
