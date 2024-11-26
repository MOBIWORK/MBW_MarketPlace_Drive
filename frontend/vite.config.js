import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"
import frappeui from "frappe-ui/vite"
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    frappeui(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true,
      },
      manifest: {
        display: 'standalone',
        name: 'Frappe Drive',
        short_name: 'Frappe Drive',
        start_url: '/drive',
        description:
          'Modern & 100% Open-source Drive',
        icons: [
          {
            src: '/assets/drive/manifest/manifest-icon-192.maskable.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/assets/drive/manifest/manifest-icon-192.maskable.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'maskable',
          },
          {
            src: '/assets/drive/manifest/manifest-icon-512.maskable.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any',
          },
          {
            src: '/assets/drive/manifest/manifest-icon-512.maskable.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      }
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
    },
  },
  build: {
    sourcemap: true,
    outDir: `../${path.basename(path.resolve(".."))}/public/frontend`,
    emptyOutDir: true,
    target: "esnext",
    commonjsOptions: {
      include: [/tailwind.config.js/, /node_modules/],
    },
  },
  optimizeDeps: {
    esbuildOptions: { target: "esnext" },
    include: [
      "frappe-ui",
      "feather-icons",
      "showdown",
      "prosemirror",
      "tiptap",
      "engine.io-client",
      "tailwind.config.js",
    ],
  },
})
