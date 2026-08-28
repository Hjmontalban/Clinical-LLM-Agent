import logging
import re
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from app.core.config import Settings
from app.models.paper import Paper

logger = logging.getLogger(__name__)

STUDY_TYPE_MAP = {
    "systematic review": "Systematic Review",
    "meta-analysis": "Meta-analysis",
    "randomized controlled trial": "Randomized Controlled Trial",
    "clinical trial": "Clinical Trial",
    "cohort studies": "Cohort Study",
    "case-control studies": "Case-Control Study",
    "cross-sectional studies": "Cross-sectional Study",
    "case reports": "Case Report",
    "review": "Review",
    "protocol": "Protocol",
}


def classify_study_type(publication_types: list[str], title: str = "") -> str:
    combined = " ".join(publication_types).lower()
    title_lower = title.lower()
    for key, label in STUDY_TYPE_MAP.items():
        if key in combined or key in title_lower:
            return label
    if "animal" in combined or "mice" in title_lower or "rat" in title_lower:
        return "Animal Study"
    if "in vitro" in combined or "in vitro" in title_lower:
        return "In-vitro Study"
    return "Other"


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi or None


class PubMedClient:
    BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, settings: Settings):
        self.settings = settings

    def _params(self, extra: dict[str, Any]) -> dict[str, Any]:
        params = {
            "tool": self.settings.ncbi_tool_name,
            "email": self.settings.ncbi_email,
            **extra,
        }
        if self.settings.ncbi_api_key:
            params["api_key"] = self.settings.ncbi_api_key
        return params

    async def search(self, query: str, limit: int = 20) -> list[Paper]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            search_resp = await client.get(
                f"{self.BASE}/esearch.fcgi",
                params=self._params({
                    "db": "pubmed",
                    "term": query,
                    "retmax": limit,
                    "retmode": "json",
                    "sort": "relevance",
                }),
            )
            search_resp.raise_for_status()
            pmids = search_resp.json().get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            fetch_resp = await client.get(
                f"{self.BASE}/efetch.fcgi",
                params=self._params({
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "xml",
                }),
            )
            fetch_resp.raise_for_status()
            return self._parse_xml(fetch_resp.text)

    def _parse_xml(self, xml_text: str) -> list[Paper]:
        papers: list[Paper] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            logger.exception("Failed to parse PubMed XML")
            return papers

        for article in root.findall(".//PubmedArticle"):
            try:
                medline = article.find("MedlineCitation")
                if medline is None:
                    continue
                pmid_el = medline.find("PMID")
                pmid = pmid_el.text if pmid_el is not None else None

                article_el = medline.find("Article")
                if article_el is None:
                    continue

                title_el = article_el.find("ArticleTitle")
                title = "".join(title_el.itertext()) if title_el is not None else "Untitled"

                abstract_parts = []
                for abs_el in article_el.findall(".//AbstractText"):
                    label = abs_el.get("Label", "")
                    text = "".join(abs_el.itertext())
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)
                abstract = " ".join(abstract_parts) or None

                authors = []
                for author in article_el.findall(".//Author"):
                    last = author.find("LastName")
                    fore = author.find("ForeName")
                    if last is not None:
                        name = last.text or ""
                        if fore is not None and fore.text:
                            name = f"{fore.text} {name}"
                        authors.append(name)

                journal_el = article_el.find(".//Journal/Title")
                journal = journal_el.text if journal_el is not None else None

                year = None
                pub_date = article_el.find(".//PubDate/Year")
                if pub_date is not None and pub_date.text:
                    try:
                        year = int(pub_date.text)
                    except ValueError:
                        pass

                doi = None
                for id_el in article.findall(".//ArticleId"):
                    if id_el.get("IdType") == "doi":
                        doi = normalize_doi(id_el.text)
                    if id_el.get("IdType") == "pmc" and not doi:
                        pass

                pmcid = None
                for id_el in article.findall(".//ArticleId"):
                    if id_el.get("IdType") == "pmc":
                        pmcid = id_el.text

                pub_types = [
                    pt.text for pt in article_el.findall(".//PublicationType")
                    if pt.text
                ]

                mesh_terms = [
                    mh.find("DescriptorName").text
                    for mh in medline.findall(".//MeshHeading")
                    if mh.find("DescriptorName") is not None and mh.find("DescriptorName").text
                ]

                study_type = classify_study_type(pub_types, title)

                papers.append(Paper(
                    id=f"pmid_{pmid}" if pmid else None,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    year=year,
                    journal=journal,
                    doi=doi,
                    pmid=pmid,
                    pmcid=pmcid,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
                    source="pubmed",
                    study_type=study_type,
                    mesh_terms=mesh_terms,
                    publication_types=pub_types,
                ))
            except Exception:
                logger.exception("Error parsing PubMed article")
        return papers
