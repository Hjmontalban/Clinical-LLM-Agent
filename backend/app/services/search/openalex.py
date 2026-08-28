import logging
import re

import httpx

from app.core.config import Settings
from app.models.paper import Paper
from app.services.search.pubmed import classify_study_type, normalize_doi

logger = logging.getLogger(__name__)


class OpenAlexClient:
    BASE = "https://api.openalex.org"

    def __init__(self, settings: Settings):
        self.settings = settings

    async def search(self, query: str, limit: int = 20) -> list[Paper]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE}/works",
                params={
                    "search": query,
                    "per_page": limit,
                    "mailto": self.settings.crossref_mailto,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        papers: list[Paper] = []
        for item in data.get("results", []):
            doi = normalize_doi(item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None)
            ids = item.get("ids") or {}
            pmid = None
            if ids.get("pmid"):
                pmid = re.sub(r"https?://pubmed\.ncbi\.nlm\.nih\.gov/", "", ids["pmid"])

            authors = []
            for auth in item.get("authorships", []):
                name = auth.get("author", {}).get("display_name")
                if name:
                    authors.append(name)

            abstract = self._reconstruct_abstract(item.get("abstract_inverted_index"))
            pub_year = item.get("publication_year")
            title = item.get("title") or "Untitled"
            oa_id = item.get("id", "").split("/")[-1]

            papers.append(Paper(
                id=f"oa_{oa_id}" if oa_id else None,
                title=title,
                authors=authors,
                abstract=abstract,
                year=pub_year,
                journal=(item.get("primary_location") or {}).get("source", {}).get("display_name"),
                doi=doi,
                pmid=pmid,
                url=item.get("doi") or item.get("id"),
                source="openalex",
                study_type=classify_study_type([], title),
                citation_count=item.get("cited_by_count"),
            ))
        return papers

    @staticmethod
    def _reconstruct_abstract(inverted_index: dict | None) -> str | None:
        if not inverted_index:
            return None
        words: list[tuple[int, str]] = []
        for word, positions in inverted_index.items():
            for pos in positions:
                words.append((pos, word))
        if not words:
            return None
        words.sort(key=lambda x: x[0])
        return " ".join(w for _, w in words)
