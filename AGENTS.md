# AGENTS.md

## Cursor Cloud specific instructions

### Overview

NewGRIP is a monorepo with two independent services:

| Service | Directory | Tech | Port |
|---|---|---|---|
| Engine (backend) | `services/engine` | FastAPI + OpenCV (Python) | 8000 |
| Web UI (frontend) | `apps/web` | React + React Flow (Vite) | 5173 |

No databases, Docker, or external services required. Fully stateless and local-first.

### Running services

**Backend:**
```bash
cd services/engine
source .venv/bin/activate
uvicorn newgrip_engine.app:app --host 127.0.0.1 --port 8000
```

**Frontend:**
```bash
cd apps/web
pnpm dev --host 127.0.0.1 --port 5173
```

### Verification commands

See `README.md` for the full list. Summary:

- Backend lint: `cd services/engine && source .venv/bin/activate && ruff check src tests`
- Backend tests: `cd services/engine && source .venv/bin/activate && pytest`
- Frontend lint: `cd apps/web && pnpm lint`
- Frontend typecheck: `cd apps/web && pnpm typecheck`
- Frontend tests: `cd apps/web && pnpm test`
- Frontend build: `cd apps/web && pnpm build`

### Non-obvious caveats

- The real `pnpm-lock.yaml` is in `apps/web/`, not the root. Always run `pnpm install` from `apps/web/`.
- esbuild requires build script approval. The `pnpm.onlyBuiltDependencies` field in `apps/web/package.json` handles this non-interactively. Do NOT run `pnpm approve-builds` (it's interactive).
- The Python venv is at `services/engine/.venv`. Always activate it before running backend commands.
- `python3-venv` system package may need to be installed if the venv doesn't exist yet (`sudo apt-get install -y python3-venv` or `python3.12-venv`).
- Frontend lint produces 3 warnings (not errors) by default. This is expected.
- The frontend connects to the backend at `http://127.0.0.1:8000` (hardcoded as `API_BASE`).
