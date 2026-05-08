import { useState } from "react";
import { Search, RefreshCw, Loader2, CheckCircle2, XCircle, Clock, Zap } from "lucide-react";
import type { SubjectType, ReportStatus } from "../data/types";

const SUBJECT_TYPES: { value: SubjectType; label: string }[] = [
  { value: "product",    label: "Product" },
  { value: "company",   label: "Company" },
  { value: "concept",   label: "Concept" },
  { value: "person",    label: "Person" },
  { value: "technology",label: "Technology" },
  { value: "other",     label: "Other" },
];

interface StatusConfig {
  icon: React.ReactNode;
  label: string;
  color: string;
}

function getStatusConfig(status: ReportStatus | null): StatusConfig | null {
  if (!status) return null;
  const configs: Partial<Record<ReportStatus, StatusConfig>> = {
    pending: {
      icon: <Clock className="w-3 h-3" />,
      label: "Pending",
      color: "text-[#78716c]",
    },
    planning: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Planning",
      color: "text-[#78716c]",
    },
    searching: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Searching",
      color: "text-[#78716c]",
    },
    scraping: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Scraping",
      color: "text-[#78716c]",
    },
    filtering: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Filtering evidence",
      color: "text-[#78716c]",
    },
    analyzing_vertical: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Analyzing",
      color: "text-[#78716c]",
    },
    analyzing_horizontal: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Analyzing",
      color: "text-[#78716c]",
    },
    synthesizing: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Synthesizing",
      color: "text-[#78716c]",
    },
    quality_checking: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Quality check",
      color: "text-[#78716c]",
    },
    persisting: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      label: "Saving",
      color: "text-[#78716c]",
    },
    completed: {
      icon: <CheckCircle2 className="w-3 h-3" />,
      label: "Completed",
      color: "text-[#3a6048]",
    },
    failed: {
      icon: <XCircle className="w-3 h-3" />,
      label: "Failed",
      color: "text-red-600",
    },
  };
  return configs[status] ?? null;
}

interface ResearchInputBarProps {
  activeStatus: ReportStatus | null;
  onSubmit: (topic: string, subjectType: SubjectType, forceRefresh: boolean) => void;
}

export function ResearchInputBar({ activeStatus, onSubmit }: ResearchInputBarProps) {
  const [topic, setTopic] = useState("");
  const [subjectType, setSubjectType] = useState<SubjectType>("product");

  const isRunning =
    activeStatus !== null &&
    activeStatus !== "completed" &&
    activeStatus !== "failed" &&
    activeStatus !== "empty";

  const statusConfig = getStatusConfig(activeStatus);

  function handleSubmit(forceRefresh = false) {
    if (!topic.trim() || isRunning) return;
    onSubmit(topic.trim(), subjectType, forceRefresh);
  }

  return (
    <header className="h-14 bg-white border-b border-[#ddd8cd] flex items-center px-5 gap-4 shrink-0 z-20">
      {/* Logo mark — warm charcoal instead of cold navy */}
      <div className="flex items-center gap-2.5 shrink-0">
        <div className="w-7 h-7 bg-[#292524] rounded-md flex items-center justify-center">
          <Zap className="w-3.5 h-3.5 text-[#e8e4da]" />
        </div>
        <span className="text-[13px] tracking-tight text-[#1c1917]" style={{ fontWeight: 600, letterSpacing: "-0.01em" }}>
          HV Analysis
        </span>
      </div>

      <div className="w-px h-5 bg-[#ddd8cd] shrink-0" />

      {/* Topic input */}
      <div className="flex-1 relative min-w-0">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#c8c0b4]" />
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="Enter research topic — e.g. GPT-4o, Cursor AI, LangChain, Sam Altman..."
          className="w-full h-8 pl-8 pr-3 bg-[#f5f2eb] border border-[#ddd8cd] rounded-md text-[13px] text-[#1c1917] placeholder:text-[#b8b0a8] focus:outline-none focus:ring-1 focus:ring-[#292524]/40 focus:border-[#292524]/60 transition-colors"
          disabled={isRunning}
        />
      </div>

      {/* Subject type */}
      <select
        value={subjectType}
        onChange={(e) => setSubjectType(e.target.value as SubjectType)}
        className="h-8 pl-3 pr-7 bg-[#f5f2eb] border border-[#ddd8cd] rounded-md text-[13px] text-[#44403c] focus:outline-none focus:ring-1 focus:ring-[#292524]/40 appearance-none cursor-pointer shrink-0"
        disabled={isRunning}
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a8a29e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
          backgroundRepeat: "no-repeat",
          backgroundPosition: "right 8px center",
        }}
      >
        {SUBJECT_TYPES.map((t) => (
          <option key={t.value} value={t.value}>
            {t.label}
          </option>
        ))}
      </select>

      {/* Force Refresh */}
      <button
        onClick={() => handleSubmit(true)}
        disabled={!topic.trim() || isRunning}
        className="h-8 px-3 flex items-center gap-1.5 text-[13px] text-[#57534e] bg-white border border-[#ddd8cd] rounded-md hover:bg-[#f5f2eb] hover:border-[#ccc7bc] disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0"
        title="Force refresh — ignore cache and re-run research"
      >
        <RefreshCw className="w-3 h-3" />
        <span>Force Refresh</span>
      </button>

      {/* Deep Research CTA — warm charcoal, not cold navy */}
      <button
        onClick={() => handleSubmit(false)}
        disabled={!topic.trim() || isRunning}
        className="h-8 px-4 flex items-center gap-1.5 text-[13px] text-[#e8e4da] bg-[#292524] rounded-md hover:bg-[#1c1a18] disabled:opacity-40 disabled:cursor-not-allowed transition-colors shrink-0 shadow-sm"
      >
        {isRunning ? (
          <>
            <Loader2 className="w-3 h-3 animate-spin" />
            <span>Running...</span>
          </>
        ) : (
          <>
            <Search className="w-3 h-3" />
            <span>Deep Research</span>
          </>
        )}
      </button>

      {/* Status indicator */}
      {statusConfig && (
        <div className={`flex items-center gap-1.5 text-[12px] shrink-0 ${statusConfig.color}`}>
          {statusConfig.icon}
          <span>{statusConfig.label}</span>
        </div>
      )}
    </header>
  );
}
