import Link from "next/link";
import { SearchBox } from "@/components/search/SearchBox";
import {
  Search,
  FileCheck,
  GitCompare,
  Shield,
  ArrowRight,
} from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Multi-source search",
    description: "PubMed, Semantic Scholar, and OpenAlex searched concurrently with deduplication.",
  },
  {
    icon: FileCheck,
    title: "Evidence synthesis",
    description: "PICO-style query planning with structured evidence tables and confidence ratings.",
  },
  {
    icon: GitCompare,
    title: "Conflict detection",
    description: "Identifies disagreements between studies and explains possible reasons.",
  },
  {
    icon: Shield,
    title: "Citation verification",
    description: "Claim-level verification ensures citations actually support generated statements.",
  },
];

export default function HomePage() {
  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <section className="relative overflow-hidden bg-white border-b border-surface-border">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-50 via-white to-white" />
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 py-12 sm:py-20 text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-brand-50 border border-brand-200 px-3 py-1 text-xs font-medium text-brand-700 mb-6">
            Evidence-grounded research tool
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-900 tracking-tight leading-tight">
            Understand Biomedical
            <br />
            <span className="text-brand-600">Evidence Faster</span>
          </h1>
          <p className="mt-4 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Search scientific literature, compare evidence, verify citations, and explore
            uncertainty with an AI-assisted research workflow.
          </p>
          <div className="mt-8">
            <SearchBox variant="hero" />
          </div>
          <p className="mt-4 text-xs text-slate-400">
            Do not enter personally identifiable patient information.
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
        <div className="grid sm:grid-cols-2 gap-4 sm:gap-6">
          {features.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="rounded-2xl border border-surface-border bg-white p-5 sm:p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 mb-4">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="font-semibold text-slate-900">{title}</h3>
              <p className="text-sm text-slate-600 mt-2 leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 pb-16">
        <div className="rounded-2xl bg-slate-900 text-white p-8 sm:p-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div>
            <h2 className="text-xl font-semibold">Ready to explore the evidence?</h2>
            <p className="text-slate-400 text-sm mt-2">
              Start a research query and get a verified evidence report in minutes.
            </p>
          </div>
          <Link
            href="/search"
            className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl px-5 py-3 text-sm font-medium transition-colors min-h-[44px]"
          >
            Start Research <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
