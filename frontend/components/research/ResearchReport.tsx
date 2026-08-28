"use client";

import { useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  Shield,
  Scale,
} from "lucide-react";
import { Card, CardContent, CardHeader, Badge } from "@/components/ui/Card";
import { PaperCard } from "@/components/papers/PaperCard";
import { ProgressTracker } from "@/components/research/ProgressTracker";
import { CitationDrawer } from "@/components/citations/CitationDrawer";
import type { ResearchResult, Paper } from "@/lib/types";
import { cn } from "@/lib/utils";

function strengthVariant(s?: string) {
  switch (s?.toLowerCase()) {
    case "high": return "success";
    case "moderate": return "info";
    case "low": return "warning";
    case "very low": return "danger";
    default: return "default";
  }
}

interface ResearchReportProps {
  data: ResearchResult;
}

export function ResearchReport({ data }: ResearchReportProps) {
  const [activeTab, setActiveTab] = useState<"findings" | "studies" | "conflicts" | "gaps">("findings");
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [citationIndex, setCitationIndex] = useState<number | undefined>();

  const isProcessing = !["completed", "failed"].includes(data.status);
  const paperMap = Object.fromEntries((data.papers || []).map((p) => [p.id, p]));

  const tabs = [
    { id: "findings" as const, label: "Findings", icon: BookOpen },
    { id: "studies" as const, label: "Studies", icon: BarChart3 },
    { id: "conflicts" as const, label: "Conflicts", icon: Scale },
    { id: "gaps" as const, label: "Gaps", icon: AlertTriangle },
  ];

  const openCitation = (paperId: string, index?: number) => {
    const paper = paperMap[paperId];
    if (paper) {
      setSelectedPaper(paper);
      setCitationIndex(index);
    }
  };

  const renderCitations = (text: string) => {
    const parts = text.split(/(\[[\w_]+\])/g);
    return parts.map((part, i) => {
      const match = part.match(/\[([\w_]+)\]/);
      if (match) {
        const id = match[1];
        const paper = paperMap[id];
        const idx = data.papers?.findIndex((p) => p.id === id);
        return (
          <button
            key={i}
            onClick={() => openCitation(id, idx !== undefined && idx >= 0 ? idx : undefined)}
            className="text-brand-600 hover:text-brand-700 font-mono text-xs mx-0.5 underline-offset-2 hover:underline"
          >
            [{idx !== undefined && idx >= 0 ? idx + 1 : id}]
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  if (data.status === "failed") {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="py-8 text-center">
          <AlertTriangle className="h-10 w-10 text-red-500 mx-auto mb-3" />
          <h2 className="font-semibold text-red-800">Research Failed</h2>
          <p className="text-sm text-red-600 mt-2">{data.error || "An unexpected error occurred."}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Question */}
      <div>
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">Research Question</p>
        <h1 className="text-xl sm:text-2xl font-semibold text-slate-900 leading-snug">{data.question}</h1>
      </div>

      {/* Processing */}
      {isProcessing && (
        <Card>
          <CardHeader>
            <h2 className="font-semibold text-slate-900">Analyzing Evidence</h2>
            <p className="text-sm text-slate-500 mt-1">Searching literature and synthesizing findings…</p>
          </CardHeader>
          <CardContent>
            <ProgressTracker steps={data.progress_steps || []} />
            {data.source_status && (
              <div className="mt-4 flex flex-wrap gap-2">
                {Object.entries(data.source_status).map(([src, status]) => (
                  <Badge key={src} variant={status === "ok" ? "success" : "danger"}>
                    {src}: {status === "ok" ? "✓" : "✗"}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {data.status === "completed" && (
        <>
          {/* Executive Summary */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between flex-wrap gap-2">
                <h2 className="font-semibold text-slate-900">Executive Summary</h2>
                <Badge variant={strengthVariant(data.evidence_strength)}>
                  {data.evidence_strength || "Unknown"} Evidence
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-slate-700 leading-relaxed text-sm sm:text-base whitespace-pre-line">
                {data.executive_summary}
              </p>
              {data.evidence_strength_reason && (
                <p className="text-sm text-slate-500 mt-3 border-t border-surface-border pt-3">
                  <strong>Why:</strong> {data.evidence_strength_reason}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Tabs */}
          <div className="border-b border-surface-border overflow-x-auto">
            <div className="flex gap-1 min-w-max">
              {tabs.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
                    activeTab === id
                      ? "border-brand-600 text-brand-700"
                      : "border-transparent text-slate-500 hover:text-slate-700"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {activeTab === "findings" && (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <h3 className="font-semibold text-slate-900">Key Findings</h3>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {(data.key_findings || []).map((finding, i) => (
                      <li key={i} className="flex gap-3 text-sm text-slate-700 leading-relaxed">
                        <span className="font-semibold text-brand-600 shrink-0">{i + 1}.</span>
                        <span>{renderCitations(finding)}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              {data.limitations && data.limitations.length > 0 && (
                <Card>
                  <CardHeader>
                    <h3 className="font-semibold text-slate-900">Limitations</h3>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {data.limitations.map((l, i) => (
                        <li key={i} className="text-sm text-slate-600 flex gap-2">
                          <span className="text-slate-400">•</span>{l}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {activeTab === "studies" && (
            <div className="space-y-4">
              {/* Desktop table */}
              <div className="hidden md:block overflow-x-auto">
                <Card>
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-surface-border text-left">
                        {["Study", "Year", "Type", "Population", "Outcome", "Result"].map((h) => (
                          <th key={h} className="px-4 py-3 font-medium text-slate-500 text-xs uppercase">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(data.evidence_table || []).map((row, i) => (
                        <tr key={i} className="border-b border-surface-border last:border-0 hover:bg-slate-50">
                          <td className="px-4 py-3 font-medium text-slate-900 max-w-[200px]">
                            <button
                              onClick={() => row.paper_id && openCitation(row.paper_id, i)}
                              className="text-left hover:text-brand-600 line-clamp-2"
                            >
                              {row.study}
                            </button>
                          </td>
                          <td className="px-4 py-3 text-slate-600">{row.year || "—"}</td>
                          <td className="px-4 py-3"><Badge>{row.study_type}</Badge></td>
                          <td className="px-4 py-3 text-slate-600 max-w-[120px] line-clamp-2">{row.population}</td>
                          <td className="px-4 py-3 text-slate-600 max-w-[120px] line-clamp-2">{row.outcome}</td>
                          <td className="px-4 py-3 text-slate-600 max-w-[150px] line-clamp-3">{row.result}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Card>
              </div>

              {/* Mobile cards */}
              <div className="md:hidden space-y-3">
                {(data.papers || []).map((paper, i) => (
                  <PaperCard
                    key={paper.id || i}
                    paper={paper}
                    index={i}
                    onClick={() => setSelectedPaper(paper)}
                  />
                ))}
              </div>
            </div>
          )}

          {activeTab === "conflicts" && (
            <div className="space-y-4">
              {(data.conflicting_evidence || []).length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center text-slate-500 text-sm">
                    No major conflicts identified in the retrieved evidence.
                  </CardContent>
                </Card>
              ) : (
                data.conflicting_evidence!.map((conflict, i) => (
                  <Card key={i}>
                    <CardContent className="space-y-3">
                      <h3 className="font-semibold text-slate-900">{conflict.topic}</h3>
                      <p className="text-sm text-slate-600">{conflict.explanation}</p>
                      <div className="grid sm:grid-cols-2 gap-3">
                        <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-3">
                          <p className="text-xs font-medium text-emerald-700 mb-2">Supports</p>
                          {conflict.supporting_papers.map((id) => (
                            <button
                              key={id}
                              onClick={() => openCitation(id)}
                              className="block text-sm text-emerald-800 hover:underline text-left"
                            >
                              {paperMap[id]?.title?.slice(0, 60) || id}…
                            </button>
                          ))}
                        </div>
                        <div className="rounded-xl bg-red-50 border border-red-200 p-3">
                          <p className="text-xs font-medium text-red-700 mb-2">Conflicts</p>
                          {conflict.conflicting_papers.map((id) => (
                            <button
                              key={id}
                              onClick={() => openCitation(id)}
                              className="block text-sm text-red-800 hover:underline text-left"
                            >
                              {paperMap[id]?.title?.slice(0, 60) || id}…
                            </button>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          )}

          {activeTab === "gaps" && (
            <Card>
              <CardHeader>
                <h3 className="font-semibold text-slate-900">Research Gaps</h3>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {(data.research_gaps || []).map((gap, i) => (
                    <li key={i} className="text-sm text-slate-600 flex gap-2">
                      <span className="text-slate-400">•</span>{gap}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Verification Report */}
          {data.verification && (
            <Card className="border-brand-200 bg-brand-50/30">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-brand-600" />
                  <h3 className="font-semibold text-slate-900">Citation Verification</h3>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div>
                    <p className="text-2xl font-bold text-slate-900">{data.verification.total_claims}</p>
                    <p className="text-xs text-slate-500">Claims analyzed</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-600">{data.verification.supported}</p>
                    <p className="text-xs text-slate-500">Supported</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-amber-600">{data.verification.partially_supported}</p>
                    <p className="text-xs text-slate-500">Partial</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-brand-600">{data.verification.citation_coverage}%</p>
                    <p className="text-xs text-slate-500">Citation coverage</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Disclaimer */}
          <div className="rounded-xl bg-slate-50 border border-surface-border p-4 text-xs text-slate-500 leading-relaxed">
            <strong className="text-slate-700">Disclaimer:</strong> This tool summarizes published research for educational
            and evidence exploration purposes. It is not medical advice. Do not enter personally identifiable patient
            information. Consult qualified healthcare professionals for personal medical decisions.
          </div>
        </>
      )}

      <CitationDrawer
        paper={selectedPaper}
        onClose={() => {
          setSelectedPaper(null);
          setCitationIndex(undefined);
        }}
        citationIndex={citationIndex}
      />
    </div>
  );
}
