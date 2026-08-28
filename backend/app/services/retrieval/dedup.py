import logging
import re
from rapidfuzz import fuzz

from app.models.paper import Paper
from app.services.search.pubmed import normalize_doi

logger = logging.getLogger(__name__)


def normalize_title(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title


def merge_papers(primary: Paper, secondary: Paper) -> Paper:
    """Keep the richest metadata record."""
    data = primary.model_dump()
    secondary_data = secondary.model_dump()
    for key, value in secondary_data.items():
        if value and (not data.get(key) or data.get(key) in ("", [], None, 0.0)):
            data[key] = value
    if secondary.abstract and (not primary.abstract or len(secondary.abstract) > len(primary.abstract)):
        data["abstract"] = secondary.abstract
    if secondary.citation_count and (not primary.citation_count or secondary.citation_count > primary.citation_count):
        data["citation_count"] = secondary.citation_count
    sources = {primary.source, secondary.source}
    data["source"] = "+".join(sorted(sources))
    return Paper(**data)


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    if not papers:
        return []

    unique: list[Paper] = []
    seen_doi: dict[str, int] = {}
    seen_pmid: dict[str, int] = {}
    seen_pmcid: dict[str, int] = {}
    seen_title: dict[str, int] = {}

    for paper in papers:
        doi = normalize_doi(paper.doi)
        pmid = paper.pmid
        pmcid = paper.pmcid
        norm_title = normalize_title(paper.title)

        match_idx: int | None = None

        if doi and doi in seen_doi:
            match_idx = seen_doi[doi]
        elif pmid and pmid in seen_pmid:
            match_idx = seen_pmid[pmid]
        elif pmcid and pmcid in seen_pmcid:
            match_idx = seen_pmcid[pmcid]
        elif norm_title and norm_title in seen_title:
            match_idx = seen_title[norm_title]
        else:
            for i, existing in enumerate(unique):
                if doi and normalize_doi(existing.doi) == doi:
                    match_idx = i
                    break
                if pmid and existing.pmid == pmid:
                    match_idx = i
                    break
                if fuzz.ratio(norm_title, normalize_title(existing.title)) > 92:
                    match_idx = i
                    break

        if match_idx is not None:
            unique[match_idx] = merge_papers(unique[match_idx], paper)
        else:
            unique.append(paper)
            idx = len(unique) - 1
            if doi:
                seen_doi[doi] = idx
            if pmid:
                seen_pmid[pmid] = idx
            if pmcid:
                seen_pmcid[pmcid] = idx
            if norm_title:
                seen_title[norm_title] = idx

    return unique
