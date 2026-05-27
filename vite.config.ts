import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/users": "http://localhost:8000",
      "/login": "http://localhost:8000",
      "/me": "http://localhost:8000",
      "/characters": "http://localhost:8000",
      "/admin": "http://localhost:8000",
    },
  },
});
