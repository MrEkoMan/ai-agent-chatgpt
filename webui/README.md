AI Agent WebUI

This is a small Vite + React + TypeScript frontend intended to interact with the FastAPI backend in the repository root.

Quick start (after Node is installed):

1. cd webui
2. npm install
3. npm run dev

Notes:
- The frontend expects the API to be available at the same origin (same host/port). If the backend runs separately, set up a proxy in `vite.config.ts` or use an absolute URL when calling fetch.
- Login uses POST /v1/login which returns a JSON { token } on success. The token is stored in React context for subsequent calls.
