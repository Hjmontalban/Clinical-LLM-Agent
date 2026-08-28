from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str | None = None
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    year: int | None = None
    journal: str | None = None
    doi: str | None = None
    pmid: str | None = None
    pmcid: str | None = None
    url: str | None = None
    source: str = "unknown"
    study_type: str | None = None
    citation_count: int | None = None
    relevance_score: float = 0.0
    mesh_terms: list[str] = Field(default_factory=list)
    publication_types: list[str] = Field(default_factory=list)

    def display_authors(self, max_authors: int = 3) -> str:
        if not self.authors:
            return "Unknown authors"
        if len(self.authors) <= max_authors:
            return ", ".join(self.authors)
        return ", ".join(self.authors[:max_authors]) + " et al."


class PICO(BaseModel):
    population: str = ""
    intervention: str = ""
    comparison: str = ""
    outcomes: list[str] = Field(default_factory=list)
    study_types: list[str] = Field(default_factory=list)


class EvidenceExtraction(BaseModel):
    paper_id: str
    study_design: str = "Unknown"
    population: str = ""
    sample_size: int | None = None
    intervention: str = ""
    comparison: str = ""
    primary_outcomes: list[str] = Field(default_factory=list)
    secondary_outcomes: list[str] = Field(default_factory=list)
    main_results: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    certainty: str = "unknown"


class Claim(BaseModel):
    claim_id: str
    text: str
    source_ids: list[str] = Field(default_factory=list)
    support_type: str = "direct"
    confidence: float = 0.0
    support_status: str = "UNVERIFIABLE"
    verification_reason: str = ""
    evidence_text: str = ""


class ConflictGroup(BaseModel):
    topic: str
    supporting_papers: list[str] = Field(default_factory=list)
    conflicting_papers: list[str] = Field(default_factory=list)
    explanation: str = ""


class VerificationReport(BaseModel):
    total_claims: int = 0
    supported: int = 0
    partially_supported: int = 0
    not_supported: int = 0
    contradicted: int = 0
    unverifiable: int = 0
    removed: int = 0
    citation_coverage: float = 0.0
    hallucination_rate: float = 0.0
    claims: list[Claim] = Field(default_factory=list)


class EvidenceTableRow(BaseModel):
    study: str
    year: int | None = None
    study_type: str = ""
    population: str = ""
    intervention: str = ""
    outcome: str = ""
    result: str = ""
    limitations: str = ""
    paper_id: str = ""


class ResearchResult(BaseModel):
    research_id: str
    question: str
    status: str = "queued"
    progress_steps: list[dict[str, Any]] = Field(default_factory=list)
    pico: PICO | None = None
    executive_summary: str = ""
    key_findings: list[str] = Field(default_factory=list)
    evidence_strength: str = "Unknown"
    evidence_strength_reason: str = ""
    evidence_table: list[EvidenceTableRow] = Field(default_factory=list)
    conflicting_evidence: list[ConflictGroup] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    research_gaps: list[str] = Field(default_factory=list)
    papers: list[Paper] = Field(default_factory=list)
    verification: VerificationReport | None = None
    source_status: dict[str, str] = Field(default_factory=dict)
    created_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
