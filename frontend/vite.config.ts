import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import eslint from 'vite-plugin-eslint'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue({
      script: {
        defineModel: true,
        propsDestructure: true,
      },
    }),
    eslint({
      cache: false,
      include: ['src/**/*.vue', 'src/**/*.ts', 'src/**/*.tsx'],
      exclude: ['node_modules', 'dist'],
      failOnWarning: true,
      failOnError: true,
      emitWarning: true,
      emitError: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // 将所有警告转换为错误
        throw new Error(warning.message)
      },
    },
  },
  esbuild: {
    logLevel: 'error',
    logOverride: {
      'this-is-undefined-in-esm': 'error',
      'equals-negative-zero': 'error',
    },
  },
})
