// deploy-config (U23, EPIC-6, Phase 2) — the browser ENTRY the frozen frontend deferred here
// (Scope-A §9: "the frontend cannot run in a browser — no bundler; deploy-config owns that").
//
// This constructs the REAL transport + the five frozen seams and mounts the frozen `App`. It
// IMPORTS the frozen `App` / `seams` / `httpTransport` and edits NONE of them (BR-DEP-1) — `App`
// takes `seams` + `transport` as props and mounts nothing itself, which is exactly the seam this
// entry populates.
//
// CG-DEP-Fold-1 — connectivity: `baseUrl: '/api'` pairs with `vercel.json`'s `/api/:path*`
// rewrite, so the browser makes SAME-ORIGIN requests that Vercel proxies to the Render backend.
// No CORS is needed and `backend/app/main.py` is NOT edited. `baseUrl` is the frozen transport's
// own constructor arg (it defaults to '' but accepts an override) — set here, in deploy-config's
// own entry, never in a frozen module.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app/App.jsx';
import { createSeams } from './app/seams.js';
import { createHttpTransport } from './app/httpTransport.js';

// Stub identity SHAPE (Scope-A's X-User-Id client mirror). A build-time env var, never a value
// committed here. Absent -> the transport sends no header -> the server fail-closes to 401, a
// truthful unauthenticated state (not a crash).
const userId = import.meta.env.VITE_USER_ID;

const transport = createHttpTransport({ baseUrl: '/api', userId });
const seams = createSeams(transport);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App seams={seams} transport={transport} />
  </StrictMode>,
);
