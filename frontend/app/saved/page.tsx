"use client";

import { useEffect, useState } from "react";
import { Bookmark } from "lucide-react";

export default function SavedPage() {
  const [saved, setSaved] = useState<string[]>([]);

  useEffect(() => {
    try {
      const data = localStorage.getItem("cea_saved");
      if (data) setSaved(JSON.parse(data));
    } catch {}
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Saved Research</h1>
      <p className="text-sm text-slate-600 mb-6">Bookmarked papers and research reports.</p>

      {saved.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <Bookmark className="h-10 w-10 mx-auto mb-3 opacity-40" />
          <p>No saved items yet.</p>
          <p className="text-xs mt-2">Save papers from research results to access them here.</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {saved.map((id) => (
            <li key={id} className="rounded-xl border border-surface-border bg-white p-4 text-sm">
              {id}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
