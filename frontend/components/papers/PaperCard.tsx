import { Card, CardContent, Badge } from "@/components/ui/Card";
import { ExternalLink, Users } from "lucide-react";
import type { Paper } from "@/lib/types";
import { cn } from "@/lib/utils";

interface PaperCardProps {
  paper: Paper;
  index?: number;
  onClick?: () => void;
}

export function PaperCard({ paper, index, onClick }: PaperCardProps) {
  const authors = paper.authors?.length
    ? paper.authors.slice(0, 3).join(", ") + (paper.authors.length > 3 ? " et al." : "")
    : "Unknown authors";

  return (
    <Card
      className={cn("transition-shadow hover:shadow-md cursor-pointer", onClick && "cursor-pointer")}
      onClick={onClick}
    >
      <CardContent className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            {index !== undefined && (
              <span className="text-xs font-mono text-brand-600 font-semibold">[{index + 1}]</span>
            )}
            <h3 className="font-semibold text-slate-900 text-sm leading-snug mt-0.5 line-clamp-2">
              {paper.title}
            </h3>
          </div>
          {paper.relevance_score !== undefined && paper.relevance_score > 0 && (
            <Badge variant="info">{Math.round(paper.relevance_score * 100)}%</Badge>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
          {paper.year && <span>{paper.year}</span>}
          {paper.study_type && (
            <>
              <span>·</span>
              <Badge>{paper.study_type}</Badge>
            </>
          )}
          {paper.journal && (
            <>
              <span>·</span>
              <span className="truncate max-w-[150px]">{paper.journal}</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <Users className="h-3.5 w-3.5 shrink-0" />
          <span className="line-clamp-1">{authors}</span>
        </div>

        {paper.abstract && (
          <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed">{paper.abstract}</p>
        )}

        <div className="flex flex-wrap gap-2 pt-1">
          {paper.pmid && (
            <span className="text-xs text-slate-400 font-mono">PMID: {paper.pmid}</span>
          )}
          {paper.doi && (
            <span className="text-xs text-slate-400 font-mono truncate max-w-[200px]">DOI: {paper.doi}</span>
          )}
          {paper.url && (
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="inline-flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700 ml-auto"
            >
              Open <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
