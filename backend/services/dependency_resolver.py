# backend/services/dependency_resolver.py
import os

def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")

def _candidate_matches(candidate: str, all_file_paths: set[str]) -> list[str]:
    normalized = _normalize_path(os.path.normpath(candidate))
    possible_paths = [
        f"{normalized}.py",
        f"{normalized}/__init__.py",
    ]

    matches: list[str] = []
    for possible_path in possible_paths:
        if possible_path in all_file_paths:
            matches.append(possible_path)

        suffix = f"/{possible_path}"
        matches.extend(path for path in all_file_paths if path.endswith(suffix))

    return sorted(set(matches), key=lambda path: (path.count("/"), path))

def _resolve_candidate(candidate: str, all_file_paths: set[str]) -> str | None:
    matches = _candidate_matches(candidate, all_file_paths)
    return matches[0] if matches else None

def resolve_python_import(
    module: str,
    is_relative: bool,
    source_file: str,
    all_file_paths: set[str],
    imported_names: list[str] | None = None,
    level: int = 0,
) -> str | None:
    """
    Try to resolve a Python import string to an actual file path in the repo.
    Returns None if it can't be resolved (i.e. it's an external package).
    """
    source_file = _normalize_path(source_file)
    all_file_paths = {_normalize_path(path) for path in all_file_paths}
    imported_names = imported_names or []

    if is_relative:
        source_dir = os.path.dirname(source_file)
        base_dir = source_dir
        for _ in range(max(level - 1, 0)):
            base_dir = os.path.dirname(base_dir)
        candidate = os.path.join(base_dir, module.replace(".", "/"))
    else:
        candidate = module.replace(".", "/")

    # Prefer the imported submodule for statements like "from . import cli".
    for imported_name in imported_names:
        if imported_name == "*":
            continue

        imported_candidate = os.path.join(candidate, imported_name.replace(".", "/"))
        resolved = _resolve_candidate(imported_candidate, all_file_paths)
        if resolved:
            return resolved

    resolved = _resolve_candidate(candidate, all_file_paths)
    if resolved:
        return resolved

    return None  # not found internally -> treat as external


def resolve_js_import(module: str, source_file: str, all_file_paths: set[str]) -> str | None:
    """
    Resolve a JS/TS import path. Only relative imports (./  or ../) are treated as internal;
    bare imports (no leading dot) are npm packages -> external.
    """
    if not module.startswith("."):
        return None  # bare import = external package (react, lodash, etc.)

    source_file = _normalize_path(source_file)
    all_file_paths = {_normalize_path(path) for path in all_file_paths}
    source_dir = os.path.dirname(source_file)
    candidate = os.path.normpath(os.path.join(source_dir, module))

    # Try common extensions and index files, in priority order
    possible_suffixes = [
        ".ts", ".tsx", ".js", ".jsx",
        "/index.ts", "/index.tsx", "/index.js", "/index.jsx",
    ]
    for suffix in possible_suffixes:
        test_path = candidate + suffix if not suffix.startswith("/") else candidate + suffix
        # normalize path separators for comparison
        test_path = test_path.replace("\\", "/")
        if test_path in all_file_paths:
            return test_path

    return None
