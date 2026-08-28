import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import ResearchNotFoundError
from app.db.session import ResearchRepository, init_db, get_session_factory
from app.schemas.search import (
    HealthResponse,
    ResearchCreateRequest,
    ResearchCreateResponse,
    SearchRequest,
    SearchResponse,
)
from app.services.research.cache import cache_research, get_cached_research
from app.services.research.pipeline import ResearchPipeline, start_research
from app.services.retrieval.dedup import deduplicate_papers
from app.services.retrieval.query_utils import simplify_research_query
from app.services.retrieval.ranking import rank_papers
from app.services.search.openalex import OpenAlexClient
from app.services.search.pubmed import PubMedClient
from app.services.search.semantic_scholar import SemanticScholarClient

logger = logging.getLogger(__name__)

router = APIRouter()

_rate_limits: dict[str, list[float]] = defaultdict(list)


async def get_repo():
    await init_db()
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield ResearchRepository(session)


def check_rate_limit(request: Request, settings: Settings = Depends(get_settings)) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now().timestamp()
    window = _rate_limits[client_ip]
    window[:] = [t for t in window if now - t < 60]
    if len(window) >= settings.rate_limit_per_minute:
        raise HTTPException(429, "Rate limit exceeded. Try again in a minute.")
    window.append(now)


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)):
    return HealthResponse(status="ok", app=settings.app_name)


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
):
    check_rate_limit(request, settings)
    pubmed = PubMedClient(settings)
    semantic = SemanticScholarClient(settings)
    openalex = OpenAlexClient(settings)

    search_query = simplify_research_query(body.query)

    sources: dict[str, str] = {}
    all_papers = []

    async def run_source(name: str, coro):
        try:
            papers = await coro
            sources[name] = "ok"
            return papers
        except Exception as e:
            logger.warning("%s failed: %s", name, e)
            sources[name] = "error"
            return []

    results = await asyncio.gather(
        run_source("pubmed", pubmed.search(search_query, body.limit)),
        run_source("semantic_scholar", semantic.search(search_query, body.limit)),
        run_source("openalex", openalex.search(search_query, body.limit)),
    )
    for papers in results:
        all_papers.extend(papers)

    unique = deduplicate_papers(all_papers)
    ranked = rank_papers(unique, search_query)[: body.limit]

    for i, p in enumerate(ranked):
        if not p.id:
            p.id = f"search_{i+1}"

    return SearchResponse(
        query=body.query,
        papers=[p.model_dump() for p in ranked],
        total=len(ranked),
        sources=sources,
    )


@router.post("/research", response_model=ResearchCreateResponse)
async def create_research(
    body: ResearchCreateRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
    repo: ResearchRepository = Depends(get_repo),
):
    check_rate_limit(request, settings)
    try:
        if settings.is_vercel:
            # Serverless: run full pipeline inline and return result (no cross-request DB)
            import uuid
            research_id = f"res_{uuid.uuid4().hex[:12]}"
            await repo.create(research_id, body.question)
            pipeline = ResearchPipeline(settings, repo)
            result = await pipeline.run(research_id, body.question)
            result_dict = result.model_dump()
            cache_research(research_id, result_dict)
            return ResearchCreateResponse(
                research_id=research_id,
                status=result.status,
                result=result_dict,
            )

        research_id = await start_research(settings, repo, body.question)
        return ResearchCreateResponse(research_id=research_id, status="processing")
    except Exception as e:
        logger.exception("Failed to start research")
        raise HTTPException(500, f"Research failed: {e}") from e


@router.get("/research")
async def list_research(repo: ResearchRepository = Depends(get_repo)):
    records = await repo.list_recent(20)
    items = []
    for r in records:
        item = {
            "research_id": r.id,
            "question": r.question,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        if r.result_json:
            try:
                data = json.loads(r.result_json)
                item["evidence_strength"] = data.get("evidence_strength", "")
            except json.JSONDecodeError:
                pass
        items.append(item)
    return {"items": items}


@router.get("/research/{research_id}")
async def get_research(research_id: str, repo: ResearchRepository = Depends(get_repo)):
    cached = get_cached_research(research_id)
    if cached:
        return cached

    record = await repo.get(research_id)
    if not record:
        raise HTTPException(404, f"Research '{research_id}' not found")
    if record.result_json:
        return json.loads(record.result_json)
    return {
        "research_id": record.id,
        "question": record.question,
        "status": record.status,
        "progress_steps": ResearchPipeline(get_settings(), repo)._make_steps(record.status),
    }


@router.get("/research/{research_id}/papers")
async def get_research_papers(research_id: str, repo: ResearchRepository = Depends(get_repo)):
    record = await repo.get(research_id)
    if not record:
        raise HTTPException(404, f"Research '{research_id}' not found")
    if record.result_json:
        data = json.loads(record.result_json)
        return {"papers": data.get("papers", [])}
    return {"papers": []}


@router.get("/research/{research_id}/verification")
async def get_verification(research_id: str, repo: ResearchRepository = Depends(get_repo)):
    record = await repo.get(research_id)
    if not record:
        raise HTTPException(404, f"Research '{research_id}' not found")
    if record.result_json:
        data = json.loads(record.result_json)
        return data.get("verification", {})
    return {}


@router.get("/papers/{paper_id}")
async def get_paper(paper_id: str, repo: ResearchRepository = Depends(get_repo)):
    record = await repo.get_paper(paper_id)
    if not record:
        raise HTTPException(404, f"Paper '{paper_id}' not found")
    authors = json.loads(record.authors) if record.authors else []
    return {
        "id": record.id,
        "title": record.title,
        "abstract": record.abstract,
        "authors": authors,
        "year": record.year,
        "journal": record.journal,
        "doi": record.doi,
        "pmid": record.pmid,
        "pmcid": record.pmcid,
        "url": record.url,
        "source": record.source,
        "study_type": record.study_type,
    }


@router.get("/evaluation")
async def evaluation_dashboard(repo: ResearchRepository = Depends(get_repo)):
    records = await repo.list_recent(50)
    completed = [r for r in records if r.status == "completed" and r.result_json]
    total_claims = 0
    supported = 0
    partial = 0
    coverage_sum = 0.0
    for r in completed:
        try:
            data = json.loads(r.result_json)
            v = data.get("verification") or {}
            total_claims += v.get("total_claims", 0)
            supported += v.get("supported", 0)
            partial += v.get("partially_supported", 0)
            coverage_sum += v.get("citation_coverage", 0)
        except json.JSONDecodeError:
            pass
    n = len(completed) or 1
    return {
        "total_research_completed": len(completed),
        "total_claims_analyzed": total_claims,
        "claims_supported": supported,
        "claims_partially_supported": partial,
        "avg_citation_coverage": round(coverage_sum / n, 1),
        "unsupported_claim_rate": round(
            (total_claims - supported - partial) / max(total_claims, 1) * 100, 1
        ),
        "note": "Metrics computed from actual completed research sessions.",
    }
