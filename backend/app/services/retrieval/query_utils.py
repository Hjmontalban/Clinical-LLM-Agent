import re


def simplify_research_query(question: str) -> str:
    """Convert a natural-language research question into a keyword search query."""
    q = question.strip()

    patterns = [
        r"^what does (the )?current research say about\s+",
        r"^what does research say about\s+",
        r"^what is the evidence (for|on|about|regarding)\s+",
        r"^what are the effects of\s+",
        r"^how effective (is|are)\s+",
        r"^does\s+",
        r"^is there evidence (that|for|about)\s+",
        r"^can\s+",
    ]
    for pattern in patterns:
        q = re.sub(pattern, "", q, flags=re.IGNORECASE)

    q = q.rstrip("?.! ").strip()
    return q if len(q) >= 3 else question.strip()


def build_search_queries(question: str, expanded: list[str] | None = None) -> list[str]:
    """Build deduplicated search queries, prioritizing keyword-friendly forms."""
    simplified = simplify_research_query(question)
    queries: list[str] = []

    for candidate in [simplified, question, *(expanded or [])]:
        candidate = candidate.strip()
        if candidate and candidate not in queries:
            queries.append(candidate)

    return queries[:4]
