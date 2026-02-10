# GRIP to NewGRIP Parity Matrix

This matrix tracks required parity features and current implementation status.

Status legend:

- `done`: Implemented and test-covered in NewGRIP
- `partial`: Implemented with reduced scope or proxy behavior
- `missing`: Not yet implemented

## Core Pipeline Model

| Capability | GRIP Reference | NewGRIP Status |
|---|---|---|
| DAG validation and cycle rejection | `GRIP/core/.../Pipeline.java` | `done` |
| Connection type compatibility | `GRIP/core/.../ConnectionValidator.java` | `done` |
| Deterministic execution ordering | `GRIP/core/.../PipelineRunner.java` | `done` |
| Multi-branch pipelines | `GRIP/core/.../Pipeline.java` | `done` |
| Source + steps + connections serialization | `GRIP/core/.../serialization/Project.java` | `done` |

## Operation Coverage

| Category | GRIP Baseline | NewGRIP Status |
|---|---|---|
| Filtering (blur family) | Blur/Gaussian variants | `done` |
| Thresholding | HSV/RGB/HSL/Threshold ops | `done` |
| Edge detection | Canny/Sobel/Laplacian | `done` |
| Contours | Find/ConvexHull/Filter | `done` (with structured metadata outputs) |
| Morphology | Erode/Dilate | `done` |
| Color transforms | RGB->Gray/HSV/HSL/RGB threshold | `done` |
| Arithmetic ops | Add/Subtract/Multiply/Divide/AddWeighted/Min/Max | `done` |
| Bitwise ops | AND/OR/XOR/NOT | `done` |
| Transform ops | Resize/Flip/Crop/Normalize/ExtractChannel/Transpose | `done` |
| Detection ops | Lines/Blobs | `done` (with structured metadata outputs) |
| Advanced ops | Mask/DistanceTransform/Watershed | `done` (with structured metadata outputs) |
| Neural stub integration | Not primary in GRIP | `done` (stub) |

## Sources, Previews, and Artifacts

| Capability | GRIP Baseline | NewGRIP Status |
|---|---|---|
| Image source | Yes | `done` |
| Video/camera source | Yes | `missing` |
| Per-stage visual preview | Yes | `done` |
| Structured preview (reports) | Yes | `done` (contours, lines, keypoints, distances, segments, thresholds) |
| Stage artifact output | Partial in GRIP ecosystem | `done` |

## Integrations and Tooling

| Capability | GRIP Baseline | NewGRIP Status |
|---|---|---|
| Headless API run | Yes | `done` |
| CLI validate/run/export | Yes | `done` |
| GRIP import compatibility | Yes | `done` (proper operation mapping) |
| Code generation (Python/Java/C++) | Yes | `done` (real cv2 calls) |
| Operation capability endpoint | N/A legacy style | `done` (`/v1/operations`) |
| NetworkTables/ROS publish | Yes | `missing` |

## UI/UX

| Capability | GRIP Baseline | NewGRIP Status |
|---|---|---|
| Node palette by operation categories | Yes | `done` |
| No raw JSON in primary UX | Desired | `done` |
| Responsive desktop/tablet/mobile layout | Better-than-GRIP target | `done` |
| Node/preview visual distinction by operation | Better-than-GRIP target | `done` |
| Multi-input/multi-output socket handles | N/A (GRIP had it) | `done` (color-coded: blue=image, amber=json) |
| Socket type mismatch visual feedback | N/A | `done` (red edges + red node glow) |
| Connect mode (click output to filter palette) | N/A | `done` (auto-connect + fitView) |
| Multi-output inspector (all outputs for node) | N/A | `done` |

## Acceptance Targets

### Must-Have (Current Implementation Push)

1. Core DAG and execution reliability
2. Operation catalog endpoint and dynamic UI palette
3. Real backend processing for blur/threshold/canny and image artifacts
4. GRIP import path and codegen path verified
5. Automated backend/frontend/visual validation

### Stretch

1. Video/camera source parity
2. NetworkTables/ROS publish parity
3. Multi-input node UI (visual multi-input handles for arithmetic/bitwise ops)
