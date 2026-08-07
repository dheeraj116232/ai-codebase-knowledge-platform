# backend/services/prompt_builder.py
from models.search_models import SearchResultItem

SYSTEM_PROMPT = """You are a senior software engineer explaining a codebase to another developer.

Rules:
- Answer ONLY using the provided code context. Do not invent functions, files, or behavior that isn't shown.
- If the context doesn't contain enough information to answer, say so explicitly — do not guess.
- Reference specific file paths and line numbers when relevant.
- Be precise and technical, but concise. Avoid restating the question.
- If you show code, use proper markdown code blocks with language tags.
"""

def build_context_block(chunks: list[SearchResultItem]) -> str:
    """Format retrieved chunks into a labeled, readable context block."""
    if not chunks:
        return "No relevant code context was found for this query."

    sections = []
    for i, chunk in enumerate(chunks, start=1):
        sections.append(
            f"[Context {i}] File: {chunk.file_path} (lines {chunk.start_line}-{chunk.end_line})\n"
            f"```{chunk.language}\n{chunk.content}\n```"
        )
    return "\n\n".join(sections)

def build_user_prompt(question: str, chunks: list[SearchResultItem]) -> str:
    context_block = build_context_block(chunks)
    return f"""Code context from the repository:

{context_block}

---

Question: {question}

Answer the question using only the code context above. Cite file paths and line numbers where relevant."""