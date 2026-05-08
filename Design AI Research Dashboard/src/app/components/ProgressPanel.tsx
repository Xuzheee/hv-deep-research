import { CheckCircle2, Loader2, Circle, XCircle, Clock } from "lucide-react";
import type { ProgressStep } from "../data/types";

interface ProgressPanelProps {
  topic: string;
  progressMessage: string;
  steps: ProgressStep[];
  elapsedLabel?: string;
}

function StepIcon({ status }: { status: ProgressStep["status"] }) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />;
    case "running":
      return <Loader2 className="w-4 h-4 text-blue-500 animate-spin shrink-0" />;
    case "failed":
      return <XCircle className="w-4 h-4 text-red-500 shrink-0" />;
    default:
      // Warm muted circle — was cool text-[#cbd5e1]
      return <Circle className="w-4 h-4 text-[#c8c0b4] shrink-0" />;
  }
}

export function ProgressPanel({ topic, progressMessage, steps, elapsedLabel }: ProgressPanelProps) {
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const totalCount = steps.length;
  const progressPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="flex-1 flex items-start justify-center pt-16 px-8 bg-[#f5f2eb]">
      <div className="w-full max-w-xl">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <Loader2 className="w-4 h-4 text-[#78716c] animate-spin" />
            <span className="text-[13px] text-[#57534e]" style={{ fontWeight: 500 }}>
              Deep Research in progress
            </span>
            {elapsedLabel && (
              <span className="ml-auto text-[12px] text-[#a8a29e] flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {elapsedLabel}
              </span>
            )}
          </div>
          <h2 className="text-[#0f172a] mb-2" style={{ fontSize: "18px" }}>
            Researching:{" "}
            <span style={{ fontWeight: 600 }}>{topic}</span>
          </h2>
          <p className="text-[13px] text-[#78716c]">{progressMessage}</p>
        </div>

        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[12px] text-[#78716c]">
              {completedCount} / {totalCount} steps
            </span>
            <span className="text-[12px] text-[#78716c]">{progressPct}%</span>
          </div>
          <div className="h-1.5 bg-[#ddd8cd] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#292524] rounded-full transition-all duration-700"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        {/* Steps list */}
        <div className="bg-white border border-[#ddd8cd] rounded-lg overflow-hidden">
          {steps.map((step, idx) => (
            <div
              key={step.step_id}
              className={`flex items-start gap-3 px-4 py-3 ${
                idx < steps.length - 1 ? "border-b border-[#ebe7de]" : ""
              } ${step.status === "running" ? "bg-[#f0ede5]" : ""}`}
            >
              <StepIcon status={step.status} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[13px] ${
                      step.status === "pending"
                        ? "text-[#a8a29e]"
                        : step.status === "running"
                        ? "text-[#292524]"
                        : step.status === "failed"
                        ? "text-red-700"
                        : "text-[#374151]"
                    }`}
                    style={{ fontWeight: step.status === "running" ? 500 : 400 }}
                  >
                    {step.label}
                  </span>
                  {step.timestamp && step.status === "completed" && (
                    <span className="ml-auto text-[11px] text-[#a8a29e] shrink-0">{step.timestamp}</span>
                  )}
                </div>
                {step.message && step.status !== "pending" && (
                  <p
                    className={`text-[12px] mt-0.5 ${
                      step.status === "running"
                        ? "text-[#78716c]"
                        : step.status === "failed"
                        ? "text-red-500"
                        : "text-[#a8a29e]"
                    }`}
                  >
                    {step.message}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        <p className="text-[12px] text-[#a8a29e] text-center mt-4">
          Research typically takes 1–5 minutes. This page will update automatically.
        </p>
      </div>
    </div>
  );
}