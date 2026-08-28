import pytest
from app.models.paper import Paper
from app.services.retrieval.dedup import deduplicate_papers, normalize_title
from app.services.retrieval.ranking import rank_papers


def test_normalize_title():
    assert normalize_title("Hello, World!") == "hello world"


def test_deduplicate_by_doi():
    papers = [
        Paper(title="Study A", doi="10.1234/test", source="pubmed"),
        Paper(title="Study A duplicate", doi="10.1234/test", source="openalex", abstract="Longer abstract here"),
    ]
    result = deduplicate_papers(papers)
    assert len(result) == 1
    assert result[0].abstract == "Longer abstract here"


def test_rank_papers():
    papers = [
        Paper(title="Unrelated study", abstract="cats and dogs", source="pubmed", year=2010),
        Paper(
            title="Metformin cardiovascular outcomes",
            abstract="metformin reduces cardiovascular risk in diabetes",
            source="pubmed",
            year=2023,
            study_type="Randomized Controlled Trial",
        ),
    ]
    ranked = rank_papers(papers, "metformin cardiovascular")
    assert ranked[0].title.startswith("Metformin")
