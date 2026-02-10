# NewGRIP Examples

The `examples/cases` directory contains focused pipelines that exercise distinct operation groups and UI behaviors.

## Available Cases

1. `01_validation_starter.newgrip.json`
2. `02_threshold_tuning.newgrip.json`
3. `03_blur_denoise.newgrip.json`
4. `04_canny_edges.newgrip.json`
5. `05_parallel_branches.newgrip.json`
6. `06_multi_step_chain.newgrip.json`
7. `07_parameter_sweep_target.newgrip.json`
8. `08_agent_style_starter.newgrip.json`
9. `09_neural_stub_path.newgrip.json`
10. `10_grip_contour_proxy.newgrip.json`

## Input Asset

- `examples/assets/web-test-image.jpg` (internet download fixture)

## Quick Use

Run a case in the engine:

```bash
cd services/engine
source .venv/bin/activate
newgrip run --pipeline ../examples/cases/04_canny_edges.newgrip.json --input ../examples/assets/web-test-image.jpg --artifacts-dir ../.artifacts
```
