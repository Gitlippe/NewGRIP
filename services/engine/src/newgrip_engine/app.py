from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import generate_pipeline
from .codegen import generate_code
from .executor import execute_pipeline
from .models import (
    CodegenRequest,
    GenerateRequest,
    PipelineDocumentV1,
    RunRequest,
    RunResponse,
    ValidationResponse,
)
from .operations import OperationRegistry
from .persistence import import_grip_xml
from .sweeps import run_parameter_sweep
from .validator import validate_pipeline

app = FastAPI(title="NewGRIP Engine API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ValidateRequest(BaseModel):
    pipeline: PipelineDocumentV1


class ImportGripRequest(BaseModel):
    xml: str


class CodegenResponse(BaseModel):
    filename: str
    content: str


class SweepRequest(BaseModel):
    pipeline: PipelineDocumentV1
    nodeId: str
    parameter: str
    values: list[str | int | float | bool]


class PreviewEvent(BaseModel):
    event: str
    runId: str
    nodeId: str
    timestamp: float
    payload: dict


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/operations")
def operations() -> dict:
    return {
        "operations": [
            {
                "key": desc.key,
                "category": desc.category,
                "label": desc.label,
                "executeOp": desc.execute_op,
                "outputType": desc.output_type,
                "params": [p.model_dump() for p in desc.params],
                "inputs": desc.inputs if desc.inputs is not None else [{"name": "in", "type": "image"}],
                "outputs": desc.outputs if desc.outputs is not None else [{"name": "out", "type": desc.output_type}],
            }
            for desc in OperationRegistry.catalog()
        ]
    }


@app.post("/v1/pipelines/validate", response_model=ValidationResponse)
def validate(req: ValidateRequest) -> ValidationResponse:
    return validate_pipeline(req.pipeline)


@app.post("/v1/pipelines/run", response_model=RunResponse)
def run(req: RunRequest) -> RunResponse:
    result = validate_pipeline(req.pipeline)
    if not result.ok:
        raise HTTPException(status_code=400, detail=result.errors)
    artifacts_root = str(Path(__file__).resolve().parents[4] / ".artifacts")
    return execute_pipeline(
        req.pipeline, req.inputImagePath,
        artifacts_root=artifacts_root,
        input_image_base64=req.inputImageBase64,
    )


@app.post("/v1/projects/import/grip")
def import_grip(req: ImportGripRequest) -> dict:
    pipeline, warnings = import_grip_xml(req.xml)
    return {"pipeline": pipeline.model_dump(by_alias=True), "warnings": warnings}


@app.post("/v1/codegen", response_model=CodegenResponse)
def codegen(req: CodegenRequest) -> CodegenResponse:
    filename, content = generate_code(req.pipeline, req.language, req.className)
    return CodegenResponse(filename=filename, content=content)


@app.post("/v1/agent/generate")
def agent_generate(req: GenerateRequest) -> dict:
    response = generate_pipeline(req)
    return response.model_dump(by_alias=True)


@app.post("/v1/sweeps")
def sweep(req: SweepRequest) -> dict:
    results = run_parameter_sweep(req.pipeline, req.nodeId, req.parameter, list(req.values))
    return {
        "results": [
            {"parameters": r.parameters, "score": r.score, "outputs": r.outputs}
            for r in results
        ]
    }


@app.post("/v1/preview/events")
def preview_events(run: RunRequest) -> dict:
    exec_result = execute_pipeline(run.pipeline, run.inputImagePath)
    events = [
        PreviewEvent(
            event="trace",
            runId="run-1",
            nodeId=trace.nodeId,
            timestamp=0.0,
            payload={"status": trace.status, "message": trace.message},
        ).model_dump()
        for trace in exec_result.traces
    ]
    return {"events": events}
