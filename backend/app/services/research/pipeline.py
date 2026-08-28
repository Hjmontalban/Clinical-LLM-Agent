import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings
from app.db.session import ResearchRepository
from app.models.paper import ResearchResult
from app.services.ai.provider import get_llm_provider
from app.services.ai.query_planner import QueryPlanner
from app.services.ai.safety import SafetyGate
from app.services.ai.synthesizer import Synthesizer
from app.services.ai.verifier import CitationVerifier
from app.services.retrieval.dedup import deduplicate_papers
from app.services.retrieval.query_utils import build_search_queries
from app.services.retrieval.ranking import rank_papers
from app.services.search.openalex import OpenAlexClient
from app.services.search.pubmed import PubMedClient
from app.services.search.semantic_scholar import SemanticScholarClient

logger = logging.getLogger(__name__)

PROGRESS_STEPS = [
    "understanding",
    "searching_pubmed",
    "searching_semantic_scholar",
    "searching_openalex",
    "deduplicating",
    "ranking",
    "extracting",
    "synthesizing",
    "verifying",
    "safety_check",
    "completed",
]


class ResearchPipeline:
    def __init__(self, settings: Settings, repo: ResearchRepository):
        self.settings = settings
        self.repo = repo
        self.pubmed = PubMedClient(settings)
        self.semantic = SemanticScholarClient(settings)
        self.openalex = OpenAlexClient(settings)
        self.llm = get_llm_provider(settings)
        self.planner = QueryPlanner(self.llm)
        self.synthesizer = Synthesizer(self.llm)
        self.verifier = CitationVerifier(self.llm)
        self.safety = SafetyGate()

    def _make_steps(self, current: str) -> list[dict[str, Any]]:
        current_idx = PROGRESS_STEPS.index(current) if current in PROGRESS_STEPS else 0
        labels = {
            "understanding": "Understanding question",
            "searching_pubmed": "Searching PubMed",
            "searching_semantic_scholar": "Searching Semantic Scholar",
            "searching_openalex": "Searching OpenAlex",
            "deduplicating": "Removing duplicates",
            "ranking": "Ranking evidence",
            "extracting": "Extracting study findings",
            "synthesizing": "Synthesizing evidence",
            "verifying": "Verifying citations",
            "safety_check": "Running safety checks",
            "completed": "Preparing final report",
        }
        steps = []
        for i, key in enumerate(PROGRESS_STEPS):
            if key == "completed" and current != "completed":
                continue
            status = "completed" if i < current_idx else ("active" if i == current_idx else "pending")
            steps.append({"key": key, "label": labels[key], "status": status})
        return steps

    async def _update_progress(self, research_id: str, step: str, partial: dict) -> None:
        partial["progress_steps"] = self._make_steps(step)
        partial["status"] = step if step != "completed" else "processing"
        await self.repo.update(research_id, partial["status"], partial)

    async def run(self, research_id: str, question: str) -> ResearchResult:
        result = ResearchResult(
            research_id=research_id,
            question=question,
            status="understanding",
            created_at=datetime.now(timezone.utc),
            progress_steps=self._make_steps("understanding"),
        )
        partial = result.model_dump()

        try:
            # Step 1: Query understanding
            plan = await self.planner.plan(question)
            result.pico = self.planner.to_pico(plan)
            partial["pico"] = result.pico.model_dump()
            await self._update_progress(research_id, "searching_pubmed", partial)

            # Step 2-4: Multi-source search
            source_status: dict[str, str] = {}
            all_papers = []
            queries = build_search_queries(question, plan.search_queries)
            if self.settings.is_vercel:
                queries = queries[:2]

            for q in queries:
                limit = min(15, self.settings.max_papers_per_search)
                pubmed_task = self._safe_search("pubmed", self.pubmed.search(q, limit))
                semantic_task = self._safe_search("semantic_scholar", self.semantic.search(q, limit))
                openalex_task = self._safe_search("openalex", self.openalex.search(q, limit))

                results = await asyncio.gather(pubmed_task, semantic_task, openalex_task)
                for source, papers, status in results:
                    source_status[source] = status
                    all_papers.extend(papers)

            result.source_status = source_status
            partial["source_status"] = source_status
            await self._update_progress(research_id, "deduplicating", partial)

            # Step 5: Deduplication
            unique = deduplicate_papers(all_papers)
            await self._update_progress(research_id, "ranking", partial)

            # Step 6: Ranking
            max_synthesis = min(8, self.settings.max_papers_for_synthesis) if self.settings.is_vercel else self.settings.max_papers_for_synthesis
            ranked = rank_papers(unique, question)[:max_synthesis]

            # Assign stable IDs
            for i, paper in enumerate(ranked):
                if not paper.id:
                    paper.id = f"paper_{research_id[:8]}_{i+1}"
                await self.repo.save_paper(paper.id, paper.model_dump())

            result.papers = ranked
            partial["papers"] = [p.model_dump() for p in ranked]
            await self._update_progress(research_id, "synthesizing", partial)

            # Step 7-8: Synthesis
            synthesis = await self.synthesizer.synthesize(question, ranked)
            findings, table, conflicts, claims = self.synthesizer.parse_output(synthesis, ranked)

            result.executive_summary = self.safety.add_disclaimer(synthesis.executive_summary)
            result.key_findings = self.safety.filter_findings(findings)
            result.evidence_strength = synthesis.evidence_strength
            result.evidence_strength_reason = synthesis.evidence_strength_reason
            result.evidence_table = table
            result.conflicting_evidence = conflicts
            result.limitations = synthesis.limitations
            result.research_gaps = synthesis.research_gaps

            partial.update({
                "executive_summary": result.executive_summary,
                "key_findings": result.key_findings,
                "evidence_strength": result.evidence_strength,
                "evidence_strength_reason": result.evidence_strength_reason,
                "evidence_table": [t.model_dump() for t in table],
                "conflicting_evidence": [c.model_dump() for c in conflicts],
                "limitations": result.limitations,
                "research_gaps": result.research_gaps,
            })
            await self._update_progress(research_id, "verifying", partial)

            # Step 9: Citation verification
            if claims:
                verification = await self.verifier.verify_all(claims, ranked)
                result.verification = verification
                partial["verification"] = verification.model_dump()

            await self._update_progress(research_id, "safety_check", partial)

            # Step 10: Safety gate on summary
            result.executive_summary, _ = self.safety.check_text(result.executive_summary)
            result.executive_summary = self.safety.add_disclaimer(result.executive_summary)

            result.status = "completed"
            result.completed_at = datetime.now(timezone.utc)
            result.progress_steps = self._make_steps("completed")
            for step in result.progress_steps:
                step["status"] = "completed"

            final = result.model_dump()
            await self.repo.update(research_id, "completed", final)
            return result

        except Exception as e:
            logger.exception("Research pipeline failed for %s", research_id)
            result.status = "failed"
            result.error = str(e)
            await self.repo.update(research_id, "failed", result.model_dump())
            return result

    async def _safe_search(self, source: str, coro):
        try:
            papers = await coro
            return source, papers, "ok"
        except Exception as e:
            logger.warning("%s search failed: %s", source, e)
            return source, [], "error"


async def _run_in_background(settings: Settings, research_id: str, question: str) -> None:
    from app.db.session import ResearchRepository, get_session_factory
    factory = get_session_factory()
    async with factory() as session:
        repo = ResearchRepository(session)
        pipeline = ResearchPipeline(settings, repo)
        await pipeline.run(research_id, question)


async def start_research(settings: Settings, repo: ResearchRepository, question: str) -> str:
    research_id = f"res_{uuid.uuid4().hex[:12]}"
    await repo.create(research_id, question)

    if settings.is_vercel:
        # Serverless: background tasks are killed after response — run inline
        pipeline = ResearchPipeline(settings, repo)
        await pipeline.run(research_id, question)
    else:
        asyncio.create_task(_run_in_background(settings, research_id, question))

    return research_id
