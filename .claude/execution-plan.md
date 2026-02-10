# NewGRIP Remediation Execution Plan

## Status: READY FOR EXECUTION
Generated: 2026-02-10 from comprehensive verification audit

## Overall Verdict from Audit: "Good but gaps"
The core pipeline engine is genuinely production-quality. Major gaps need fixing.

---

## REPOSITORY LAYOUT

```
/Volumes/git/Experimental/ReGRIP/NewGRIP/
├── services/engine/src/newgrip_engine/   # Python backend (FastAPI + OpenCV)
│   ├── app.py          (141 lines) - FastAPI routes
│   ├── models.py       (119 lines) - Pydantic models
│   ├── operations.py   (277 lines) - OpenCV operation registry (17 real ops + 1 stub)
│   ├── executor.py     (78 lines)  - Pipeline execution engine
│   ├── validator.py    (87 lines)  - DAG validation + topological sort
│   ├── persistence.py  (78 lines)  - JSON save/load + GRIP XML import
│   ├── codegen.py      (54 lines)  - Code generation (Python/Java/C++)
│   ├── agent.py        (53 lines)  - Agent pipeline generation (stub)
│   ├── agent_provider.py (24 lines) - AI provider (pure stub)
│   ├── sweeps.py       (45 lines)  - Parameter sweep
│   ├── parity.py       (34 lines)  - GRIP parity scanner
│   └── cli.py          (83 lines)  - CLI interface
├── services/engine/tests/              # 9 test files, 259 lines, 18 tests all passing
├── services/engine/pyproject.toml
├── services/engine/openapi.yaml
├── apps/web/src/
│   ├── App.tsx         (715 lines) - MONOLITHIC React component
│   ├── App.test.tsx    (12 lines)  - 2 trivial tests
│   ├── main.tsx        (12 lines)  - Entry point
│   └── styles.css      (186 lines) - Dark theme, 3-tier responsive
├── apps/web/package.json               # React 18 + ReactFlow 11 + Vite 6
├── scripts/
│   ├── run_backend_artifact_validation.py
│   └── run_visual_audit.mjs
├── .github/workflows/ci.yml           # 3-job CI pipeline
├── fixtures/pipelines/                 # 4 test pipeline fixtures
├── examples/cases/                     # 10 .newgrip.json examples
├── examples/assets/web-test-image.jpg  # Test image (221KB)
├── docs/parity-matrix.md
├── docs/getting-started.md
└── .artifacts/verification/            # Prior validation reports + screenshots
```

## LEGACY BASELINE
```
/Volumes/git/Experimental/ReGRIP/GRIP/   # Java legacy app
├── core/src/main/java/edu/wpi/grip/core/
│   ├── Pipeline.java                    # Pipeline model
│   ├── operations/CVOperations.java     # 29 raw OpenCV operations
│   └── operations/composite/            # 24 composite operations (53 total)
```

---

## CRITICAL FINDINGS TO FIX (from audit)

### Critical (C1-C2)
1. **Agent/AI is pure stub** - `agent_provider.py` returns string literals, `agent.py` uses keyword matching
2. **Codegen produces comments only** - Generated code has `# step` comments, not real cv2 calls

### High (H1-H3)
3. **Operation parity 17/53 (32%)** - Missing: arithmetic, bitwise, HSL/RGB threshold, find lines/blobs, cascade classifier, crop, resize, normalize, mask, distance transform, watershed, save images, switch, valve
4. **Frontend is 715-line monolith** - Zero component decomposition, 2 trivial tests
5. **No video/camera source** - File-only input

### Medium (M1-M5)
6. **Sweep scoring trivial** - `score = len(run.outputs)` always same
7. **HSV threshold simplified** - Single slider vs GRIP's 6 independent sliders
8. **GRIP import maps all ops to noop** - No operation mapping table
9. **Parity matrix slightly understates** - Some `partial` items are actually `done`
10. **Visual audit Playwright version fragile** - Hardcoded browser version dependency

