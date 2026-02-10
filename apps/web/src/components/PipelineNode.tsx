import { Handle, NodeProps, Position } from "reactflow";
import type { NodeData, SocketDef } from "../types";

export function PipelineNodeView({ data, selected }: NodeProps<NodeData>) {
  const isSource = data.op.startsWith("source.");
  const inputs: SocketDef[] = data.inputs ?? (isSource ? [] : [{ name: "in", type: "image" }]);
  const outputs: SocketDef[] = data.outputs ?? [{ name: "out", type: data.outputType === "image" ? "image" : "json" }];

  return (
    <div className={`nodeCard${data.hasError ? " nodeCardError" : ""}`}>
      {inputs.map((inp, i) => (
        <Handle
          key={inp.name}
          type="target"
          position={Position.Left}
          id={inp.name}
          className={`socketHandle socket-${inp.type}`}
          style={{ top: `${((i + 1) / (inputs.length + 1)) * 100}%` }}
        />
      ))}
      {inputs.length > 1 &&
        inputs.map((inp, i) => (
          <div
            key={`label-${inp.name}`}
            className="socketLabel socketLabelLeft"
            style={{ top: `${((i + 1) / (inputs.length + 1)) * 100}%` }}
          >
            {inp.name}
          </div>
        ))}
      <div className="nodeHeader">
        <div className="nodeName">{data.label}</div>
        <div className="nodeOp">{data.op}</div>
      </div>
      <div className="nodeBody">
        {isSource && data.imageUrl ? (
          <img
            className="nodeThumb"
            src={data.imageUrl}
            alt={`${data.label} preview`}
          />
        ) : data.outputType === "image" ? (
          <div className="nodeMeta">Image output</div>
        ) : (
          <div className="nodeMeta">Structured output node</div>
        )}
        <div className="nodeMeta">
          {selected ? "Selected" : "Click to inspect"}
        </div>
      </div>
      {outputs.map((out, i) => (
        <Handle
          key={out.name}
          type="source"
          position={Position.Right}
          id={out.name}
          className={`socketHandle socket-${out.type}`}
          style={{ top: `${((i + 1) / (outputs.length + 1)) * 100}%` }}
        />
      ))}
      {outputs.length > 1 &&
        outputs.map((out, i) => (
          <div
            key={`label-${out.name}`}
            className="socketLabel socketLabelRight"
            style={{ top: `${((i + 1) / (outputs.length + 1)) * 100}%` }}
          >
            {out.name}
          </div>
        ))}
    </div>
  );
}

export const nodeTypes = { pipelineNode: PipelineNodeView };
