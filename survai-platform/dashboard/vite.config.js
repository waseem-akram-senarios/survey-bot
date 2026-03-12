import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy API requests to the gateway during development
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        // The gateway has: location /api/ { rewrite ^/api/(.*)$ /pg/api/$1 last; }
        // So /api/surveys/list -> gateway -> /pg/api/surveys/list -> survey-service
      },
    },
  },
})
