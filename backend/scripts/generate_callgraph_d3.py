import json
from pathlib import Path

INPUT = Path(__file__).resolve().parents[1] / 'callgraph_pallets_flask.json'
OUT_DIR = Path(__file__).resolve().parents[1] / 'callgraph_output'
OUT_DIR.mkdir(exist_ok=True)
HTML_OUT = OUT_DIR / 'callgraph_pallets_flask_d3.html'

with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build edges from resolved calls
edges = []
for c in data.get('calls', []) if isinstance(data.get('calls', None), list) else data.get('sample_calls', []):
    if not c.get('resolved'):
        continue
    caller = f"{c.get('caller_file')}::{c.get('caller_function')}"
    callee_file = c.get('callee_file') or c.get('callee')
    callee = f"{callee_file}::{c.get('callee_name')}"
    edges.append((caller, callee))

# If no resolved edges, use most_called_functions as isolated nodes
if not edges:
    nodes = [item['function'] for item in data.get('most_called_functions', [])]
    links = []
else:
    nodes = list({n for e in edges for n in e})
    # limit nodes
    MAX = 500
    if len(nodes) > MAX:
        from collections import Counter
        cnt = Counter([n for e in edges for n in e])
        keep = set([n for n,_ in cnt.most_common(MAX)])
        edges = [(a,b) for a,b in edges if a in keep and b in keep]
        nodes = list({n for e in edges for n in e})
    id_map = {n:i for i,n in enumerate(nodes)}
    links = [{'source': id_map[a], 'target': id_map[b]} for a,b in edges]

nodes_obj = [{'id': i, 'label': n} for i,n in enumerate(nodes)]

html_template = '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Callgraph - pallets_flask (D3)</title>
<style>
  body { margin:0; font-family: Arial, Helvetica, sans-serif; }
  svg { width:100%; height:100vh; }
  .node circle { stroke: #fff; stroke-width: 1.5px; }
  .link { stroke: #999; stroke-opacity: 0.6; }
</style>
</head>
<body>
<svg></svg>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = __NODES__;
const links = __LINKS__;

const svg = d3.select('svg');
const width = window.innerWidth;
const height = window.innerHeight;

const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(60).strength(0.7))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .on('tick', ticked);

const link = svg.append('g')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
  .selectAll('line')
  .data(links)
  .enter().append('line')
    .attr('stroke-width', 1.5);

const node = svg.append('g')
  .selectAll('g')
  .data(nodes)
  .enter().append('g')
  .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

node.append('circle')
  .attr('r', 6)
  .attr('fill', 'steelblue');

node.append('title')
  .text(d => d.label);

node.append('text')
  .attr('x', 8)
  .attr('y', 3)
  .text(d => d.label)
  .style('font-size', '10px');

function ticked() {
  link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

  node
      .attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
}

function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}
</script>
</body>
</html>
'''

html = html_template.replace('__NODES__', json.dumps(nodes_obj))
html = html.replace('__LINKS__', json.dumps(links))

HTML_OUT.write_text(html, encoding='utf-8')
print('Wrote', HTML_OUT)
