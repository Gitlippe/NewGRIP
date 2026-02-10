export type SocketType = "image" | "mask" | "number" | "boolean" | "contours" | "lines" | "json";
export type ParamView = "text" | "slider" | "range" | "select" | "checkbox";
export interface SocketSpec {
    name: string;
    type: SocketType;
}
export interface ParamSpec {
    name: string;
    view: ParamView;
    value: unknown;
    options?: string[];
    min?: number;
    max?: number;
}
export interface PipelineNode {
    id: string;
    op: string;
    label?: string;
    params?: ParamSpec[];
    inputs: SocketSpec[];
    outputs: SocketSpec[];
    position?: {
        x: number;
        y: number;
    };
}
export interface EndpointRef {
    nodeId: string;
    socket: string;
}
export interface PipelineEdge {
    id: string;
    from: EndpointRef;
    to: EndpointRef;
}
export interface PipelineDocumentV1 {
    version: 1;
    nodes: PipelineNode[];
    edges: PipelineEdge[];
    metadata?: Record<string, unknown>;
}
export declare const PIPELINE_SCHEMA_V1: {
    $schema: string;
    $id: string;
    title: string;
    type: string;
    required: string[];
    properties: {
        version: {
            const: number;
        };
        nodes: {
            type: string;
            items: {
                $ref: string;
            };
        };
        edges: {
            type: string;
            items: {
                $ref: string;
            };
        };
        metadata: {
            type: string;
            additionalProperties: boolean;
        };
    };
    $defs: {
        socketType: {
            type: string;
            enum: string[];
        };
        paramView: {
            type: string;
            enum: string[];
        };
        param: {
            type: string;
            required: string[];
            properties: {
                name: {
                    type: string;
                };
                view: {
                    $ref: string;
                };
                value: {};
                options: {
                    type: string;
                    items: {
                        type: string;
                    };
                };
                min: {
                    type: string;
                };
                max: {
                    type: string;
                };
            };
            additionalProperties: boolean;
        };
        socket: {
            type: string;
            required: string[];
            properties: {
                name: {
                    type: string;
                };
                type: {
                    $ref: string;
                };
            };
            additionalProperties: boolean;
        };
        node: {
            type: string;
            required: string[];
            properties: {
                id: {
                    type: string;
                };
                op: {
                    type: string;
                };
                label: {
                    type: string;
                };
                params: {
                    type: string;
                    items: {
                        $ref: string;
                    };
                };
                inputs: {
                    type: string;
                    items: {
                        $ref: string;
                    };
                };
                outputs: {
                    type: string;
                    items: {
                        $ref: string;
                    };
                };
                position: {
                    type: string;
                    properties: {
                        x: {
                            type: string;
                        };
                        y: {
                            type: string;
                        };
                    };
                    required: string[];
                    additionalProperties: boolean;
                };
            };
            additionalProperties: boolean;
        };
        endpoint: {
            type: string;
            required: string[];
            properties: {
                nodeId: {
                    type: string;
                };
                socket: {
                    type: string;
                };
            };
            additionalProperties: boolean;
        };
        edge: {
            type: string;
            required: string[];
            properties: {
                id: {
                    type: string;
                };
                from: {
                    $ref: string;
                };
                to: {
                    $ref: string;
                };
            };
            additionalProperties: boolean;
        };
    };
    additionalProperties: boolean;
};
export declare const AGENT_PLAN_DSL_V1: {
    $schema: string;
    $id: string;
    title: string;
    type: string;
    required: string[];
    properties: {
        version: {
            const: number;
        };
        pipeline: {
            $ref: string;
        };
        notes: {
            type: string;
            items: {
                type: string;
            };
        };
    };
    additionalProperties: boolean;
};
export declare const PREVIEW_STREAM_V1: {
    $schema: string;
    $id: string;
    title: string;
    type: string;
    required: string[];
    properties: {
        event: {
            type: string;
            enum: string[];
        };
        runId: {
            type: string;
        };
        nodeId: {
            type: string;
        };
        timestamp: {
            type: string;
        };
        payload: {
            type: string;
            additionalProperties: boolean;
        };
    };
    additionalProperties: boolean;
};