### Low (L1-L4)
11. **No OpenAPI schemas** - Skeleton only
12. **Frontend lint is no-op** - `echo "lint handled by workspace"`
13. **CI Python 3.11 vs local 3.14**
14. **Frontend fallback executeOp mismatch** - gaussian-blur and median-blur both map to opencv.blur in fallback

---

## EXECUTION PLAN - 6 WORKSTREAMS

### Workstream 1: Operation Parity (HIGHEST IMPACT)
**Goal**: Increase from 17 to ~40 operations, covering all major GRIP categories
**Files**: `operations.py`, `app.py` (catalog updates automatically from registry)

#### 1A: Arithmetic Operations (add 8 ops)
- `opencv.add` → cv2.add
- `opencv.subtract` → cv2.subtract
- `opencv.absdiff` → cv2.absdiff
- `opencv.multiply` → cv2.multiply
- `opencv.divide` → cv2.divide
- `opencv.addWeighted` → cv2.addWeighted (already used internally, expose as op)
- `opencv.min` → cv2.min
- `opencv.max` → cv2.max
Each takes two image inputs and produces one image output.

#### 1B: Bitwise Operations (add 4 ops)
- `opencv.bitwise_and` → cv2.bitwise_and
- `opencv.bitwise_or` → cv2.bitwise_or
- `opencv.bitwise_xor` → cv2.bitwise_xor
- `opencv.bitwise_not` → cv2.bitwise_not

#### 1C: Image Transform Operations (add 6 ops)
- `opencv.crop` → numpy slicing with x,y,w,h params
- `opencv.resize` → cv2.resize with width,height params
- `opencv.flip` → cv2.flip with flipCode param
- `opencv.normalize` → cv2.normalize
- `opencv.extractChannel` → cv2.extractChannel
- `opencv.transpose` → cv2.transpose

#### 1D: Color/Threshold Expansion (add 3 ops)
- `opencv.hslThreshold` → cv2.cvtColor(BGR2HLS) + cv2.inRange with 6 params (H/S/L min+max)
- `opencv.rgbThreshold` → cv2.inRange with 6 params (R/G/B min+max)
- Upgrade existing `opencv.hsvThreshold` to 6 params (H/S/V min+max)

#### 1E: Feature Detection (add 2 ops)
- `opencv.findLines` → cv2.HoughLinesP
- `opencv.findBlobs` → cv2.SimpleBlobDetector

#### 1F: Advanced (add 3 ops)
- `opencv.mask` → cv2.bitwise_and with mask
- `opencv.distanceTransform` → cv2.distanceTransform
- `opencv.watershed` → cv2.watershed

**Tests**: Add `test_new_operations.py` with execution test for each new op
**Validation**: All 10 examples must still pass, new examples for new ops

---

### Workstream 2: Codegen Fix (HIGH IMPACT, LOW EFFORT)
**Goal**: Generated code should contain real OpenCV calls, not just comments
**Files**: `codegen.py`

#### Implementation:
- Map each operation to its actual cv2 call with proper parameters
- Build a codegen template per operation type:
  - `opencv.gaussianBlur` → `current = cv2.GaussianBlur(current, ({kernel}, {kernel}), 0)`
  - `opencv.canny` → `gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY); current = cv2.Canny(gray, {low}, {high})`
  - etc.
- Python codegen should produce runnable script
- Java/C++ codegen should produce compilable code with proper imports
- Update `test_codegen_snapshots.py` to verify generated code contains real calls

---

### Workstream 3: GRIP Import Enhancement (HIGH IMPACT, LOW EFFORT)
**Goal**: Map GRIP operation class names to NewGRIP operation keys
**Files**: `persistence.py`

