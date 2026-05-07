from __future__ import annotations
from typing import List
from core.rag import ResourceAllocationGraph

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    _DEPS_AVAILABLE = True
except ImportError:
    _DEPS_AVAILABLE = False


def draw_rag(rag: ResourceAllocationGraph,
             cycle_nodes: List[str] = None,
             output_path: str = "rag.png",
             title: str = "Resource Allocation Graph") -> None:
    if not _DEPS_AVAILABLE:
        print("Install networkx and matplotlib to enable visualization.")
        return

    cycle_nodes = set(cycle_nodes or [])
    G = nx.DiGraph()

    process_ids = list(rag.processes.keys())
    resource_ids = list(rag.resources.keys())

    G.add_nodes_from(process_ids, node_type="process")
    G.add_nodes_from(resource_ids, node_type="resource")

    # Assignment edges: resource -> process (black solid)
    assignment_edges = []
    for resource_id, holders in rag.assignment_edges.items():
        for pid in holders:
            G.add_edge(resource_id, pid, edge_type="assignment")
            assignment_edges.append((resource_id, pid))

    # Request edges: process -> resource (orange dashed)
    request_edges = []
    for pid, wanted in rag.request_edges.items():
        for resource_id in wanted:
            G.add_edge(pid, resource_id, edge_type="request")
            request_edges.append((pid, resource_id))

    pos = nx.spring_layout(G, seed=42)

    node_colors = []
    node_shapes_process = []
    node_shapes_resource = []
    for node in G.nodes():
        if node in process_ids:
            color = "red" if node in cycle_nodes else "steelblue"
            node_shapes_process.append((node, color))
        else:
            color = "red" if node in cycle_nodes else "mediumseagreen"
            node_shapes_resource.append((node, color))

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title(title, fontsize=14)

    process_nodes = [n for n, _ in node_shapes_process]
    process_colors = [c for _, c in node_shapes_process]
    nx.draw_networkx_nodes(G, pos, nodelist=process_nodes, node_color=process_colors,
                           node_shape="o", node_size=800, ax=ax)

    resource_nodes = [n for n, _ in node_shapes_resource]
    resource_colors = [c for _, c in node_shapes_resource]
    nx.draw_networkx_nodes(G, pos, nodelist=resource_nodes, node_color=resource_colors,
                           node_shape="s", node_size=800, ax=ax)

    nx.draw_networkx_labels(G, pos, ax=ax, font_color="white", font_size=9)

    nx.draw_networkx_edges(G, pos, edgelist=assignment_edges,
                           edge_color="black", style="solid",
                           arrows=True, arrowsize=20, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=request_edges,
                           edge_color="orange", style="dashed",
                           arrows=True, arrowsize=20, ax=ax)

    legend = [
        mpatches.Patch(color="steelblue", label="Process"),
        mpatches.Patch(color="mediumseagreen", label="Resource"),
        mpatches.Patch(color="red", label="In cycle"),
        mpatches.Patch(color="black", label="Assignment edge"),
        mpatches.Patch(color="orange", label="Request edge"),
    ]
    ax.legend(handles=legend, loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Graph saved to {output_path}")
