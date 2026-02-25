import { useMemo, useState } from "react";
import type { ConnectFromState, OpTemplate } from "../types";

type OperationPaletteProps = {
  templates: OpTemplate[];
  onAddStep: (template: OpTemplate) => void;
  connectFrom?: ConnectFromState | null;
  loading?: boolean;
};

export function OperationPalette({
  templates,
  onAddStep,
  connectFrom,
  loading,
}: OperationPaletteProps) {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    let ops = connectFrom
      ? templates.filter((t) =>
          t.inputs.some((inp) => inp.type === connectFrom.socketType),
        )
      : templates;
    if (search.trim()) {
      const q = search.toLowerCase();
      ops = ops.filter((t) => t.label.toLowerCase().includes(q) || t.category.toLowerCase().includes(q));
    }
    return ops;
  }, [templates, connectFrom, search]);

  const categories = useMemo(
    () => Array.from(new Set(filtered.map((t) => t.category))),
    [filtered],
  );

  return (
    <aside className="sidePanel" role="navigation" aria-label="Operations palette">
      {connectFrom ? (
        <div className="connectModeBanner">
          Connect from <strong>{connectFrom.socketName}</strong> ({connectFrom.socketType})
        </div>
      ) : (
        <div className="panelTitle">Operations</div>
      )}
      <input
        className="formControl searchInput"
        type="search"
        placeholder="Filter operations..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {loading ? (
        <div className="statusCard">Loading operations...</div>
      ) : (
        <div className="opGrid">
          {categories.map((category) => (
            <div key={category}>
              <div className="categoryTitle">
                {category}
              </div>
              {filtered
                .filter((t) => t.category === category)
                .map((template) => (
                  <button
                    key={template.key}
                    className={`opButton${connectFrom ? " opButtonConnect" : ""}`}
                    onClick={() => onAddStep(template)}
                    title={template.executeOp}
                  >
                    {template.label}
                  </button>
                ))}
            </div>
          ))}
          {categories.length === 0 && search && (
            <div className="statusCard">No matching operations</div>
          )}
        </div>
      )}
    </aside>
  );
}
