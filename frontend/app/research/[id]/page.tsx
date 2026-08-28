"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ResearchReport } from "@/components/research/ResearchReport";
import { getResearch } from "@/lib/api";
import type { ResearchResult } from "@/lib/types";

export default function ResearchPage() {
  const params = useParams();
  const id = params.id as string;
  const [data, setData] = useState<ResearchResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const poll = async () => {
      const result = await getResearch(id);
      if (!active) return result.status;
      setData(result);
      return result.status;
    };

    const run = async () => {
      try {
        const cached = sessionStorage.getItem(`research_${id}`);
        if (cached) {
          setData(JSON.parse(cached) as ResearchResult);
          return;
        }

        let status = await poll();
        while (active && status && !["completed", "failed"].includes(status)) {
          await new Promise((r) => setTimeout(r, 3000));
          status = await poll();
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load research");
      }
    };

    run();
    return () => {
      active = false;
    };
  }, [id]);

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 rounded-xl w-3/4" />
          <div className="h-32 bg-slate-200 rounded-2xl" />
          <div className="h-48 bg-slate-200 rounded-2xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <ResearchReport data={data} />
    </div>
  );
}
