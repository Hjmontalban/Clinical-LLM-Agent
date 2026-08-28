export interface Paper {
  id?: string;
  title: string;
  authors: string[];
  abstract?: string | null;
  year?: number | null;
  journal?: string | null;
  doi?: string | null;
  pmid?: string | null;
  pmcid?: string | null;
  url?: string | null;
  source: string;
  study_type?: string | null;
  citation_count?: number | null;
  relevance_score?: number;
}

export interface ProgressStep {
  key: string;
  label: string;
  status: "pending" | "active" | "completed";
}

export interface Claim {
  claim_id: string;
  text: string;
  source_ids: string[];
  support_status: string;
  verification_reason?: string;
  evidence_text?: string;
  confidence?: number;
}

export interface VerificationReport {
  total_claims: number;
  supported: number;
  partially_supported: number;
  not_supported: number;
  contradicted: number;
  unverifiable: number;
  removed: number;
  citation_coverage: number;
  hallucination_rate: number;
  claims: Claim[];
}

export interface EvidenceTableRow {
  study: string;
  year?: number | null;
  study_type: string;
  population: string;
  intervention: string;
  outcome: string;
  result: string;
  limitations: string;
  paper_id: string;
}

export interface ConflictGroup {
  topic: string;
  supporting_papers: string[];
  conflicting_papers: string[];
  explanation: string;
}

export interface ResearchResult {
  research_id: string;
  question: string;
  status: string;
  progress_steps?: ProgressStep[];
  executive_summary?: string;
  key_findings?: string[];
  evidence_strength?: string;
  evidence_strength_reason?: string;
  evidence_table?: EvidenceTableRow[];
  conflicting_evidence?: ConflictGroup[];
  limitations?: string[];
  research_gaps?: string[];
  papers?: Paper[];
  verification?: VerificationReport;
  source_status?: Record<string, string>;
  created_at?: string;
  completed_at?: string;
  error?: string;
}

export interface SearchResponse {
  query: string;
  papers: Paper[];
  total: number;
  sources: Record<string, string>;
}

export interface HistoryItem {
  research_id: string;
  question: string;
  status: string;
  created_at?: string;
  evidence_strength?: string;
}

export interface EvaluationMetrics {
  total_research_completed: number;
  total_claims_analyzed: number;
  claims_supported: number;
  claims_partially_supported: number;
  avg_citation_coverage: number;
  unsupported_claim_rate: number;
  note: string;
}
