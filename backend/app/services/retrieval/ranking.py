import math
import re
from collections import Counter

from app.models.paper import Paper

STUDY_DESIGN_SCORES = {
    "Systematic Review": 1.0,
    "Meta-analysis": 1.0,
    "Randomized Controlled Trial": 0.9,
    "Clinical Trial": 0.8,
    "Cohort Study": 0.65,
    "Case-Control Study": 0.6,
    "Cross-sectional Study": 0.5,
    "Case Report": 0.3,
    "Review": 0.55,
    "Animal Study": 0.25,
    "In-vitro Study": 0.2,
    "Protocol": 0.15,
    "Other": 0.4,
}

SOURCE_RELIABILITY = {
    "pubmed": 1.0,
    "semantic_scholar": 0.9,
    "openalex": 0.85,
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25_score(query_tokens: list[str], doc_text: str, avg_dl: float, doc_freq: Counter, n_docs: int, k1: float = 1.5, b: float = 0.75) -> float:
    doc_tokens = tokenize(doc_text)
    if not doc_tokens:
        return 0.0
    dl = len(doc_tokens)
    tf = Counter(doc_tokens)
    score = 0.0
    for term in query_tokens:
        if term not in tf:
            continue
        df = doc_freq.get(term, 0)
        idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)
        freq = tf[term]
        numerator = freq * (k1 + 1)
        denominator = freq + k1 * (1 - b + b * dl / max(avg_dl, 1))
        score += idf * numerator / denominator
    return score


def semantic_similarity(query: str, text: str) -> float:
    q_tokens = set(tokenize(query))
    d_tokens = set(tokenize(text))
    if not q_tokens or not d_tokens:
        return 0.0
    intersection = q_tokens & d_tokens
    return len(intersection) / math.sqrt(len(q_tokens) * len(d_tokens))


def recency_score(year: int | None, current_year: int = 2026) -> float:
    if not year:
        return 0.3
    age = max(0, current_year - year)
    return max(0.1, 1.0 - age / 30)


def study_design_score(study_type: str | None) -> float:
    return STUDY_DESIGN_SCORES.get(study_type or "Other", 0.4)


def metadata_quality_score(paper: Paper) -> float:
    score = 0.0
    if paper.abstract:
        score += 0.3
    if paper.doi:
        score += 0.2
    if paper.pmid:
        score += 0.15
    if paper.authors:
        score += 0.1
    if paper.journal:
        score += 0.1
    if paper.citation_count:
        score += min(0.15, paper.citation_count / 500)
    return min(1.0, score)


def source_reliability_score(paper: Paper) -> float:
    sources = paper.source.split("+")
    return max(SOURCE_RELIABILITY.get(s, 0.7) for s in sources)


def rank_papers(papers: list[Paper], query: str) -> list[Paper]:
    if not papers:
        return []

    query_tokens = tokenize(query)
    doc_texts = [
        f"{p.title} {p.abstract or ''} {' '.join(p.mesh_terms)}"
        for p in papers
    ]
    avg_dl = sum(len(tokenize(t)) for t in doc_texts) / max(len(doc_texts), 1)

    doc_freq: Counter = Counter()
    for text in doc_texts:
        doc_freq.update(set(tokenize(text)))
    n_docs = len(papers)

    scored: list[tuple[Paper, float]] = []
    for paper, doc_text in zip(papers, doc_texts):
        sem = semantic_similarity(query, doc_text)
        kw = bm25_score(query_tokens, doc_text, avg_dl, doc_freq, n_docs)
        kw_norm = min(1.0, kw / 10) if kw > 0 else 0.0
        design = study_design_score(paper.study_type)
        recency = recency_score(paper.year)
        meta = metadata_quality_score(paper)
        source = source_reliability_score(paper)

        final = (
            0.35 * sem
            + 0.20 * kw_norm
            + 0.15 * design
            + 0.10 * recency
            + 0.10 * meta
            + 0.10 * source
        )
        paper.relevance_score = round(final, 4)
        scored.append((paper, final))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in scored]
