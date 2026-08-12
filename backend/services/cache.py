# backend/services/cache.py
_parse_cache: dict[str, "RepoParseResult"] = {}

def get_cached_parse(repo_name: str):
    return _parse_cache.get(repo_name)

def set_cached_parse(repo_name: str, result):
    _parse_cache[repo_name] = result


# backend/services/cache.py (extend)
_ast_cache: dict[str, list] = {}

def get_cached_ast(repo_name: str):
    return _ast_cache.get(repo_name)

def set_cached_ast(repo_name: str, results):
    _ast_cache[repo_name] = results
    
# backend/services/cache.py (extend)
_graph_cache: dict[str, "nx.DiGraph"] = {}

def get_cached_graph(repo_name: str):
    return _graph_cache.get(repo_name)

def set_cached_graph(repo_name: str, graph):
    _graph_cache[repo_name] = graph