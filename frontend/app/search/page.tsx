import { SearchBox } from "@/components/search/SearchBox";

export default function SearchPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Research Search</h1>
        <p className="text-slate-600 text-sm mt-2">
          Ask a biomedical research question. The system will search multiple literature
          sources, rank evidence, synthesize findings, and verify citations.
        </p>
      </div>
      <SearchBox variant="compact" />
    </div>
  );
}