#### Implementation:
Add mapping dict:
```python
GRIP_OP_MAP = {
    "edu.wpi.grip.core.operations.composite.BlurOperation": "opencv.gaussianBlur",
    "edu.wpi.grip.core.operations.composite.CannyEdgeOperation": "opencv.canny",
    "edu.wpi.grip.core.operations.composite.FindContoursOperation": "opencv.findContours",
    "edu.wpi.grip.core.operations.composite.FilterContoursOperation": "opencv.filterContours",
    "edu.wpi.grip.core.operations.composite.ConvexHullsOperation": "opencv.convexHulls",
    "edu.wpi.grip.core.operations.composite.HSVThresholdOperation": "opencv.hsvThreshold",
    "edu.wpi.grip.core.operations.composite.DesaturateOperation": "opencv.rgbToGray",
    "edu.wpi.grip.core.operations.composite.ResizeOperation": "opencv.resize",
    "edu.wpi.grip.core.operations.composite.CropOperation": "opencv.crop",
    "edu.wpi.grip.core.operations.composite.MaskOperation": "opencv.mask",
    "edu.wpi.grip.core.operations.composite.NormalizeOperation": "opencv.normalize",
    # ... add all mappable operations
}
```
- Replace the `if op.startswith("edu.wpi"): op = "opencv.noop"` with lookup
- Fall back to noop only for truly unmapped operations
- Add test with real GRIP XML samples

---

### Workstream 4: Frontend Decomposition + Tests (MEDIUM IMPACT, MEDIUM EFFORT)
**Goal**: Break monolithic App.tsx into components, add meaningful tests
**Files**: `apps/web/src/`

#### 4A: Component Extraction
Create these files from App.tsx:
- `src/components/OperationPalette.tsx` - Left sidebar with categorized operation buttons
- `src/components/InspectorPanel.tsx` - Right sidebar parameter editor
- `src/components/PreviewPanel.tsx` - Output preview grid + trace list
- `src/components/PipelineCanvas.tsx` - ReactFlow wrapper
- `src/components/PipelineNode.tsx` - Custom node renderer (already exists inline)
- `src/types.ts` - Shared types (ParamSpec, OpTemplate, PipelineDocumentV1, OutputView)
- `src/api.ts` - API client functions (validate, run, loadCatalog)
- `src/utils.ts` - Helper functions (debugLog, toPipeline, outputToViews)

#### 4B: Fix Frontend Bugs
- Fix fallback `executeOp` mismatch: gaussian-blur should map to `opencv.gaussianBlur` not `opencv.blur`
- Fix median-blur should map to `opencv.medianBlur` not `opencv.blur`

#### 4C: Add Real Frontend Tests
- `src/components/__tests__/OperationPalette.test.tsx` - Renders categories, click adds node
- `src/components/__tests__/InspectorPanel.test.tsx` - Renders params, slider/checkbox/select
- `src/api.test.ts` - Mock fetch, test catalog loading, error fallback
- `src/utils.test.ts` - Test toPipeline, outputToViews
- Update App.test.tsx with real rendering test

#### 4D: Add ESLint
- Install and configure `eslint` + `@typescript-eslint`
- Replace no-op lint script with real one

---

### Workstream 5: Sweep Scoring + Minor Fixes (LOW-MEDIUM IMPACT)
**Goal**: Make sweep scoring meaningful, fix minor issues
**Files**: `sweeps.py`, `parity.py`, docs

#### 5A: Meaningful Sweep Scoring
Replace `score = float(len(run.outputs))` with actual metrics:
- For image outputs: compute pixel variance, edge density, or mean intensity
- Score = weighted sum of quality metrics
- Different scoring strategies per operation type

#### 5B: Update Parity Matrix
- Change edge detection from `partial` to `done`
- Change morphology from `partial` to `done`
- Add newly implemented operations
- Add clear "missing" list for operations not yet planned

#### 5C: Fix CI Python Version
- Update ci.yml to use Python 3.12 (compromise between 3.11 and 3.14)

#### 5D: Flesh Out OpenAPI Spec
- Add request/response schemas for all endpoints
- Generate from FastAPI's built-in openapi.json

---

### Workstream 6: End-to-End Verification (REQUIRED FINAL STEP)
**Goal**: Prove all fixes work together
**Files**: scripts, fixtures, examples

#### 6A: Backend Verification
- Run `ruff check src tests` → must pass
- Run `pytest -v` → all tests pass including new ones
- Run `run_backend_artifact_validation.py` → all fixtures pass
- Test all new operations via API

