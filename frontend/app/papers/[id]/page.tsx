"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { getPaper } from "@/lib/api";
import type { Paper } from "@/lib/types";
import { Badge } from "@/components/ui/Card";

export default function PaperPage() {
  const params = useParams();
  const id = params.id as string;
  const [paper, setPaper] = useState<(Paper & { id: string }) | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getPaper(id)
      .then(setPaper)
      .catch((e) => setError(e.message));
  }, [id]);

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600">{error}</p>
        <Link href="/history" className="text-brand-600 text-sm mt-4 inline-block">← Back</Link>
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="animate-pulse h-64 bg-slate-200 rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <Link href="/history" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-brand-600 mb-6">
        <ArrowLeft className="h-4 w-4" /> Back
      </Link>

      <h1 className="text-xl font-bold text-slate-900 leading-snug">{paper.title}</h1>

      <div className="flex flex-wrap gap-2 mt-3">
        {paper.year && <Badge>{paper.year}</Badge>}
        {paper.study_type && <Badge variant="info">{paper.study_type}</Badge>}
        {paper.source && <Badge>{paper.source}</Badge>}
      </div>

      <p className="text-sm text-slate-600 mt-4">
        {paper.authors?.join(", ") || "Unknown authors"}
      </p>
      {paper.journal && (
        <p className="text-sm text-slate-500 mt-1">{paper.journal}</p>
      )}

      {paper.abstract && (
        <div className="mt-6">
          <h2 className="font-semibold text-slate-900 mb-2">Abstract</h2>
          <p className="text-sm text-slate-700 leading-relaxed">{paper.abstract}</p>
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-4 text-xs font-mono text-slate-500">
        {paper.pmid && <span>PMID: {paper.pmid}</span>}
        {paper.doi && <span>DOI: {paper.doi}</span>}
        {paper.pmcid && <span>PMC: {paper.pmcid}</span>}
      </div>

      {paper.url && (
        <a
          href={paper.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 mt-6 text-brand-600 hover:text-brand-700 text-sm font-medium"
        >
          Open Source <ExternalLink className="h-4 w-4" />
        </a>
      )}
    </div>
  );
}
