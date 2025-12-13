import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",       // dossier de build
    emptyOutDir: true,    // vider le dossier avant build
  },
  base: "/",              // base URL de l'app
  server: {
    port: 5173,           // port dev (optionnel)
    proxy: {
      // Proxy pour les appels API vers le backend FastAPI
      "/api": {
        target: "http://localhost:8000", // ton backend local
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
