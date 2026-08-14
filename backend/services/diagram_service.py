# backend/services/diagram_service.py
import networkx as nx
import re
from config.diagram_config import MAX_NODES_IN_DIAGRAM
from services.groq_service import get_groq_client
from config.llm_config import GROQ_MODEL, TEMPERATURE


def reduce_graph_for_diagram(graph: nx.DiGraph, max_nodes: int = MAX_NODES_IN_DIAGRAM) -> nx.DiGraph:
    """
    Keep only the most connected (highest total degree) nodes, to keep the
    diagram readable. This prioritizes architecturally central files.
    """
    if graph.number_of_nodes() <= max_nodes:
        return graph

    degrees = dict(graph.degree())
    top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]
    top_node_names = {name for name, _ in top_nodes}

    return graph.subgraph(top_node_names).copy()

def _sanitize_node_id(file_path: str) -> str:
    """Mermaid node IDs can't contain slashes, dots, or dashes — sanitize while keeping it readable."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", file_path)

def _short_label(file_path: str) -> str:
    """Show just the filename, not the full path, to keep diagram labels compact."""
    return file_path.split("/")[-1]

def generate_mermaid_syntax(graph: nx.DiGraph) -> str:
    lines = ["graph TD"]  # top-down flowchart

    # Declare nodes with readable labels
    for node in graph.nodes():
        node_id = _sanitize_node_id(node)
        label = _short_label(node)
        lines.append(f'    {node_id}["{label}"]')

    # Declare edges
    for source, target in graph.edges():
        source_id = _sanitize_node_id(source)
        target_id = _sanitize_node_id(target)
        lines.append(f"    {source_id} --> {target_id}")

    return "\n".join(lines)


DIAGRAM_CAPTION_PROMPT = """You are describing a software architecture diagram to a developer.

Rules:
- Base your description ONLY on the file names and connections listed.
- Do not invent purpose or behavior beyond what filenames reasonably suggest.
- Write 2-3 sentences describing the overall structure shown (e.g. "central files", "layering pattern").
- Be factual about the connections, not speculative about implementation details.
"""

def generate_diagram_caption(graph: nx.DiGraph) -> str:
    if graph.number_of_nodes() == 0:
        return "No significant file relationships found to diagram."

    in_degrees = sorted(graph.in_degree(), key=lambda x: x[1], reverse=True)[:5]
    central_files = ", ".join(f"{_short_label(f)} ({d} dependents)" for f, d in in_degrees if d > 0)

    prompt = f"""Diagram shows {graph.number_of_nodes()} files and {graph.number_of_edges()} dependency connections.

Most central files (most depended-upon): {central_files or "none clearly central"}

Describe this architecture structure in 2-3 sentences."""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": DIAGRAM_CAPTION_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=TEMPERATURE,
        max_tokens=150,
    )
    return response.choices[0].message.content

# backend/services/diagram_service.py (add this)
from models.diagram_models import DiagramResult  # define below

def build_dependency_diagram(graph: nx.DiGraph, repo_name: str, include_caption: bool = True) -> "DiagramResult":
    reduced = reduce_graph_for_diagram(graph)
    mermaid_syntax = generate_mermaid_syntax(reduced)
    caption = generate_diagram_caption(reduced) if include_caption else None

    return DiagramResult(
        repo_name=repo_name,
        mermaid_syntax=mermaid_syntax,
        node_count=reduced.number_of_nodes(),
        edge_count=reduced.number_of_edges(),
        was_reduced=reduced.number_of_nodes() < graph.number_of_nodes(),
        original_node_count=graph.number_of_nodes(),
        caption=caption,
    )