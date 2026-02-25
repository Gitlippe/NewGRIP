import type { OpTemplate, PipelineDocumentV1 } from "./types";

export const API_BASE = "http://127.0.0.1:8000";

export async function loadCatalog(): Promise<OpTemplate[]> {
  const response = await fetch(`${API_BASE}/v1/operations`);
  const payload = await response.json();
  const parsed: OpTemplate[] = (payload.operations ?? []).map((op: any) => ({
    key: String(op.key),
    label: String(op.label),
    category: String(op.category ?? "General"),
    displayOp: String(op.displayOp ?? op.executeOp ?? op.key),
    executeOp: String(op.executeOp ?? op.key),
    outputType: op.outputType === "json" ? "json" : "image",
    params: Array.isArray(op.params) ? op.params : [],
    inputs: Array.isArray(op.inputs) ? op.inputs : [{ name: "in", type: "image" }],
    outputs: Array.isArray(op.outputs) ? op.outputs : [{ name: "out", type: op.outputType === "json" ? "json" : "image" }],
  }));
  return parsed;
}

export async function validatePipeline(
  pipeline: PipelineDocumentV1,
): Promise<{ ok: boolean; errors: string[] }> {
  const response = await fetch(`${API_BASE}/v1/pipelines/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pipeline }),
  });
  return response.json() as Promise<{ ok: boolean; errors: string[] }>;
}

async function fetchImageAsBase64(url: string): Promise<string | undefined> {
  try {
    const resp = await fetch(url);
    const blob = await resp.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        // Strip "data:image/...;base64," prefix
        resolve(dataUrl.split(",")[1]);
      };
      reader.readAsDataURL(blob);
    });
  } catch {
    return undefined;
  }
}

export async function runPreview(
  pipeline: PipelineDocumentV1,
  inputImagePath: string | undefined,
): Promise<{
  ok: boolean;
  traces: Array<{ nodeId: string; status: string }>;
  outputs: Record<string, unknown>;
}> {
  let inputImageBase64: string | undefined;
  if (inputImagePath && !inputImagePath.startsWith("http")) {
    inputImageBase64 = await fetchImageAsBase64(inputImagePath);
  }
  const response = await fetch(`${API_BASE}/v1/pipelines/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pipeline, inputImagePath, inputImageBase64 }),
  });
  return response.json();
}

export async function generateCode(
  pipeline: PipelineDocumentV1,
  language: string,
  className: string,
): Promise<{ filename: string; content: string }> {
  const response = await fetch(`${API_BASE}/v1/codegen`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pipeline, language, className }),
  });
  if (!response.ok) {
    throw new Error(`Code generation failed (${response.status})`);
  }
  return response.json() as Promise<{ filename: string; content: string }>;
}
