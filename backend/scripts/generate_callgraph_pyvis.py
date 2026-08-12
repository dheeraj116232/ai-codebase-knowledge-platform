import json
from pathlib import Path
from pyvis.network import Network

INPUT = Path(__file__).resolve().parents[1] / 'callgraph_pallets_flask.json'
OUT_DIR = Path(__file__).resolve().parents[1] / 'callgraph_output'
OUT_DIR.mkdir(exist_ok=True)
HTML_OUT = OUT_DIR / 'callgraph_pallets_flask.html'

with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build edges from resolved calls to reduce noise
edges = []
for c in data.get('calls', []) if isinstance(data.get('calls', None), list) else data.get('sample_calls', []):
    if not c.get('resolved'):
        continue
    caller = f"{c.get('caller_file')}::{c.get('caller_function')}"
    callee_file = c.get('callee_file') or c.get('callee')
    callee = f"{callee_file}::{c.get('callee_name')}"
    edges.append((caller, callee))

# If no resolved edges, fall back to most_called_functions as nodes
if not edges:
    net = Network(height='800px', width='100%', directed=True)
    for i, item in enumerate(data.get('most_called_functions', [])):
        label = item['function']
        net.add_node(i, label=label, title=f"calls: {item['call_count']}")
    net.show(str(HTML_OUT))
    print('Wrote', HTML_OUT)
    raise SystemExit(0)

# Limit graph size
MAX_NODES = 500
nodes = set([n for e in edges for n in e])
if len(nodes) > MAX_NODES:
    # keep highest-degree nodes
    from collections import Counter
    cnt = Counter([n for e in edges for n in e])
    keep = set([n for n,_ in cnt.most_common(MAX_NODES)])
    edges = [(a,b) for a,b in edges if a in keep and b in keep]

net = Network(height='900px', width='100%', bgcolor='#ffffff', font_color='black', directed=True)
net.barnes_hut()

# Add nodes and edges
for a,b in edges:
    net.add_node(a, label=a, title=a)
    net.add_node(b, label=b, title=b)
    net.add_edge(a, b)

# Better physics for large graphs
net.show_buttons(filter_=['physics'])
net.show(str(HTML_OUT))
print('Wrote', HTML_OUT)
