# Deployment

## Static architecture

All inference runs on browser CPU in a Web Worker. This includes PCA source encoding, learned neural context/transition layers, inverse-PCA expression decoding and seeded NB sampling. A Python/FastAPI backend is unnecessary; static hosting supports actual inference. `/health.json` exposes model identity and inference mode.

Local: `npm ci`, `npm run dev`. Production: `npm run build`, `npm run preview`.

## GitHub Pages

1. Create a repository after confirming rights to distribute the derived research model/data. Never commit credentials or restricted assets.
2. Upload the project source, package-lock and public assets. Exclude node_modules,.tools,.cache,.env and local archives.
3. For a repository named `SCA1-WM`, build with `VITE_BASE_PATH=/SCA1-WM/` before `npm run build` (PowerShell: `$env:VITE_BASE_PATH='/SCA1-WM/'`).
4. Publish the `dist` directory using your repository's Pages deployment workflow. Expected configurable URL: `https://YOUR_ACCOUNT.github.io/SCA1-WM/` (placeholder, not a deployed URL).
5. Hash routing keeps all pages valid without server rewrite rules. Model loading uses the configured base path in both main thread and worker.

Generic static hosting can use `VITE_BASE_PATH=./` (default) and publish dist. HTTPS is required for browser WebCrypto outside localhost. No API key or remote inference service is needed.

## Owner-private Sites

The project includes a private Sites identity in `.openai/hosting.json`. Hosting source synchronization and publication must preserve its project ID and owner-private audience. The deployment URL is recorded in `docs/DEPLOYMENT_RESULT.json` once the native publishing tool confirms success. Do not interpret an expected URL as proof of deployment.

## Docker static deployment

```text
docker build -t sca1-wm .
docker run --rm -p8080:80 sca1-wm
```

For remote hosts, terminate HTTPS at your ingress. Container serves static files only; no Python backend, GPU or filesystem access to the original project is required.
