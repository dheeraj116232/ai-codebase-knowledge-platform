import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

INPUT = Path(__file__).resolve().parents[1] / 'callgraph_pallets_flask.json'
OUT_DIR = Path(__file__).resolve().parents[1] / 'callgraph_output'
OUT_DIR.mkdir(exist_ok=True)

with open(INPUT,'r',encoding='utf-8') as f:
    data = json.load(f)

# Build graph from resolved calls only to reduce noise
G = nx.DiGraph()
for c in data.get('sample_calls', []) + data.get('calls', []) if isinstance(data.get('calls', None), list) else data.get('sample_calls', []):
    # use resolved flag if present
    resolved = c.get('resolved', False)
    if not resolved:
        continue
    caller = f"{c.get('caller_file')}::{c.get('caller_function')}"
    callee_file = c.get('callee_file') or c.get('callee')
    callee = f"{callee_file}::{c.get('callee_name')}"
    G.add_edge(caller, callee)

if G.number_of_nodes() == 0:
    # fallback: use most_called_functions to create nodes
    for item in data.get('most_called_functions', []):
        fn = item['function']
        G.add_node(fn)

# Limit graph size for visualization
MAX_NODES = 200
if G.number_of_nodes() > MAX_NODES:
    nodes_to_keep = list(sorted(G.degree, key=lambda x: x[1], reverse=True))[:MAX_NODES]
    keep = {n for n,_ in nodes_to_keep}
    G = G.subgraph(keep).copy()

plt.figure(figsize=(14,10))
pos = nx.spring_layout(G, k=0.5, iterations=50)
nx.draw_networkx_nodes(G, pos, node_size=120, node_color='skyblue')
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10)
nx.draw_networkx_labels(G, pos, font_size=8)
plt.axis('off')
PNG = OUT_DIR / 'callgraph_pallets_flask.png'
SVG = OUT_DIR / 'callgraph_pallets_flask.svg'
plt.savefig(PNG, dpi=150, bbox_inches='tight')
plt.savefig(SVG, bbox_inches='tight')
print('Wrote', PNG, SVG)
