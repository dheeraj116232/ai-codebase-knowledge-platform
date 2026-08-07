# backend/services/chunk_service.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.chunk_models import CodeChunk
from models.file_models import ParsedFile
from config.chunk_config import CHUNK_SIZE, CHUNK_OVERLAP, LANGCHAIN_LANGUAGE_MAP

def get_splitter_for_language(language: str) -> RecursiveCharacterTextSplitter:
    """Return a splitter tuned to the file's language, falling back to generic."""
    lc_language = LANGCHAIN_LANGUAGE_MAP.get(language)

    if lc_language:
        return RecursiveCharacterTextSplitter.from_language(
            language=lc_language,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    # Fallback for languages with no specific separators (e.g. json)
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

def _compute_line_range(full_content: str, chunk_text: str, search_start: int) -> tuple[int, int, int]:
    """
    Find where chunk_text sits in full_content to derive its line numbers.
    Returns (start_line, end_line, next_search_start).
    """
    idx = full_content.find(chunk_text, search_start)
    if idx == -1:
        # Fallback: overlap can make exact matching fail occasionally
        idx = search_start

    start_line = full_content.count("\n", 0, idx) + 1
    end_line = start_line + chunk_text.count("\n")
    next_search_start = idx + 1  # advance so overlapping chunks don't match the same position
    return start_line, end_line, next_search_start

def chunk_file(parsed_file: ParsedFile, repo_name: str) -> list[CodeChunk]:
    if not parsed_file.content or not parsed_file.content.strip():
        return []

    splitter = get_splitter_for_language(parsed_file.language)
    raw_chunks = splitter.split_text(parsed_file.content)

    chunks: list[CodeChunk] = []
    search_cursor = 0

    for i, chunk_text in enumerate(raw_chunks):
        start_line, end_line, search_cursor = _compute_line_range(
            parsed_file.content, chunk_text, search_cursor
        )

        chunks.append(CodeChunk(
            chunk_id=f"{parsed_file.path}::{i}",
            repo_name=repo_name,
            file_path=parsed_file.path,
            language=parsed_file.language,
            content=chunk_text,
            start_line=start_line,
            end_line=end_line,
            chunk_index=i,
            char_count=len(chunk_text),
        ))

    return chunks

def chunk_repository(parsed_files: list[ParsedFile], repo_name: str) -> list[CodeChunk]:
    all_chunks: list[CodeChunk] = []
    for pf in parsed_files:
        all_chunks.extend(chunk_file(pf, repo_name))
    return all_chunks