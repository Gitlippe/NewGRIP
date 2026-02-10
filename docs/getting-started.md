# Getting Started

## Prerequisites

- Python 3.10+
- Node.js 20+
- `pnpm`

## Start Engine

```bash
cd services/engine
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn newgrip_engine.app:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Start Web UI

```bash
cd apps/web
pnpm install --no-frozen-lockfile
pnpm dev --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`.

## First Run

1. Click `Validate`.
2. Click `Run Preview`.
3. Confirm:
   - trace panel shows successful node execution
   - preview panel shows stage outputs
   - output cards reflect distinct processing stages

## Connect Mode

Click any output handle (colored circle on the right side of a node) to enter
connect mode. The operation palette filters to show only compatible operations.
Click an operation to automatically add it to the graph, connect it to the
source output, and fit the view. Click the canvas background to exit connect
mode.

## Multi-Output Nodes

Operations like Find Contours, Convex Hulls, and Find Lines produce multiple
outputs (image + structured JSON metadata). Each output has its own handle,
color-coded blue for image and amber for JSON. Connecting a JSON output to an
image input highlights the edge and target node in red to indicate the type
mismatch.

## Verify Full Stack

```bash
cd services/engine
source .venv/bin/activate
pytest

cd ../../apps/web
pnpm typecheck && pnpm test && pnpm build

cd ..
python3 scripts/run_backend_artifact_validation.py
node scripts/run_visual_audit.mjs
```

## Artifact Interpretation

- `backend-artifact-report.json`
  - one section per fixture pipeline
  - includes output keys, trace count, and output hashes
- `visual-audit-report.json`
  - desktop/tablet/mobile viewport results
  - preview card counts, trace counts, canvas dimensions
  - screenshot paths for visual inspection
