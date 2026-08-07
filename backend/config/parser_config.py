# backend/config/parser_config.py

# Map extensions to a language label
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".md": "markdown",
    ".json": "json",
    ".go": "go",
    ".java": "java",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
}

INCLUDED_EXTENSIONS = set(EXTENSION_LANGUAGE_MAP.keys())

IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", "venv", ".venv",
    "__pycache__", ".next", "target", "vendor", ".pytest_cache",
    "coverage", ".idea", ".vscode", "egg-info",
}

IGNORED_FILE_PATTERNS = {
    ".min.js", ".map", ".lock", ".log",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
}

MAX_FILE_SIZE_BYTES = 1_000_000  # skip files > 1MB (likely generated/binary)