"use client";

import { useState } from "react";
import { X, ExternalLink } from "lucide-react";
import type { Paper, Claim } from "@/lib/types";
import { Badge } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface CitationDrawerProps {
  paper: Paper | null;
  claim?: Claim | null;
  citationIndex?: number;
  onClose: () => void;
}

export function CitationDrawer({ paper, claim, citationIndex, onClose }: CitationDrawerProps) {
  const [open, setOpen] = useState(!!paper);

  if (!paper) return null;

  const handleClose = () => {
    setOpen(false);
    onClose();
  };

  const statusVariant = (status?: string) => {
    switch (status) {
      case "SUPPORTED": return "success";
      case "PARTIALLY_SUPPORTED": return "warning";
      case "NOT_SUPPORTED":
      case "CONTRADICTED": return "danger";
      default: return "default";
    }
  };

  return (
    <>
      <div
        className="fixed inset-0 bg-black/30 z-50 animate-fade-in"
        onClick={handleClose}
        aria-hidden
      />
      <div
        className={cn(
          "fixed z-50 bg-white shadow-2xl animate-slide-up",
          "inset-x-0 bottom-0 rounded-t-2xl max-h-[85vh] overflow-y-auto",
          "lg:inset-y-0 lg:right-0 lg:left-auto lg:bottom-auto lg:w-[420px] lg:rounded-none lg:rounded-l-2xl"
        )}
        role="dialog"
        aria-label="Citation details"
      >
        <div className="sticky top-0 bg-white border-b border-surface-border px-5 py-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">
              {citationIndex !== undefined ? `Citation [${citationIndex + 1}]` : "Citation"}
            </p>
            <h2 className="font-semibold text-slate-900 text-sm mt-0.5">Source Paper</h2>
          </div>
          <button
            onClick={handleClose}
            className="p-2 rounded-lg hover:bg-slate-100"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          <div>
            <h3 className="font-semibold text-slate-900 leading-snug">{paper.title}</h3>
            <p className="text-sm text-slate-500 mt-2">
              {paper.authors?.slice(0, 4).join(", ")}
              {paper.authors && paper.authors.length > 4 ? " et al." : ""}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              {paper.journal} · {paper.year}
            </p>
          </div>

          {claim && (
            <div className="rounded-xl bg-slate-50 border border-surface-border p-4 space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-500">Verification</span>
                <Badge variant={statusVariant(claim.support_status)}>
                  {claim.support_status.replace(/_/g, " ")}
                </Badge>
              </div>
              {claim.evidence_text && (
                <div>
                  <p className="text-xs font-medium text-slate-500 mb-1">Supporting passage</p>
                  <p className="text-sm text-slate-700 italic">&ldquo;{claim.evidence_text}&rdquo;</p>
                </div>
              )}
              {claim.verification_reason && (
                <p className="text-xs text-slate-500">{claim.verification_reason}</p>
              )}
            </div>
          )}

          {paper.abstract && (
            <div>
              <p className="text-xs font-medium text-slate-500 mb-1">Abstract</p>
              <p className="text-sm text-slate-600 leading-relaxed">{paper.abstract}</p>
            </div>
          )}

          <div className="flex flex-wrap gap-3 text-xs text-slate-500 font-mono">
            {paper.pmid && <span>PMID: {paper.pmid}</span>}
            {paper.doi && <span>DOI: {paper.doi}</span>}
          </div>

          {paper.url && (
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-brand-600 hover:text-brand-700 font-medium"
            >
              Open Source <ExternalLink className="h-4 w-4" />
            </a>
          )}
        </div>
      </div>
    </>
  );
}
