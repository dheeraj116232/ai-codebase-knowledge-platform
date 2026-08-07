import time
from groq import Groq

from config.llm_config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    MAX_TOKENS_RESPONSE,
    TEMPERATURE,
)

from services.prompt_builder import (
    SYSTEM_PROMPT,
    build_user_prompt,
)

from models.search_models import SearchResultItem


# Singleton Groq client
_client = None


def get_groq_client() -> Groq:
    """
    Create the Groq client once and reuse it
    across all requests.
    """
    global _client

    if _client is None:
        if not GROQ_API_KEY:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )

        _client = Groq(api_key=GROQ_API_KEY)

    return _client


def generate_answer(
    question: str,
    chunks: list[SearchResultItem],
    max_retries: int = 2,
) -> dict:
    """
    Generate an answer using the retrieved code chunks.

    Args:
        question: User's question.
        chunks: Retrieved semantic search results.
        max_retries: Number of retry attempts for transient API failures.

    Returns:
        Dictionary containing answer, model, sources and token usage.
    """

    client = get_groq_client()

    user_prompt = build_user_prompt(question, chunks)

    last_error = None

    for attempt in range(max_retries + 1):

        try:

            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS_RESPONSE,
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "model": GROQ_MODEL,
                "sources": [
                    {
                        "file_path": chunk.file_path,
                        "lines": f"{chunk.start_line}-{chunk.end_line}",
                    }
                    for chunk in chunks
                ],
                "tokens_used": (
                    response.usage.total_tokens
                    if response.usage
                    else None
                ),
            }

        except Exception as e:

            last_error = e

            # Retry with exponential backoff
            if attempt < max_retries:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue

    raise RuntimeError(
        f"Groq API call failed after {max_retries + 1} attempts: {last_error}"
    )