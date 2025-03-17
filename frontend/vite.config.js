import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"
import frappeui from "frappe-ui/vite"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), frappeui()],
  define: {
    "process.env.IS_PREACT": JSON.stringify("true"),
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
      "highlight.js/lib/core": path.resolve(__dirname, "highlight-fix.js"),
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
  server: {
    allowedHosts: ["drivephong.dev"],
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
      "highlight.js",
      "tailwind.config.js",
    ],
  },
})
