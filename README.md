# NewGRIP

NewGRIP is a local-first, cross-platform OpenCV pipeline builder with:

- visual node graph editing
- real backend execution for core operation groups
- stage artifact generation for each run
- GRIP import support and code generation outputs
- optional agent-assisted pipeline bootstrapping

## Repository Layout

- `apps/web` - React + React Flow visual editor
- `services/engine` - FastAPI + OpenCV execution engine
- `fixtures` - GRIP and pipeline test fixtures
- `examples` - runnable example `.newgrip.json` pipelines and image assets
- `scripts` - automated backend artifact and visual audit harnesses

## Quick Start

### 1) Engine

```bash
cd services/engine
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn newgrip_engine.app:app --host 127.0.0.1 --port 8000
```

### 2) Web UI

```bash
cd apps/web
pnpm install --no-frozen-lockfile
pnpm dev --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`.

## Verification Commands

### Backend

```bash
cd services/engine
source .venv/bin/activate
ruff check src tests
pytest
```

### Frontend

```bash
cd apps/web
pnpm typecheck
pnpm test
pnpm build
```

### Artifact + Visual Validation

```bash
python3 scripts/run_backend_artifact_validation.py
node scripts/run_visual_audit.mjs
```

Outputs are written to `.artifacts/verification`.

## Parity Status (vs GRIP)

| Area | Status | Notes |
|---|---|---|
| DAG validation + deterministic execution | done | Cycle detection, socket type checks, topo order |
| Filtering + threshold + edge operations | done | Real OpenCV execution paths |
| Contours + morphology + color transforms | done | Full OpenCV implementations with structured metadata outputs |
| Multi-input/multi-output sockets | done | 8 operations produce secondary structured data (contours, lines, keypoints, etc.) |
| Socket type mismatch detection | done | Red edges + red node glow on incompatible connections |
| Connect mode (click-to-wire) | done | Click output handle to filter palette to compatible ops, auto-connect on selection |
| Per-stage artifacts and traces | done | Image files + serialized outputs |
| Dynamic operation catalog in UI | done | `/v1/operations` drives palette with input/output socket metadata |
| GRIP import | done | Namespace normalization + migration warnings |
| Code generation (py/java/cpp) | done | Deterministic scaffold output |
| Advanced sources (camera/video) | missing | Roadmap item |

See `docs/parity-matrix.md` for detailed tracking.

## Examples

- Catalog: `examples/README.md`
- Setup/run guide: `docs/getting-started.md`
- Deep usage walkthrough: `docs/examples/examples-guide.md`
