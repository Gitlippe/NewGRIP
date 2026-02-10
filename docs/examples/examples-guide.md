# Examples Guide

This guide explains what each example demonstrates and how to validate outputs.

## Case Index

### `01_validation_starter.newgrip.json`

- Purpose: smallest valid source -> noop path
- Validate: graph validates and produces two image outputs

### `02_threshold_tuning.newgrip.json`

- Purpose: threshold parameter behavior
- Validate: output becomes binary-like compared with source

### `03_blur_denoise.newgrip.json`

- Purpose: Gaussian blur impact
- Validate: output hashes differ between source and blur stage

### `04_canny_edges.newgrip.json`

- Purpose: edge detection
- Validate: high-contrast edge map appears in output card

### `05_parallel_branches.newgrip.json`

- Purpose: branch execution and multi-output previews
- Validate: two branch outputs exist in run payload

### `06_multi_step_chain.newgrip.json`

- Purpose: chained operations over several steps
- Validate: trace order matches topological node order

### `07_parameter_sweep_target.newgrip.json`

- Purpose: use with `/v1/sweeps`
- Validate: scores return for each tested parameter value

### `08_agent_style_starter.newgrip.json`

- Purpose: mimics generated starter plan shape
- Validate: compatible with `/v1/agent/generate` output schema

### `09_neural_stub_path.newgrip.json`

- Purpose: image -> neural stub JSON output
- Validate: `step-2.out` is structured JSON in outputs

### `10_grip_contour_proxy.newgrip.json`

- Purpose: GRIP-like contour flow proxy
- Validate: contour stages produce materially different image hashes

## Command Example

```bash
cd services/engine
source .venv/bin/activate
newgrip validate --pipeline ../examples/cases/10_grip_contour_proxy.newgrip.json
newgrip run --pipeline ../examples/cases/10_grip_contour_proxy.newgrip.json --input ../examples/assets/web-test-image.jpg --artifacts-dir ../.artifacts
```
