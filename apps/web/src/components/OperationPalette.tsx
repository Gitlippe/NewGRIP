import type { ConnectFromState, OpTemplate } from "../types";

type OperationPaletteProps = {
  templates: OpTemplate[];
  onAddStep: (template: OpTemplate) => void;
  connectFrom?: ConnectFromState | null;
};

export function OperationPalette({
  templates,
  onAddStep,
  connectFrom,
}: OperationPaletteProps) {
  const filtered = connectFrom
    ? templates.filter((t) =>
        t.inputs.some((inp) => inp.type === connectFrom.socketType),
      )
    : templates;

  const categories = Array.from(new Set(filtered.map((t) => t.category)));

  return (
    <aside className="sidePanel">
      {connectFrom ? (
        <div className="connectModeBanner">
          Connect from <strong>{connectFrom.socketName}</strong> ({connectFrom.socketType})
        </div>
      ) : (
        <div className="panelTitle">Operations</div>
      )}
      <div className="opGrid">
        {categories.map((category) => (
          <div key={category}>
            <div className="panelTitle" style={{ marginTop: 8 }}>
              {category}
            </div>
            {filtered
              .filter((t) => t.category === category)
              .map((template) => (
                <button
                  key={template.key}
                  className={`opButton${connectFrom ? " opButtonConnect" : ""}`}
                  onClick={() => onAddStep(template)}
                >
                  {template.label}
                </button>
              ))}
          </div>
        ))}
      </div>
    </aside>
  );
}
