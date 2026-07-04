import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev/preview server runs on port 3000 (matches docker-compose + README).
// host: true binds 0.0.0.0 so the container port mapping works.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
  },
  preview: {
    host: true,
    port: 3000,
  },
});
