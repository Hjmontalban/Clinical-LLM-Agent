"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { getEvaluation } from "@/lib/api";
import type { EvaluationMetrics } from "@/lib/types";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getEvaluation()
      .then(setMetrics)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const chartData = metrics
    ? [
        { name: "Supported", value: metrics.claims_supported, color: "#10b981" },
        { name: "Partial", value: metrics.claims_partially_supported, color: "#f59e0b" },
        {
          name: "Other",
          value: Math.max(
            0,
            metrics.total_claims_analyzed -
              metrics.claims_supported -
              metrics.claims_partially_supported
          ),
          color: "#94a3b8",
        },
      ]
    : [];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">AI Evaluation</h1>
      <p className="text-sm text-slate-600 mb-6">
        Metrics computed from actual completed research sessions — not hardcoded.
      </p>

      {loading ? (
        <div className="h-64 bg-slate-200 rounded-2xl animate-pulse" />
      ) : !metrics ? (
        <Card>
          <CardContent className="py-12 text-center text-slate-500">
            No evaluation data yet. Complete some research queries first.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: "Research Completed", value: metrics.total_research_completed },
              { label: "Claims Analyzed", value: metrics.total_claims_analyzed },
              { label: "Citation Coverage", value: `${metrics.avg_citation_coverage}%` },
              { label: "Claims Supported", value: metrics.claims_supported },
              { label: "Partially Supported", value: metrics.claims_partially_supported },
              { label: "Unsupported Rate", value: `${metrics.unsupported_claim_rate}%` },
            ].map(({ label, value }) => (
              <Card key={label}>
                <CardContent className="pt-5">
                  <p className="text-2xl font-bold text-slate-900">{value}</p>
                  <p className="text-xs text-slate-500 mt-1">{label}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {metrics.total_claims_analyzed > 0 && (
            <Card>
              <CardHeader>
                <h2 className="font-semibold text-slate-900">Claim Verification Breakdown</h2>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ left: 20 }}>
                      <XAxis type="number" />
                      <YAxis type="category" dataKey="name" width={80} />
                      <Tooltip />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {chartData.map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}

          <p className="text-xs text-slate-400">{metrics.note}</p>
        </div>
      )}
    </div>
  );
}
