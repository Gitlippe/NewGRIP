from __future__ import annotations

from collections import defaultdict, deque

from .models import PipelineDocumentV1, ValidationResponse


def _output_socket_type_map(pipeline: PipelineDocumentV1) -> dict[str, dict[str, str]]:
    return {
        node.id: {socket.name: socket.type.value for socket in node.outputs}
        for node in pipeline.nodes
    }


def validate_pipeline(pipeline: PipelineDocumentV1) -> ValidationResponse:
    errors: list[str] = []
    node_ids = [n.id for n in pipeline.nodes]
    node_set = set(node_ids)
    if len(node_set) != len(node_ids):
        errors.append("Duplicate node ids detected.")

    outputs = _output_socket_type_map(pipeline)
    indegree: dict[str, int] = {n.id: 0 for n in pipeline.nodes}
    graph: dict[str, list[str]] = defaultdict(list)

    for edge in pipeline.edges:
        src = edge.from_.nodeId
        dst = edge.to.nodeId
        if src not in node_set:
            errors.append(f"Edge {edge.id} references missing source node {src}.")
        if dst not in node_set:
            errors.append(f"Edge {edge.id} references missing target node {dst}.")
        if src in node_set and edge.from_.socket not in outputs[src]:
            errors.append(f"Edge {edge.id} references missing source socket {edge.from_.socket}.")

        if src in node_set and dst in node_set:
            graph[src].append(dst)
            indegree[dst] += 1
            src_type = outputs[src].get(edge.from_.socket)
            dst_node = next((n for n in pipeline.nodes if n.id == dst), None)
            dst_inputs = {s.name: s.type.value for s in (dst_node.inputs if dst_node else [])}
            dst_type = dst_inputs.get(edge.to.socket)
            if dst_type is None:
                errors.append(f"Edge {edge.id} references missing target socket {edge.to.socket}.")
            elif src_type is not None and dst_type != src_type:
                errors.append(
                    f"Edge {edge.id} type mismatch: {src_type} cannot connect to {dst_type}."
                )

    # Fan-in check: multiple edges to same socket
    socket_targets: dict[tuple[str, str], list[str]] = {}
    for edge in pipeline.edges:
        key = (edge.to.nodeId, edge.to.socket)
        socket_targets.setdefault(key, []).append(edge.id)
    for key, edge_ids in socket_targets.items():
        if len(edge_ids) > 1:
            errors.append(f"Fan-in conflict: socket {key[1]} on node {key[0]} has multiple incoming edges ({', '.join(edge_ids)}).")

    queue = deque([nid for nid, deg in indegree.items() if deg == 0])
    visited = 0
    while queue:
        nid = queue.popleft()
        visited += 1
        for nxt in graph[nid]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    if visited != len(pipeline.nodes):
        errors.append("Pipeline contains a cycle.")

    return ValidationResponse(ok=not errors, errors=errors)


def topological_order(pipeline: PipelineDocumentV1) -> list[str]:
    validation = validate_pipeline(pipeline)
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))

    indegree: dict[str, int] = {n.id: 0 for n in pipeline.nodes}
    graph: dict[str, list[str]] = defaultdict(list)

    for edge in pipeline.edges:
        graph[edge.from_.nodeId].append(edge.to.nodeId)
        indegree[edge.to.nodeId] += 1

    queue = deque([nid for nid, deg in indegree.items() if deg == 0])
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for nxt in graph[nid]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order
