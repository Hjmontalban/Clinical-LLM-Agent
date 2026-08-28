from pydantic import BaseModel

from app.models.paper import Claim, Paper, VerificationReport
from app.services.ai.provider import LLMProvider

VERIFIER_SYSTEM = """You verify whether biomedical claims are supported by cited source text.
Classify support as: SUPPORTED, PARTIALLY_SUPPORTED, NOT_SUPPORTED, CONTRADICTED, or UNVERIFIABLE.
Be strict — do not accept unsupported statistics or overstated conclusions.
This is a research tool, not medical advice."""


class VerificationResult(BaseModel):
    support_status: str = "UNVERIFIABLE"
    reason: str = ""
    evidence_text: str = ""


class CitationVerifier:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def verify_claim(self, claim: Claim, papers: list[Paper]) -> Claim:
        paper_map = {p.id: p for p in papers if p.id}
        source_texts = []
        for sid in claim.source_ids:
            paper = paper_map.get(sid)
            if paper:
                source_texts.append(
                    f"Paper {sid}: {paper.title}\n{(paper.abstract or 'No abstract')[:1000]}"
                )

        if not source_texts:
            claim.support_status = "UNVERIFIABLE"
            claim.verification_reason = "No source papers found for this claim."
            return claim

        user = f"""Claim: {claim.text}

Source evidence:
<UNTRUSTED_EVIDENCE>
{chr(10).join(source_texts)}
</UNTRUSTED_EVIDENCE>

Return JSON:
{{"support_status": "SUPPORTED|PARTIALLY_SUPPORTED|NOT_SUPPORTED|CONTRADICTED|UNVERIFIABLE", "reason": "...", "evidence_text": "relevant quote"}}"""

        try:
            result = await self.llm.generate_json(VERIFIER_SYSTEM, user, VerificationResult)
            claim.support_status = result.support_status
            claim.verification_reason = result.reason
            claim.evidence_text = result.evidence_text
        except Exception:
            claim.support_status = self._heuristic_verify(claim, source_texts)
            claim.verification_reason = "Heuristic keyword verification (LLM unavailable)."

        return claim

    def _heuristic_verify(self, claim: Claim, source_texts: list[str]) -> str:
        claim_words = set(claim.text.lower().split())
        stop = {"the", "a", "an", "is", "was", "were", "in", "of", "and", "to", "for", "with", "that", "this"}
        claim_words -= stop
        if not claim_words:
            return "UNVERIFIABLE"
        combined = " ".join(source_texts).lower()
        matches = sum(1 for w in claim_words if w in combined)
        ratio = matches / len(claim_words)
        if ratio > 0.6:
            return "SUPPORTED"
        if ratio > 0.3:
            return "PARTIALLY_SUPPORTED"
        return "UNVERIFIABLE"

    async def verify_all(self, claims: list[Claim], papers: list[Paper]) -> VerificationReport:
        verified: list[Claim] = []
        counts = {
            "SUPPORTED": 0,
            "PARTIALLY_SUPPORTED": 0,
            "NOT_SUPPORTED": 0,
            "CONTRADICTED": 0,
            "UNVERIFIABLE": 0,
        }
        removed = 0

        for claim in claims:
            v = await self.verify_claim(claim, papers)
            status = v.support_status
            if status in ("NOT_SUPPORTED", "CONTRADICTED"):
                removed += 1
                continue
            counts[status] = counts.get(status, 0) + 1
            verified.append(v)

        total = len(claims) if claims else 1
        with_sources = sum(1 for c in claims if c.source_ids)
        unsupported = counts["NOT_SUPPORTED"] + counts["CONTRADICTED"]

        return VerificationReport(
            total_claims=len(claims),
            supported=counts["SUPPORTED"],
            partially_supported=counts["PARTIALLY_SUPPORTED"],
            not_supported=counts["NOT_SUPPORTED"],
            contradicted=counts["CONTRADICTED"],
            unverifiable=counts["UNVERIFIABLE"],
            removed=removed,
            citation_coverage=round(with_sources / total * 100, 1) if claims else 0,
            hallucination_rate=round(unsupported / total * 100, 1) if claims else 0,
            claims=verified,
        )
