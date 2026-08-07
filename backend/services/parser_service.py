# backend/services/parser_service.py
import os
from models.file_models import ParsedFile, RepoParseResult
from config.parser_config import (
    INCLUDED_EXTENSIONS,
    IGNORED_DIRS,
    IGNORED_FILE_PATTERNS,
    EXTENSION_LANGUAGE_MAP,
    MAX_FILE_SIZE_BYTES,
)

def should_ignore_file(filename: str) -> bool:
    return any(pattern in filename for pattern in IGNORED_FILE_PATTERNS)

def parse_repository(repo_path: str, repo_name: str) -> RepoParseResult:
    files: list[ParsedFile] = []
    languages: dict[str, int] = {}
    total_scanned = 0
    total_ignored = 0

    for root, dirs, filenames in os.walk(repo_path):
        # Prune ignored directories IN PLACE so os.walk skips them entirely
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for filename in filenames:
            total_scanned += 1
            ext = os.path.splitext(filename)[1]

            if ext not in INCLUDED_EXTENSIONS or should_ignore_file(filename):
                total_ignored += 1
                continue

            abs_path = os.path.join(root, filename)

            try:
                size = os.path.getsize(abs_path)
                if size > MAX_FILE_SIZE_BYTES:
                    total_ignored += 1
                    continue

                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            except (OSError, UnicodeDecodeError):
                total_ignored += 1
                continue

            rel_path = os.path.relpath(abs_path, repo_path)
            language = EXTENSION_LANGUAGE_MAP[ext]

            files.append(ParsedFile(
                path=rel_path,
                absolute_path=abs_path,
                extension=ext,
                language=language,
                size_bytes=size,
                line_count=content.count("\n") + 1,
                content=content,
            ))

            languages[language] = languages.get(language, 0) + 1

    return RepoParseResult(
        repo_name=repo_name,
        total_files_scanned=total_scanned,
        total_files_included=len(files),
        total_files_ignored=total_ignored,
        files=files,
        languages=languages,
    )