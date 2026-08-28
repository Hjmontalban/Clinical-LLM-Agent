"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Clock, ChevronRight } from "lucide-react";
import { getHistory } from "@/lib/api";
import type { HistoryItem } from "@/lib/types";
import { Badge } from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHistory()
      .then((data) => setItems(data.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Research History</h1>
      <p className="text-sm text-slate-600 mb-6">Your recent evidence research queries.</p>

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-slate-200 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <Clock className="h-10 w-10 mx-auto mb-3 opacity-40" />
          <p>No research history yet.</p>
          <Link href="/search" className="text-brand-600 text-sm mt-2 inline-block hover:underline">
            Start your first research query
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Link
              key={item.research_id}
              href={`/research/${item.research_id}`}
              className="flex items-center gap-4 rounded-2xl border border-surface-border bg-white p-4 hover:shadow-md transition-shadow group"
            >
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 text-sm line-clamp-2 group-hover:text-brand-700">
                  {item.question}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant={item.status === "completed" ? "success" : "info"}>
                    {item.status}
                  </Badge>
                  {item.evidence_strength && (
                    <Badge>{item.evidence_strength}</Badge>
                  )}
                  {item.created_at && (
                    <span className="text-xs text-slate-400">{formatDate(item.created_at)}</span>
                  )}
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-slate-300 group-hover:text-brand-600 shrink-0" />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
