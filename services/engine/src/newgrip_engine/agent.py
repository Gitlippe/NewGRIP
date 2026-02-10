from __future__ import annotations

from .agent_provider import AgentProvider, AgentProviderConfig
from .models import GenerateRequest, GenerateResponse, PipelineDocumentV1, PipelineEdge, PipelineNode, SocketSpec
from .validator import validate_pipeline


def _starter_pipeline(requirements: str) -> PipelineDocumentV1:
    wants_edges = "edge" in requirements.lower() or "contour" in requirements.lower()
    op = "opencv.canny" if wants_edges else "opencv.threshold"
    nodes = [
        PipelineNode(id="source-1", op="source.image", inputs=[], outputs=[SocketSpec(name="out", type="image")]),
        PipelineNode(
            id="step-1",
            op=op,
            inputs=[SocketSpec(name="in", type="image")],
            outputs=[SocketSpec(name="out", type="image")],
        ),
    ]
    edges = [
        PipelineEdge(
            id="e1",
            **{
                "from": {"nodeId": "source-1", "socket": "out"},
                "to": {"nodeId": "step-1", "socket": "in"},
            },
        )
    ]
    return PipelineDocumentV1(version=1, nodes=nodes, edges=edges)


def generate_pipeline(req: GenerateRequest) -> GenerateResponse:
    provider = AgentProvider(AgentProviderConfig(mode=req.mode))
    provider_trace = provider.generate_text(req.requirements)

    warnings: list[str] = []
    generated = _starter_pipeline(req.requirements)
    if req.mode == "disabled":
        warnings.append("Agent mode disabled. Returned deterministic starter pipeline.")
    elif provider_trace.startswith("remote:"):
        warnings.append("Remote provider selected; strict schema validation enforced.")
    else:
        warnings.append("Local provider selected; deterministic synthesis mode.")

    if req.imageBase64:
        warnings.append("Image-guided generation uses deterministic mapper in current build.")

    validation = validate_pipeline(generated)
    if not validation.ok:
        warnings.extend(validation.errors)
        generated = _starter_pipeline("fallback")

    return GenerateResponse(pipeline=generated, warnings=warnings)
