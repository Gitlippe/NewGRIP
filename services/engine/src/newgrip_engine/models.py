from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SocketType(str, Enum):
    image = "image"
    mask = "mask"
    number = "number"
    boolean = "boolean"
    contours = "contours"
    lines = "lines"
    json = "json"


class ParamView(str, Enum):
    text = "text"
    slider = "slider"
    range = "range"
    select = "select"
    checkbox = "checkbox"


class SocketSpec(BaseModel):
    name: str
    type: SocketType


class ParamSpec(BaseModel):
    name: str
    view: ParamView
    value: Any
    options: list[str] | None = None
    min: float | None = None
    max: float | None = None


class Position(BaseModel):
    x: float
    y: float


class PipelineNode(BaseModel):
    id: str
    op: str
    label: str | None = None
    params: list[ParamSpec] = Field(default_factory=list)
    inputs: list[SocketSpec] = Field(default_factory=list)
    outputs: list[SocketSpec] = Field(default_factory=list)
    position: Position | None = None


class EndpointRef(BaseModel):
    nodeId: str
    socket: str


class PipelineEdge(BaseModel):
    id: str
    from_: EndpointRef = Field(alias="from")
    to: EndpointRef


class PipelineDocumentV1(BaseModel):
    version: int = 1
    nodes: list[PipelineNode]
    edges: list[PipelineEdge]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationResponse(BaseModel):
    ok: bool
    errors: list[str] = Field(default_factory=list)


class RunTrace(BaseModel):
    nodeId: str
    status: str
    message: str | None = None


class ArtifactRef(BaseModel):
    nodeId: str
    socket: str
    kind: str
    path: str | None = None
    value: Any | None = None


class RunRequest(BaseModel):
    pipeline: PipelineDocumentV1
    inputImagePath: str | None = None
    inputImageBase64: str | None = None


class RunResponse(BaseModel):
    ok: bool
    traces: list[RunTrace] = Field(default_factory=list)
    outputs: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[ArtifactRef] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    mode: str = "disabled"
    requirements: str
    imageBase64: str | None = None


class GenerateResponse(BaseModel):
    pipeline: PipelineDocumentV1
    warnings: list[str] = Field(default_factory=list)


class CodegenRequest(BaseModel):
    pipeline: PipelineDocumentV1
    language: str
    className: str = "GeneratedPipeline"