#### 6B: Frontend Verification
- Run `pnpm typecheck` → clean
- Run `pnpm test` → all new tests pass
- Run `pnpm build` → production build succeeds
- Use Chrome browser automation to visually verify:
  - Operation palette shows all new operations grouped by category
  - Adding new ops (crop, resize, bitwise) works
  - Inspector shows correct controls for each param type
  - Run Preview produces distinct images per stage
  - Responsive layout at desktop/tablet/mobile
  - No clipping or truncation issues

#### 6C: Integration Verification
- Import a real GRIP XML file and verify operations map correctly
- Run codegen and verify output is executable Python
- Run parameter sweep and verify scores are meaningful
- Verify all 10+ examples validate and run

---

## TEAM STRUCTURE FOR EXECUTION

### Team Lead (me)
- Create tasks from this plan
- Spawn and coordinate workstream agents
- Review results and handle blockers
- Run final verification

### Agent: backend-ops (Workstream 1)
- Type: general-purpose
- Scope: Add ~26 new operations to operations.py + catalog + tests
- Must run tests after each batch

### Agent: codegen-fix (Workstream 2)
- Type: general-purpose
- Scope: Fix codegen.py to emit real cv2 calls + update tests
- Can run in parallel with backend-ops

### Agent: grip-import (Workstream 3)
- Type: general-purpose
- Scope: Add GRIP operation mapping to persistence.py + tests
- Can run in parallel with others

### Agent: frontend-refactor (Workstream 4)
- Type: general-purpose
- Scope: Decompose App.tsx, fix bugs, add tests, add ESLint
- Can run in parallel with backend work

### Agent: sweep-and-docs (Workstream 5)
- Type: general-purpose
- Scope: Fix sweep scoring, update parity matrix, fix CI, flesh out OpenAPI
- Can run in parallel

### Agent: final-verify (Workstream 6)
- Type: general-purpose
- Scope: Run all verification checks, browser automation for frontend
- Must run AFTER all other workstreams complete

---

## DEPENDENCY GRAPH

```
backend-ops ────────────┐
codegen-fix ────────────┤
grip-import ────────────┼──→ final-verify
frontend-refactor ──────┤
sweep-and-docs ─────────┘
```

All workstreams 1-5 can run in parallel. Workstream 6 depends on all completing.

---

## SUCCESS CRITERIA

1. Operation count: ≥40 (up from 17)
2. All backend tests pass (existing + new)
3. Codegen produces runnable Python code
4. GRIP import maps at least 15 operations (not just noop)
5. Frontend decomposed into ≥5 component files
6. Frontend has ≥10 meaningful tests (up from 2 trivial)
7. Sweep scoring varies across different parameter values
8. All 10 examples validate and run
9. Visual audit shows all new operations in palette
10. No regressions in existing functionality

---

## KEY COMMANDS

```bash
# Backend
cd /Volumes/git/Experimental/ReGRIP/NewGRIP/services/engine
source .venv/bin/activate
ruff check src tests
pytest -v
uvicorn newgrip_engine.app:app --host 127.0.0.1 --port 8000

# Frontend
cd /Volumes/git/Experimental/ReGRIP/NewGRIP/apps/web
pnpm install --no-frozen-lockfile
pnpm typecheck
pnpm test
pnpm build
pnpm dev --host 127.0.0.1 --port 5173

# Validation
cd /Volumes/git/Experimental/ReGRIP/NewGRIP
python3 scripts/run_backend_artifact_validation.py
node scripts/run_visual_audit.mjs

# API testing
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/v1/operations | python3 -m json.tool
```

---

## NOTES

- Browser automation for frontend verification: use `mcp__claude-in-chrome__*` tools
  - Must call `tabs_context_mcp` first, then `update_plan` with domains `["127.0.0.1", "localhost"]`
  - Local URLs may be blocked by extension policy - use Playwright scripts as alternative
- The venv at `services/engine/.venv` is already set up with all deps
- Node modules at `apps/web/node_modules` are already installed
- Python 3.14 is the local version; tests work fine with it
- All existing tests (18 backend, 2 frontend) currently pass
