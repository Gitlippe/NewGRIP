import type { Edge, Node } from "reactflow";
import type { NodeData, OutputView, PipelineDocumentV1 } from "./types";

export const sourceImageUrl = "/sample.jpg";

export function toPipeline(
  nodes: Node<NodeData>[],
  edges: Edge[],
): PipelineDocumentV1 {
  return {
    version: 1,
    nodes: nodes.map((n) => ({
      id: n.id,
      op: n.data.executeOp,
      label: n.data.label,
      params: n.data.params,
      inputs: n.data.op.startsWith("source.")
        ? []
        : (n.data.inputs ?? [{ name: "in", type: "image" }]),
      outputs: n.data.outputs ?? [
        { name: "out", type: n.data.outputType === "image" ? "image" : "json" },
      ],
      position: { x: n.position.x, y: n.position.y },
    })),
    edges: edges.map((e) => ({
      id: e.id,
      from: { nodeId: e.source, socket: e.sourceHandle ?? "out" },
      to: { nodeId: e.target, socket: e.targetHandle ?? "in" },
    })),
  };
}

export function outputToViews(
  outputs: Record<string, unknown>,
  nodes: Node<NodeData>[],
): OutputView[] {
  const nodeById = new Map(nodes.map((n) => [n.id, n]));
  return Object.entries(outputs).map(([key, value]) => {
    const nodeId = key.split(".")[0] ?? "";
    const node = nodeById.get(nodeId);

    // Backend returns {mime, base64} objects for image outputs
    if (
      value != null &&
      typeof value === "object" &&
      "mime" in (value as Record<string, unknown>) &&
      "base64" in (value as Record<string, unknown>)
    ) {
      const obj = value as { mime: string; base64: string };
      return {
        key,
        title: key,
        kind: "image" as const,
        value: `data:${obj.mime};base64,${obj.base64}`,
      };
    }

    // URL strings are treated as images
    if (typeof value === "string" && value.startsWith("http")) {
      return { key, title: key, kind: "image" as const, value };
    }

    // Objects without mime/base64 are JSON text
    if (value != null && typeof value === "object") {
      return {
        key,
        title: key,
        kind: "text" as const,
        value: JSON.stringify(value, null, 2),
      };
    }

    // Fallback: if the node is an image type but value is a plain string,
    // just show it as text (shouldn't normally happen with proper backend)
    return { key, title: key, kind: "text" as const, value: String(value) };
  });
}

export function findTypeMismatches(
  nodes: Node<NodeData>[],
  edges: Edge[],
): { errorEdgeIds: Set<string>; errorNodeIds: Set<string> } {
  const errorEdgeIds = new Set<string>();
  const errorNodeIds = new Set<string>();
  const nodeById = new Map(nodes.map((n) => [n.id, n]));

  for (const edge of edges) {
    const srcNode = nodeById.get(edge.source);
    const tgtNode = nodeById.get(edge.target);
    if (!srcNode || !tgtNode) continue;

    const srcSocket = edge.sourceHandle ?? "out";
    const tgtSocket = edge.targetHandle ?? "in";

    const srcOutput = (srcNode.data.outputs ?? []).find((o) => o.name === srcSocket);
    const tgtInput = (tgtNode.data.inputs ?? []).find((i) => i.name === tgtSocket);

    if (srcOutput && tgtInput && srcOutput.type !== tgtInput.type) {
      errorEdgeIds.add(edge.id);
      errorNodeIds.add(edge.target);
    }
  }

  return { errorEdgeIds, errorNodeIds };
}
