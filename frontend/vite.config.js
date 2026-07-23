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
});
