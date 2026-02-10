import { describe, expect, it } from "vitest";
import type { Node } from "reactflow";
import type { NodeData } from "./types";
import { findTypeMismatches, outputToViews, sourceImageUrl, toPipeline } from "./utils";

describe("toPipeline", () => {
  const sampleNodes: Node<NodeData>[] = [
    {
      id: "source-1",
      type: "pipelineNode",
      position: { x: 0, y: 0 },
      data: {
        label: "Source",
        op: "source.image",
        executeOp: "source.image",
        outputType: "image",
        params: [],
        inputs: [],
        outputs: [{ name: "out", type: "image" }],
      },
    },
    {
      id: "step-1",
      type: "pipelineNode",
      position: { x: 200, y: 0 },
      data: {
        label: "Blur",
        op: "opencv.gaussianBlur",
        executeOp: "opencv.gaussianBlur",
        outputType: "image",
        params: [{ name: "kernel", view: "slider", value: 5, min: 1, max: 31 }],
        inputs: [{ name: "in", type: "image" }],
        outputs: [{ name: "out", type: "image" }],
      },
    },
  ];

  const sampleEdges = [{ id: "e1", source: "source-1", target: "step-1" }];

  it("creates pipeline with version 1", () => {
    const pipeline = toPipeline(sampleNodes, sampleEdges);
    expect(pipeline.version).toBe(1);
  });

  it("maps nodes correctly with executeOp as op", () => {
    const pipeline = toPipeline(sampleNodes, sampleEdges);
    expect(pipeline.nodes).toHaveLength(2);
    expect(pipeline.nodes[0].op).toBe("source.image");
    expect(pipeline.nodes[1].op).toBe("opencv.gaussianBlur");
  });

  it("source nodes have no inputs, operation nodes have one input", () => {
    const pipeline = toPipeline(sampleNodes, sampleEdges);
    expect(pipeline.nodes[0].inputs).toEqual([]);
    expect(pipeline.nodes[1].inputs).toEqual([{ name: "in", type: "image" }]);
  });

  it("maps edges with socket names", () => {
    const pipeline = toPipeline(sampleNodes, sampleEdges);
    expect(pipeline.edges).toHaveLength(1);
    expect(pipeline.edges[0].from).toEqual({ nodeId: "source-1", socket: "out" });
    expect(pipeline.edges[0].to).toEqual({ nodeId: "step-1", socket: "in" });
  });

  it("uses sourceHandle and targetHandle from edges", () => {
    const edgesWithHandles = [
      { id: "e1", source: "source-1", target: "step-1", sourceHandle: "out", targetHandle: "in" },
    ];
    const pipeline = toPipeline(sampleNodes, edgesWithHandles);
    expect(pipeline.edges[0].from.socket).toBe("out");
    expect(pipeline.edges[0].to.socket).toBe("in");
  });

  it("defaults to out/in when handles are undefined", () => {
    const edgesNoHandles = [{ id: "e1", source: "source-1", target: "step-1" }];
    const pipeline = toPipeline(sampleNodes, edgesNoHandles);
    expect(pipeline.edges[0].from.socket).toBe("out");
    expect(pipeline.edges[0].to.socket).toBe("in");
  });
});

