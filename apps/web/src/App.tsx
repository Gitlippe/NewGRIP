import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Connection,
  Controls,
  Edge,
  MiniMap,
  Node,
  OnConnectStart,
  ReactFlowInstance,
  useEdgesState,
  useNodesState,
} from "reactflow";
import { loadCatalog, validatePipeline, runPreview } from "./api";
import { InspectorPanel } from "./components/InspectorPanel";
import { OperationPalette } from "./components/OperationPalette";
import { nodeTypes } from "./components/PipelineNode";
import type { ConnectFromState, NodeData, OpTemplate, OutputView } from "./types";
import { findTypeMismatches, outputToViews, sourceImageUrl, toPipeline } from "./utils";

export const fallbackTemplates: OpTemplate[] = [
  {
    key: "gaussian-blur",
    label: "Gaussian Blur",
    category: "Filtering",
    displayOp: "opencv.gaussianBlur",
    executeOp: "opencv.gaussianBlur",
    outputType: "image",
    params: [{ name: "kernel", view: "slider", value: 5, min: 1, max: 31 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "median-blur",
    label: "Median Blur",
    category: "Filtering",
    displayOp: "opencv.medianBlur",
    executeOp: "opencv.medianBlur",
    outputType: "image",
    params: [{ name: "kernel", view: "slider", value: 7, min: 1, max: 31 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "box-blur",
    label: "Box Blur",
    category: "Filtering",
    displayOp: "opencv.blur",
    executeOp: "opencv.blur",
    outputType: "image",
    params: [{ name: "kernel", view: "slider", value: 9, min: 1, max: 31 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "threshold-binary",
    label: "Threshold Binary",
    category: "Thresholding",
    displayOp: "opencv.threshold",
    executeOp: "opencv.threshold",
    outputType: "image",
    params: [{ name: "value", view: "slider", value: 130, min: 0, max: 255 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "threshold-inverse",
    label: "Threshold Inverse",
    category: "Thresholding",
    displayOp: "opencv.thresholdInverse",
    executeOp: "opencv.thresholdInverse",
    outputType: "image",
    params: [{ name: "value", view: "slider", value: 120, min: 0, max: 255 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "adaptive-threshold",
    label: "Adaptive Threshold",
    category: "Thresholding",
    displayOp: "opencv.adaptiveThreshold",
    executeOp: "opencv.adaptiveThreshold",
    outputType: "image",
    params: [{ name: "window", view: "slider", value: 11, min: 3, max: 45 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "canny",
    label: "Canny Edges",
    category: "Edges",
    displayOp: "opencv.canny",
    executeOp: "opencv.canny",
    outputType: "image",
    params: [
      { name: "low", view: "slider", value: 60, min: 0, max: 255 },
      { name: "high", view: "slider", value: 170, min: 0, max: 255 },
    ],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "sobel",
    label: "Sobel Gradient",
    category: "Edges",
    displayOp: "opencv.sobel",
    executeOp: "opencv.sobel",
    outputType: "image",
    params: [{ name: "scale", view: "slider", value: 1, min: 1, max: 8 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "laplacian",
    label: "Laplacian",
    category: "Edges",
    displayOp: "opencv.laplacian",
    executeOp: "opencv.laplacian",
    outputType: "image",
    params: [{ name: "ksize", view: "slider", value: 3, min: 1, max: 7 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "find-contours",
    label: "Find Contours",
    category: "Contours",
    displayOp: "opencv.findContours",
    executeOp: "opencv.findContours",
    outputType: "image",
    params: [{ name: "externalOnly", view: "checkbox", value: true }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }, { name: "contours", type: "json" }],
  },
  {
    key: "convex-hulls",
    label: "Convex Hulls",
    category: "Contours",
    displayOp: "opencv.convexHulls",
    executeOp: "opencv.convexHulls",
    outputType: "image",
    params: [{ name: "enabled", view: "checkbox", value: true }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }, { name: "hulls", type: "json" }],
  },
  {
    key: "filter-contours",
    label: "Filter Contours",
    category: "Contours",
    displayOp: "opencv.filterContours",
    executeOp: "opencv.filterContours",
    outputType: "image",
    params: [
      { name: "minArea", view: "slider", value: 5000, min: 0, max: 20000 },
    ],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }, { name: "contours", type: "json" }],
  },
  {
    key: "erode",
    label: "Erode",
    category: "Morphology",
    displayOp: "opencv.erode",
    executeOp: "opencv.erode",
    outputType: "image",
    params: [
      { name: "iterations", view: "slider", value: 1, min: 1, max: 8 },
    ],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "dilate",
    label: "Dilate",
    category: "Morphology",
    displayOp: "opencv.dilate",
    executeOp: "opencv.dilate",
    outputType: "image",
    params: [
      { name: "iterations", view: "slider", value: 1, min: 1, max: 8 },
    ],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "hsv-threshold",
    label: "HSV Threshold",
    category: "Color",
    displayOp: "opencv.hsvThreshold",
    executeOp: "opencv.hsvThreshold",
    outputType: "image",
    params: [{ name: "value", view: "slider", value: 115, min: 0, max: 255 }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "rgb-to-gray",
    label: "RGB to Gray",
    category: "Color",
    displayOp: "opencv.rgbToGray",
    executeOp: "opencv.rgbToGray",
    outputType: "image",
    params: [{ name: "enabled", view: "checkbox", value: true }],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "image" }],
  },
  {
    key: "nn",
    label: "NN Classify Stub",
    category: "Neural",
    displayOp: "nn.classify_stub",
    executeOp: "nn.classify_stub",
    outputType: "json",
    params: [
      {
        name: "model",
        view: "select",
        value: "mobilenet",
        options: ["mobilenet", "resnet18"],
      },
    ],
    inputs: [{ name: "in", type: "image" }],
    outputs: [{ name: "out", type: "json" }],
  },
];

export const FALLBACK_OPERATION_COUNT = fallbackTemplates.length;

const initialNodes: Node<NodeData>[] = [
  {
    id: "source-1",
    type: "pipelineNode",
    position: { x: 80, y: 180 },
    data: {
      label: "Image Source",
      op: "source.image",
      executeOp: "source.image",
      outputType: "image",
      imageUrl: sourceImageUrl,
      params: [{ name: "imageUrl", view: "text", value: sourceImageUrl }],
      inputs: [],
      outputs: [{ name: "out", type: "image" }],
    },
  },
  {
    id: "step-1",
    type: "pipelineNode",
    position: { x: 430, y: 180 },
    data: {
      label: "Gaussian Blur",
      op: "opencv.gaussianBlur",
      executeOp: "opencv.gaussianBlur",
      outputType: "image",
      params: [{ name: "kernel", view: "slider", value: 5, min: 1, max: 31 }],
      inputs: [{ name: "in", type: "image" }],
      outputs: [{ name: "out", type: "image" }],
    },
  },
];

const initialEdges: Edge[] = [
  { id: "e1", source: "source-1", target: "step-1", sourceHandle: "out", targetHandle: "in" },
];

export function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [status, setStatus] = useState("Ready");
  const [selectedNodeId, setSelectedNodeId] = useState("source-1");
  const [outputViews, setOutputViews] = useState<OutputView[]>([]);
  const [traceLines, setTraceLines] = useState<string[]>([]);
  const [operationTemplates, setOperationTemplates] =
    useState<OpTemplate[]>(fallbackTemplates);
  const [autoRun, setAutoRun] = useState(false);
  const [connectFrom, setConnectFrom] = useState<ConnectFromState | null>(null);
  const reactFlowRef = useRef<ReactFlowInstance | null>(null);

  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) ?? nodes[0],
    [nodes, selectedNodeId],
  );
  const pipeline = useMemo(() => toPipeline(nodes, edges), [nodes, edges]);

  const { errorEdgeIds, errorNodeIds } = useMemo(
    () => findTypeMismatches(nodes, edges),
    [nodes, edges],
  );

  const styledEdges = useMemo(
    () =>
      edges.map((e) =>
        errorEdgeIds.has(e.id)
          ? { ...e, style: { stroke: "#ef4444", strokeWidth: 2 }, animated: true }
          : e,
      ),
    [edges, errorEdgeIds],
  );

  const styledNodes = useMemo(
    () =>
      nodes.map((n) =>
        errorNodeIds.has(n.id)
          ? { ...n, data: { ...n.data, hasError: true } }
          : n.data.hasError
            ? { ...n, data: { ...n.data, hasError: false } }
            : n,
      ),
    [nodes, errorNodeIds],
  );

  // Load operation catalog from backend on mount
  useEffect(() => {
    const load = async () => {
      try {
        const parsed = await loadCatalog();
        if (parsed.length > 0) {
          setOperationTemplates(parsed);
        }
      } catch {
        // Fall back to built-in templates
      }
    };
    void load();
  }, []);

  const addStep = (template: OpTemplate) => {
    const nextIdx = nodes.filter((n) => n.id.startsWith("step-")).length + 1;
    const nodeId = `step-${nextIdx + 1}`;

    // Position: if in connect mode, place to the right of the source node
    let posX = 380;
    let posY = 100 + nextIdx * 120;
    const pending = connectFrom;
    if (pending) {
      const srcNode = nodes.find((n) => n.id === pending.nodeId);
      if (srcNode) {
        posX = srcNode.position.x + 350;
        posY = srcNode.position.y;
      }
    }

    setNodes((prev) => [
      ...prev,
      {
        id: nodeId,
        type: "pipelineNode",
        position: { x: posX, y: posY },
        data: {
          label: `${template.label} ${nextIdx + 1}`,
          op: template.displayOp,
          executeOp: template.executeOp,
          outputType: template.outputType,
          params: structuredClone(template.params),
          inputs: structuredClone(template.inputs),
          outputs: structuredClone(template.outputs),
        },
      },
    ]);

    // Auto-connect if in connect mode
    if (pending) {
      const compatibleInput = template.inputs.find((inp) => inp.type === pending.socketType);
      if (compatibleInput) {
        setEdges((eds) =>
          addEdge(
            {
              source: pending.nodeId,
              sourceHandle: pending.socketName,
              target: nodeId,
              targetHandle: compatibleInput.name,
            },
            eds,
          ),
        );
      }
      setConnectFrom(null);
      // Fit view after the new node + edge render
      setTimeout(() => reactFlowRef.current?.fitView({ padding: 0.15, duration: 300 }), 50);
    }
  };

  const onConnect = (connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds));
    setConnectFrom(null);
  };

  const onConnectStart: OnConnectStart = useCallback(
    (_, params) => {
      if (params.handleType !== "source" || !params.nodeId) return;
      const srcNode = nodes.find((n) => n.id === params.nodeId);
      if (!srcNode) return;
      const socketName = params.handleId ?? "out";
      const socketDef = (srcNode.data.outputs ?? []).find((o) => o.name === socketName);
      setConnectFrom({
        nodeId: params.nodeId,
        socketName,
        socketType: socketDef?.type ?? "image",
      });
    },
    [nodes],
  );

  const onPaneClick = useCallback(() => {
    setConnectFrom(null);
  }, []);

  const updateParam = (name: string, value: unknown) => {
    if (!selectedNode) return;
    setNodes((prev) =>
      prev.map((n) =>
        n.id !== selectedNode.id
          ? n
          : {
              ...n,
              data: {
                ...n.data,
                params: n.data.params.map((p) =>
                  p.name === name ? { ...p, value } : p,
                ),
                imageUrl:
                  n.id === "source-1" && name === "imageUrl"
                    ? String(value)
                    : n.data.imageUrl,
              },
            },
      ),
    );
  };

  const updateLabel = (value: string) => {
    if (!selectedNode) return;
    setNodes((prev) =>
      prev.map((n) =>
        n.id === selectedNode.id
          ? { ...n, data: { ...n.data, label: value } }
          : n,
      ),
    );
  };

  const handleValidate = async () => {
    setStatus("Validating...");
    try {
      const result = await validatePipeline(pipeline);
      setStatus(result.ok ? "Pipeline valid" : result.errors.join("; "));
    } catch (error) {
      setStatus(`Validation failed: ${String(error)}`);
    }
  };

  const handleRunPreview = useCallback(async () => {
    setStatus("Running preview...");
    try {
      const run = await runPreview(
        pipeline,
        nodes.find((n) => n.id === "source-1")?.data.imageUrl,
      );
      setOutputViews(outputToViews(run.outputs, nodes));
      setTraceLines(run.traces.map((t) => `${t.nodeId}: ${t.status}`));
      setStatus(run.ok ? "Preview updated" : "Preview failed");
    } catch (error) {
      setStatus(`Preview failed: ${String(error)}`);
    }
  }, [pipeline, nodes]);

  // Auto-run: debounce and trigger preview on every change
  const autoRunTimer = useRef<ReturnType<typeof setTimeout>>();
  useEffect(() => {
    if (!autoRun) return;
    clearTimeout(autoRunTimer.current);
    autoRunTimer.current = setTimeout(() => {
      void handleRunPreview();
    }, 400);
    return () => clearTimeout(autoRunTimer.current);
  }, [autoRun, handleRunPreview]);

  return (
    <div className="appShell">
      <OperationPalette
        templates={operationTemplates}
        onAddStep={addStep}
        connectFrom={connectFrom}
      />

      <div className="canvasArea">
        <div className="toolbar">
          <button className="toolbarButton" onClick={handleValidate}>
            Validate
          </button>
          <button className="toolbarButton toolbarButtonPrimary" onClick={handleRunPreview}>
            Run Preview
          </button>
          <label className="toggleLabel">
            <div className={`toggle${autoRun ? " toggleOn" : ""}`} onClick={() => setAutoRun((v) => !v)}>
              <div className="toggleThumb" />
            </div>
            Auto Run
          </label>
          <div className={`toolbarStatus${status === "Running preview..." || status === "Validating..." ? " toolbarStatusRunning" : status.startsWith("Preview failed") || status.startsWith("Validation failed") ? " toolbarStatusError" : status === "Preview updated" || status === "Pipeline valid" ? " toolbarStatusSuccess" : ""}`}>
            {status}
          </div>
        </div>
        <main className="canvas">
          <ReactFlow
            nodes={styledNodes}
            edges={styledEdges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onConnectStart={onConnectStart}
            onPaneClick={onPaneClick}
            onNodeClick={(_, node) => setSelectedNodeId(node.id)}
            onInit={(instance) => { reactFlowRef.current = instance; }}
            fitView
          >
            <MiniMap />
            <Controls />
            <Background gap={24} />
          </ReactFlow>
        </main>
      </div>

      <InspectorPanel
        selectedNode={selectedNode}
        outputViews={outputViews}
        traceLines={traceLines}
        onLabelChange={updateLabel}
        onParamChange={updateParam}
      />
    </div>
  );
}
