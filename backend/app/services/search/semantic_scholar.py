import logging

import httpx

from app.core.config import Settings
from app.models.paper import Paper
from app.services.search.pubmed import classify_study_type, normalize_doi

logger = logging.getLogger(__name__)


class SemanticScholarClient:
    BASE = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, settings: Settings):
        self.settings = settings

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.semantic_scholar_api_key:
            headers["x-api-key"] = self.settings.semantic_scholar_api_key
        return headers

    async def search(self, query: str, limit: int = 20) -> list[Paper]:
        fields = (
            "paperId,title,abstract,year,authors,venue,externalIds,"
            "citationCount,publicationTypes,fieldsOfStudy,url"
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.BASE}/paper/search",
                params={"query": query, "limit": limit, "fields": fields},
                headers=self._headers(),
            )
            if resp.status_code == 429:
                logger.warning("Semantic Scholar rate limited")
                return []
            resp.raise_for_status()
            data = resp.json()

        papers: list[Paper] = []
        for item in data.get("data", []):
            ext = item.get("externalIds") or {}
            pmid = ext.get("PubMed")
            doi = normalize_doi(ext.get("DOI"))
            pmcid = ext.get("PubMedCentral")
            authors = [
                a.get("name", "") for a in item.get("authors", []) if a.get("name")
            ]
            pub_types = item.get("publicationTypes") or []
            title = item.get("title") or "Untitled"
            paper_id = item.get("paperId", "")

            papers.append(Paper(
                id=f"s2_{paper_id}" if paper_id else None,
                title=title,
                authors=authors,
                abstract=item.get("abstract"),
                year=item.get("year"),
                journal=item.get("venue"),
                doi=doi,
                pmid=str(pmid) if pmid else None,
                pmcid=str(pmcid) if pmcid else None,
                url=item.get("url") or (f"https://doi.org/{doi}" if doi else None),
                source="semantic_scholar",
                study_type=classify_study_type(pub_types, title),
                citation_count=item.get("citationCount"),
                publication_types=pub_types,
            ))
        return papers
