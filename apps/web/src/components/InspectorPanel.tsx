import type { Node } from "reactflow";
import type { NodeData, OutputView } from "../types";

type InspectorPanelProps = {
  selectedNode: Node<NodeData> | undefined;
  outputViews: OutputView[];
  traceLines: string[];
  onLabelChange: (value: string) => void;
  onParamChange: (name: string, value: unknown) => void;
};

export function InspectorPanel({
  selectedNode,
  outputViews,
  traceLines,
  onLabelChange,
  onParamChange,
}: InspectorPanelProps) {
  const selectedOutputViews = selectedNode
    ? outputViews.filter((v) => v.key.startsWith(selectedNode.id + "."))
    : [];

  return (
    <aside className="sidePanel sidePanelRight">
      <div className="panelTitle">Inspector</div>
      {selectedNode ? (
        <>
          <div className="inspectorSection">
            <label className="inspectorLabel">Node Label</label>
            <input
              className="formControl"
              value={selectedNode.data.label}
              onChange={(e) => onLabelChange(e.target.value)}
            />
          </div>

          {selectedNode.data.params.map((param) => (
            <div key={param.name} className="inspectorSection">
              <label className="inspectorLabel">{param.name}</label>
              {param.view === "slider" ? (
                <input
                  className="formControl"
                  type="range"
                  min={param.min ?? 0}
                  max={param.max ?? 255}
                  value={Number(param.value)}
                  onChange={(e) =>
                    onParamChange(param.name, Number(e.target.value))
                  }
                />
              ) : param.view === "checkbox" ? (
                <input
                  type="checkbox"
                  checked={Boolean(param.value)}
                  onChange={(e) => onParamChange(param.name, e.target.checked)}
                />
              ) : param.view === "select" ? (
                <select
                  className="formControl"
                  value={String(param.value)}
                  onChange={(e) => onParamChange(param.name, e.target.value)}
                >
                  {(param.options ?? []).map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  className="formControl"
                  value={String(param.value)}
                  onChange={(e) => onParamChange(param.name, e.target.value)}
                />
              )}
            </div>
          ))}

          <div className="panelTitle">Selected Output Preview</div>
          {selectedOutputViews.length > 0 ? (
            selectedOutputViews.map((view) => (
              <div key={view.key} className="previewCard">
                <div className="inspectorLabel">{view.key.split(".").slice(1).join(".")}</div>
                {view.kind === "image" ? (
                  <img
                    className="previewImage"
                    src={view.value}
                    alt="Selected node output"
                  />
                ) : (
                  <pre className="statusCard" style={{ whiteSpace: "pre-wrap" }}>
                    {view.value}
                  </pre>
                )}
              </div>
            ))
          ) : selectedNode.data.imageUrl ? (
            <img
              className="previewImage"
              src={selectedNode.data.imageUrl}
              alt="Source image"
            />
          ) : (
            <div className="statusCard">Run preview to see output.</div>
          )}
        </>
      ) : null}

      <div className="panelTitle">Run Output</div>
      <div className="previewGrid">
        {outputViews.length === 0 ? (
          <div className="statusCard">
            Run preview to see rendered output cards.
          </div>
        ) : (
          outputViews.map((view) => (
            <div key={view.key} className="previewCard">
              <div className="inspectorLabel">{view.title}</div>
              {view.kind === "image" ? (
                <img
                  className="previewImage"
                  src={view.value}
                  alt={view.title}
                />
              ) : (
                <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{view.value}</pre>
              )}
            </div>
          ))
        )}
      </div>

      <div className="panelTitle">Execution Trace</div>
      <ul className="traceList">
        {traceLines.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </aside>
  );
}
