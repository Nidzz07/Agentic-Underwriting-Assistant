import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// deploy-config (U23) — the Vite build config the frozen frontend deferred here (package.json
// D6: "Bundler/dev-server + Vercel topology deferred to deploy-config"). `vite` is already
// installed (transitive via vitest) — NO new dependency. Produces the static `dist` bundle Vercel
// serves. The frozen `src/app/*` units are composed by `main.jsx`, never edited.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
  // Local-dev-only proxy (wiring pass Q2(a)). `vite build` ignores `server.*`, so nothing ships
  // and vercel.json's production rewrite is untouched — this is the LOCAL analogue of that rewrite.
  // ⚑ rewrite is mandatory: backend routes carry NO `/api` prefix (main.jsx sends `/api/session`,
  // backend serves `/session`), so without the strip every route 404s. Target is 127.0.0.1, NOT
  // localhost: on Windows, Node resolves localhost to IPv6 ::1 first while uvicorn binds IPv4,
  // giving an ECONNREFUSED that reads exactly like "backend is down".
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
});
