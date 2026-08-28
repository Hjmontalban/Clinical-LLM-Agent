import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import type { ProgressStep } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ProgressTracker({ steps }: { steps: ProgressStep[] }) {
  if (!steps.length) return null;

  return (
    <div className="space-y-0">
      {steps.map((step, i) => (
        <div key={step.key} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div className="mt-0.5">
              {step.status === "completed" && (
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              )}
              {step.status === "active" && (
                <Loader2 className="h-5 w-5 text-brand-600 animate-spin" />
              )}
              {step.status === "pending" && (
                <Circle className="h-5 w-5 text-slate-300" />
              )}
            </div>
            {i < steps.length - 1 && (
              <div
                className={cn(
                  "w-0.5 flex-1 my-1",
                  step.status === "completed" ? "bg-emerald-300" : "bg-slate-200"
                )}
              />
            )}
          </div>
          <div className="pb-4">
            <p
              className={cn(
                "text-sm font-medium",
                step.status === "active" && "text-brand-700",
                step.status === "completed" && "text-slate-700",
                step.status === "pending" && "text-slate-400"
              )}
            >
              {step.label}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