describe("outputToViews", () => {
  const nodes: Node<NodeData>[] = [
    {
      id: "source-1",
      type: "pipelineNode",
      position: { x: 0, y: 0 },
      data: {
        label: "Source",
        op: "source.image",
        executeOp: "source.image",
        outputType: "image",
        imageUrl: "http://example.com/img.jpg",
        params: [],
        inputs: [],
        outputs: [{ name: "out", type: "image" }],
      },
    },
    {
      id: "step-1",
      type: "pipelineNode",
      position: { x: 200, y: 0 },
      data: {
        label: "Blur",
        op: "opencv.blur",
        executeOp: "opencv.blur",
        outputType: "image",
        params: [],
        inputs: [{ name: "in", type: "image" }],
        outputs: [{ name: "out", type: "image" }],
      },
    },
  ];

  it("converts backend {mime, base64} objects to data URIs", () => {
    const views = outputToViews(
      { "step-1.out": { mime: "image/png", base64: "abc123" } },
      nodes,
    );
    expect(views).toHaveLength(1);
    expect(views[0].kind).toBe("image");
    expect(views[0].value).toBe("data:image/png;base64,abc123");
  });

  it("handles URL string values as images", () => {
    const views = outputToViews(
      { "unknown.out": "http://example.com/result.png" },
      nodes,
    );
    expect(views).toHaveLength(1);
    expect(views[0].kind).toBe("image");
    expect(views[0].value).toBe("http://example.com/result.png");
  });

  it("converts non-mime objects to JSON text", () => {
    const nodesWithJson: Node<NodeData>[] = [
      ...nodes,
      {
        id: "nn-1",
        type: "pipelineNode",
        position: { x: 400, y: 0 },
        data: {
          label: "Classify",
          op: "nn.classify_stub",
          executeOp: "nn.classify_stub",
          outputType: "json",
          params: [],
          inputs: [{ name: "in", type: "image" }],
          outputs: [{ name: "out", type: "json" }],
        },
      },
    ];
    const views = outputToViews(
      { "nn-1.out": { class: "cat", confidence: 0.95 } },
      nodesWithJson,
    );
    expect(views).toHaveLength(1);
    expect(views[0].kind).toBe("text");
    expect(views[0].value).toContain('"class": "cat"');
    expect(views[0].value).toContain('"confidence": 0.95');
  });

  it("handles plain string values as text", () => {
    const views = outputToViews({ "step-1.out": "some text data" }, nodes);
    expect(views).toHaveLength(1);
    expect(views[0].kind).toBe("text");
    expect(views[0].value).toBe("some text data");
  });

  it("does not include filter property in output views", () => {
    const views = outputToViews(
      { "step-1.out": { mime: "image/png", base64: "abc123" } },
      nodes,
    );
    expect(views[0]).not.toHaveProperty("filter");
  });
});

describe("findTypeMismatches", () => {
  const hullsNode: Node<NodeData> = {
    id: "hulls-1",
    type: "pipelineNode",
    position: { x: 0, y: 0 },
    data: {
      label: "Convex Hulls",
      op: "opencv.convexHulls",
      executeOp: "opencv.convexHulls",
      outputType: "image",
      params: [],
      inputs: [{ name: "in", type: "image" }],
      outputs: [{ name: "out", type: "image" }, { name: "hulls", type: "json" }],
    },
  };

  const grayNode: Node<NodeData> = {
    id: "gray-1",
    type: "pipelineNode",
    position: { x: 200, y: 0 },
    data: {
      label: "RGB to Gray",
      op: "opencv.rgbToGray",
      executeOp: "opencv.rgbToGray",
      outputType: "image",
      params: [],
      inputs: [{ name: "in", type: "image" }],
      outputs: [{ name: "out", type: "image" }],
    },
  };

  it("detects json→image type mismatch", () => {
    const edges = [
      { id: "e1", source: "hulls-1", target: "gray-1", sourceHandle: "hulls", targetHandle: "in" },
    ];
    const { errorEdgeIds, errorNodeIds } = findTypeMismatches([hullsNode, grayNode], edges);
    expect(errorEdgeIds.has("e1")).toBe(true);
    expect(errorNodeIds.has("gray-1")).toBe(true);
  });

  it("does not flag matching types", () => {
    const edges = [
      { id: "e1", source: "hulls-1", target: "gray-1", sourceHandle: "out", targetHandle: "in" },
    ];
    const { errorEdgeIds, errorNodeIds } = findTypeMismatches([hullsNode, grayNode], edges);
    expect(errorEdgeIds.size).toBe(0);
    expect(errorNodeIds.size).toBe(0);
  });

  it("returns empty sets when no edges exist", () => {
    const { errorEdgeIds, errorNodeIds } = findTypeMismatches([hullsNode, grayNode], []);
    expect(errorEdgeIds.size).toBe(0);
    expect(errorNodeIds.size).toBe(0);
  });
});
