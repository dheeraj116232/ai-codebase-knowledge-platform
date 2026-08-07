# backend/services/cache.py
_parse_cache: dict[str, "RepoParseResult"] = {}

def get_cached_parse(repo_name: str):
    return _parse_cache.get(repo_name)

def set_cached_parse(repo_name: str, result):
    _parse_cache[repo_name] = result