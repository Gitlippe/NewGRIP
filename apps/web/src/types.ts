export type ParamSpec = {
  name: string;
  view: "text" | "slider" | "range" | "select" | "checkbox";
  value: unknown;
  options?: string[];
  min?: number;
  max?: number;
};

export type PipelineDocumentV1 = {
  version: 1;
  nodes: Array<{
    id: string;
    op: string;
    label: string;
    params: ParamSpec[];
    inputs: Array<{ name: string; type: string }>;
    outputs: Array<{ name: string; type: string }>;
    position: { x: number; y: number };
  }>;
  edges: Array<{
    id: string;
    from: { nodeId: string; socket: string };
    to: { nodeId: string; socket: string };
  }>;
};

export type SocketDef = { name: string; type: string };

export type OpTemplate = {
  key: string;
  label: string;
  category: string;
  displayOp: string;
  executeOp: string;
  outputType: "image" | "json";
  params: ParamSpec[];
  inputs: SocketDef[];
  outputs: SocketDef[];
};

export type OutputView = {
  key: string;
  title: string;
  kind: "image" | "text";
  value: string;
};

export type ConnectFromState = {
  nodeId: string;
  socketName: string;
  socketType: string;
};

export type NodeData = {
  label: string;
  op: string;
  executeOp: string;
  outputType: "image" | "json";
  params: ParamSpec[];
  inputs: SocketDef[];
  outputs: SocketDef[];
  imageUrl?: string;
  hasError?: boolean;
};
