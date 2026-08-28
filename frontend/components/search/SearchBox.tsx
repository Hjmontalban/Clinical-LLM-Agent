"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { startResearch } from "@/lib/api";

const EXAMPLE_QUESTIONS = [
  "What does current research say about GLP-1 receptor agonists and cardiovascular outcomes?",
  "What is the evidence for metformin and cardiovascular risk in type 2 diabetes?",
  "How effective are SGLT2 inhibitors for heart failure?",
];

interface SearchBoxProps {
  variant?: "hero" | "compact";
  defaultValue?: string;
}

export function SearchBox({ variant = "hero", defaultValue = "" }: SearchBoxProps) {
  const [question, setQuestion] = useState(defaultValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (question.trim().length < 10) {
      setError("Please enter a research question (at least 10 characters).");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const { research_id } = await startResearch(question.trim());
      router.push(`/research/${research_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start research");
    } finally {
      setLoading(false);
    }
  };

  const isHero = variant === "hero";

  return (
    <div className={isHero ? "w-full max-w-2xl mx-auto" : "w-full"}>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 pointer-events-none" />
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What does current research say about..."
            rows={isHero ? 3 : 2}
            className="w-full rounded-2xl border border-surface-border bg-white pl-12 pr-4 py-4 text-base text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent resize-none shadow-sm"
            aria-label="Research question"
          />
        </div>
        {error && (
          <p className="text-sm text-red-600 px-1" role="alert">{error}</p>
        )}
        <Button type="submit" loading={loading} size="lg" className="w-full sm:w-auto">
          <Sparkles className="h-4 w-4" />
          Search Evidence
        </Button>
      </form>

      {isHero && (
        <div className="mt-6">
          <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">Try an example</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                className="text-left text-xs text-slate-600 bg-slate-50 hover:bg-slate-100 border border-surface-border rounded-xl px-3 py-2 transition-colors"
              >
                {q.length > 60 ? q.slice(0, 60) + "…" : q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
