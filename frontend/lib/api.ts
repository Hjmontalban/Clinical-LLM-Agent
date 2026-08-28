import type {
  EvaluationMetrics,
  HistoryItem,
  Paper,
  ResearchResult,
  SearchResponse,
  VerificationReport,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export async function checkHealth(): Promise<{ status: string; app: string }> {
  return fetchApi("/api/health");
}

export async function searchLiterature(
  query: string,
  limit = 20
): Promise<SearchResponse> {
  return fetchApi("/api/search", {
    method: "POST",
    body: JSON.stringify({ query, limit }),
  });
}

export async function startResearch(
  question: string
): Promise<{ research_id: string; status: string }> {
  return fetchApi("/api/research", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export async function getResearch(id: string): Promise<ResearchResult> {
  return fetchApi(`/api/research/${id}`);
}

export async function getResearchPapers(id: string): Promise<{ papers: Paper[] }> {
  return fetchApi(`/api/research/${id}/papers`);
}

export async function getVerification(
  id: string
): Promise<VerificationReport | Record<string, never>> {
  return fetchApi(`/api/research/${id}/verification`);
}

export async function getPaper(id: string): Promise<Paper & { id: string }> {
  return fetchApi(`/api/papers/${id}`);
}

export async function getHistory(): Promise<{ items: HistoryItem[] }> {
  return fetchApi("/api/research");
}

export async function getEvaluation(): Promise<EvaluationMetrics> {
  return fetchApi("/api/evaluation");
}
