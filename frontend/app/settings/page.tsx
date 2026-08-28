"use client";

import { useEffect, useState } from "react";
import { Settings as SettingsIcon, Key, Database, Shield } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";

export default function SettingsPage() {
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "error">("checking");

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.ok ? setApiStatus("ok") : setApiStatus("error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Settings</h1>
      <p className="text-sm text-slate-600 mb-6">Application configuration and status.</p>

      <div className="space-y-4">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-brand-600" />
              <h2 className="font-semibold text-slate-900">API Status</h2>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  apiStatus === "ok" ? "bg-emerald-500" : apiStatus === "error" ? "bg-red-500" : "bg-amber-500 animate-pulse"
                }`}
              />
              <span className="text-sm text-slate-600">
                {apiStatus === "ok" && "Backend API connected"}
                {apiStatus === "error" && "Backend API unavailable — start the server locally"}
                {apiStatus === "checking" && "Checking connection…"}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Key className="h-5 w-5 text-brand-600" />
              <h2 className="font-semibold text-slate-900">LLM Provider</h2>
            </div>
          </CardHeader>
          <CardContent className="text-sm text-slate-600 space-y-2">
            <p>Default: <strong>Groq</strong> (free tier — llama-3.3-70b-versatile)</p>
            <p>Alternative: Google Gemini 2.0 Flash (free tier)</p>
            <p className="text-xs text-slate-400 mt-2">
              Configure GROQ_API_KEY or GEMINI_API_KEY in backend environment variables.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-brand-600" />
              <h2 className="font-semibold text-slate-900">Privacy & Safety</h2>
            </div>
          </CardHeader>
          <CardContent className="text-sm text-slate-600 space-y-2">
            <p>Do not enter personally identifiable patient information.</p>
            <p>This tool provides research summaries, not medical advice.</p>
            <p>For emergencies, contact local emergency services.</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <SettingsIcon className="h-5 w-5 text-brand-600" />
              <h2 className="font-semibold text-slate-900">Literature Sources</h2>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="text-sm text-slate-600 space-y-1">
              <li>• PubMed (NCBI E-utilities)</li>
              <li>• Semantic Scholar</li>
              <li>• OpenAlex</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
