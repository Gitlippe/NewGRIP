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
import { loadCatalog, validatePipeline, runPreview, generateCode, importGrip } from "./api";
import { InspectorPanel } from "./components/InspectorPanel";
import { OperationPalette } from "./components/OperationPalette";
import { nodeTypes } from "./components/PipelineNode";
import type { ConnectFromState, NodeData, OpTemplate, OutputView, PipelineDocumentV1 } from "./types";
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
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [autoRun, setAutoRun] = useState(false);
  const [connectFrom, setConnectFrom] = useState<ConnectFromState | null>(null);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showImportMenu, setShowImportMenu] = useState(false);
  const reactFlowRef = useRef<ReactFlowInstance | null>(null);
  const nodeCounter = useRef(2);

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

  useEffect(() => {
    const load = async () => {
      try {
        const parsed = await loadCatalog();
        if (parsed.length > 0) {
          setOperationTemplates(parsed);
        }
      } catch {
        // Fall back to built-in templates
      } finally {
        setCatalogLoading(false);
      }
    };
    void load();
  }, []);

  const addStep = useCallback((template: OpTemplate) => {
    const idx = nodeCounter.current++;
    const nodeId = `step-${idx}`;

    // Position: if in connect mode, place to the right of the source node
    let posX = 380;
    let posY = 100 + idx * 120;
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
          label: `${template.label} ${idx}`,
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
  }, [connectFrom, nodes, setNodes, setEdges]);

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
                  n.data.op.startsWith("source.") && name === "imageUrl"
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

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(pipeline, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pipeline.newgrip.json";
    a.click();
    URL.revokeObjectURL(url);
    setShowExportMenu(false);
  };

  const handleImportJSON = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json,.newgrip.json";
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const doc = JSON.parse(text) as PipelineDocumentV1;
        const importedNodes: Node<NodeData>[] = doc.nodes.map((n) => ({
          id: n.id,
          type: "pipelineNode",
          position: n.position,
          data: {
            label: n.label,
            op: n.op,
            executeOp: n.op,
            outputType: (n.outputs?.[0]?.type === "json" ? "json" : "image") as "image" | "json",
            params: n.params,
            inputs: n.inputs,
            outputs: n.outputs,
            imageUrl: n.op === "source.image" ? (n.params.find((p) => p.name === "imageUrl")?.value as string) ?? sourceImageUrl : undefined,
          },
        }));
        const importedEdges: Edge[] = doc.edges.map((e) => ({
          id: e.id,
          source: e.from.nodeId,
          target: e.to.nodeId,
          sourceHandle: e.from.socket,
          targetHandle: e.to.socket,
        }));
        setNodes(importedNodes);
        setEdges(importedEdges);
        setOutputViews([]);
        setTraceLines([]);
        setStatus("Pipeline imported");
        setTimeout(() => reactFlowRef.current?.fitView({ padding: 0.15, duration: 300 }), 100);
      } catch {
        setStatus("Import failed: invalid file");
      }
    };
    input.click();
  };

  const handleImportGRIP = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".xml,.grip";
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      try {
        const xml = await file.text();
        
        const result = await importGrip(xml);
        const doc = result.pipeline;
        const importedNodes: Node<NodeData>[] = doc.nodes.map((n) => ({
          id: n.id,
          type: "pipelineNode",
          position: n.position,
          data: {
            label: n.label,
            op: n.op,
            executeOp: n.op,
            outputType: (n.outputs?.[0]?.type === "json" ? "json" : "image") as "image" | "json",
            params: n.params,
            inputs: n.inputs,
            outputs: n.outputs,
            imageUrl: n.op === "source.image" ? (n.params.find((p) => p.name === "imageUrl")?.value as string) ?? sourceImageUrl : undefined,
          },
        }));
        const importedEdges: Edge[] = doc.edges.map((e) => ({
          id: e.id,
          source: e.from.nodeId,
          target: e.to.nodeId,
          sourceHandle: e.from.socket,
          targetHandle: e.to.socket,
        }));
        setNodes(importedNodes);
        setEdges(importedEdges);
        setOutputViews([]);
        setTraceLines([]);
        const warn = result.warnings.length > 0 ? ` (${result.warnings.length} warnings)` : "";
        setStatus(`GRIP imported${warn}`);
        setTimeout(() => reactFlowRef.current?.fitView({ padding: 0.15, duration: 300 }), 100);
      } catch (err) {
        setStatus(`GRIP import failed: ${String(err)}`);
      }
    };
    input.click();
  };

  const handleCodegen = async (language: string) => {
    setShowExportMenu(false);
    setStatus(`Generating ${language} code...`);
    try {
      const result = await generateCode(pipeline, language, "Pipeline");
      const blob = new Blob([result.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = result.filename;
      a.click();
      URL.revokeObjectURL(url);
      setStatus(`Exported ${result.filename}`);
    } catch (error) {
      setStatus(`Code generation failed: ${String(error)}`);
    }
  };

  useEffect(() => {
    if (!showExportMenu && !showImportMenu) return;
    const close = () => { setShowExportMenu(false); setShowImportMenu(false); };
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, [showExportMenu, showImportMenu]);

  const handleDeleteSelected = useCallback(() => {
    const selectedNodeIds = nodes.filter((n) => n.selected).map((n) => n.id);
    if (selectedNodeIds.length === 0) return;
    setNodes((prev) => prev.filter((n) => !n.selected));
    setEdges((prev) => prev.filter((e) => !selectedNodeIds.includes(e.source) && !selectedNodeIds.includes(e.target)));
  }, [nodes, setNodes, setEdges]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Delete" || e.key === "Backspace") {
        const tag = (e.target as HTMLElement).tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
        handleDeleteSelected();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [handleDeleteSelected]);

  return (
    <div className="appShell">
      <OperationPalette
        templates={operationTemplates}
        onAddStep={addStep}
        connectFrom={connectFrom}
        loading={catalogLoading}
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
          <div className="toolbarSeparator" />
          <div className="dropdownWrapper">
            <button
              className="toolbarButton"
              onClick={(e) => { e.stopPropagation(); setShowImportMenu((v) => !v); }}
            >
              Import
            </button>
            {showImportMenu && (
              <div className="dropdownMenu" onClick={(e) => e.stopPropagation()}>
                <button className="dropdownItem" onClick={() => { setShowImportMenu(false); handleImportJSON(); }}>Pipeline JSON</button>
                <button className="dropdownItem" onClick={() => { setShowImportMenu(false); handleImportGRIP(); }}>GRIP XML</button>
              </div>
            )}
          </div>
          <div className="dropdownWrapper">
            <button
              className="toolbarButton"
              onClick={(e) => { e.stopPropagation(); setShowExportMenu((v) => !v); }}
            >
              Export
            </button>
            {showExportMenu && (
              <div className="dropdownMenu" onClick={(e) => e.stopPropagation()}>
                <button className="dropdownItem" onClick={handleExportJSON}>Pipeline JSON</button>
                <div className="dropdownDivider" />
                <button className="dropdownItem" onClick={() => handleCodegen("python")}>Python Code</button>
                <button className="dropdownItem" onClick={() => handleCodegen("java")}>Java Code</button>
                <button className="dropdownItem" onClick={() => handleCodegen("cpp")}>C++ Code</button>
              </div>
            )}
          </div>
          <div className={`toolbarStatus${status === "Running preview..." || status === "Validating..." ? " toolbarStatusRunning" : status.startsWith("Preview failed") || status.startsWith("Validation failed") || status.startsWith("Import failed") || status.startsWith("Code generation failed") || status.startsWith("GRIP import failed") ? " toolbarStatusError" : status === "Preview updated" || status === "Pipeline valid" || status.startsWith("Exported") || status === "Pipeline imported" || status.startsWith("GRIP imported") ? " toolbarStatusSuccess" : ""}`}>
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
            deleteKeyCode={null}
            edgesUpdatable
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
