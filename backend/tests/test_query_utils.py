from app.services.retrieval.query_utils import build_search_queries, simplify_research_query


def test_simplify_natural_language_question():
    q = "What does current research say about GLP-1 receptor agonists and cardiovascular outcomes?"
    simplified = simplify_research_query(q)
    assert "what does" not in simplified.lower()
    assert "GLP-1" in simplified


def test_build_search_queries():
    q = "What does current research say about metformin and cardiovascular outcomes?"
    queries = build_search_queries(q, ["metformin AND cardiovascular"])
    assert queries[0] == "metformin and cardiovascular outcomes"
    assert len(queries) >= 2
