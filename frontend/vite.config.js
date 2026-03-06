import { defineConfig } from "vite";

export default defineConfig({
  server: {
    proxy: {
      "/graph": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/login": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
      "/signup": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
