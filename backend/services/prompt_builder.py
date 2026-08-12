# backend/services/prompt_builder.py
from models.search_models import SearchResultItem

SYSTEM_PROMPT = """You are a senior software engineer explaining a codebase to another developer.

Rules:
- Answer ONLY using the provided code context. Do not invent functions, files, or behavior that isn't shown.
- If the context doesn't contain enough information to answer, say so explicitly; do not guess.
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

FILE_EXPLANATION_SYSTEM_PROMPT = """You are a senior software engineer writing a concise technical summary of a source file for another developer joining the project.

Rules:
- Base your summary ONLY on the structural facts provided (functions, classes, imports, dependents).
- Do not invent behavior that isn't implied by the function/class names and file structure given.
- Write 2-4 sentences describing the file's overall PURPOSE and ROLE in the codebase.
- Mention how it relates to files that depend on it, if that context is provided.
- Be direct and technical. No filler like "This file is important because...".
"""

def build_file_explanation_prompt(context: dict) -> str:
    func_list = "\n".join(
        f"- {f.name}({', '.join(f.arguments)})" + (f" [method of {f.parent_class}]" if f.is_method else "")
        for f in context["functions"]
    ) or "None"

    class_list = "\n".join(f"- {c.name}" for c in context["classes"]) or "None"

    internal_deps = "\n".join(f"- {d}" for d in context["internal_deps"]) or "None"
    external_deps = ", ".join(context["external_deps"]) or "None"
    dependents = "\n".join(f"- {d}" for d in context["dependents"]) or "None (not imported anywhere else in this repo)"

    return f"""File: {context['file_path']}

Functions defined:
{func_list}

Classes defined:
{class_list}

Internal files this depends on:
{internal_deps}

External packages used:
{external_deps}

Files that depend on this file:
{dependents}

Write a concise summary of this file's purpose and role in the codebase, based only on the structure above."""
