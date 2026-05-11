import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Clock,
  Database,
  FileSearch,
  Search,
  Users,
  LayoutDashboard,
  TrendingUp,
  GitCompare,
  FileText,
} from "lucide-react";
import * as Tabs from "@radix-ui/react-tabs";
import type { HistoryReport, NarrativeReportData, FutureScenarios } from "../data/types";
import { ProgressPanel } from "./ProgressPanel";
import { OverviewTab } from "./tabs/OverviewTab";
import { VerticalAnalysisTab } from "./tabs/VerticalAnalysisTab";
import { HorizontalAnalysisTab } from "./tabs/HorizontalAnalysisTab";

function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function QualityScore({ score }: { score: number }) {
  const color =
    score >= 85 ? "text-[#3a6048]" : score >= 70 ? "text-amber-700" : "text-red-700";
  // Warm muted backgrounds — was emerald-50/amber-50/red-50 (cool-tinted whites)
  const bg =
    score >= 85 ? "bg-[#e8f0e8] border-[#b0ceb8]" : score >= 70 ? "bg-amber-50 border-amber-200" : "bg-red-50 border-red-200";
  return (
    <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded border ${bg}`}>
      <span className="text-[11px] text-[#78716c]">Quality</span>
      <span className={`text-[13px] ${color}`} style={{ fontWeight: 600 }}>
        {score}
        <span className="text-[11px]">/100</span>
      </span>
    </div>
  );
}

// ── Empty State ────────────────────────────────────────────────────────────
function EmptyState() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-8 py-16 text-center bg-[#f5f2eb]">
      <div className="w-12 h-12 rounded-xl bg-white border border-[#ddd8cd] flex items-center justify-center mb-4">
        <FileSearch className="w-6 h-6 text-[#a8a29e]" />
      </div>
      <h2 className="text-[#1e293b] mb-2" style={{ fontSize: "18px", fontWeight: 500 }}>
        No report selected
      </h2>
      <p className="text-[14px] text-[#78716c] max-w-md mb-6">
        Enter a research topic in the input bar above and click{" "}
        <span className="font-mono text-[#44403c] bg-white border border-[#ddd8cd] px-1.5 py-0.5 rounded text-[13px]">
          Deep Research
        </span>{" "}
        to generate a structured analysis report.
      </p>

      <div className="grid grid-cols-3 gap-3 max-w-lg text-left">
        {[
          {
            icon: <Search className="w-4 h-4 text-[#5b7fa6]" />,
            title: "Topic Input",
            desc: "Enter any product, company, person, technology, or concept",
          },
          {
            icon: <Database className="w-4 h-4 text-[#8b7ab0]" />,
            title: "Evidence Collection",
            desc: "Agent searches and scrapes 10+ authoritative sources",
          },
          {
            icon: <FileSearch className="w-4 h-4 text-[#4d9070]" />,
            title: "Structured Report",
            desc: "Get Overview, Vertical, and Horizontal analysis tabs",
          },
        ].map((item, i) => (
          <div
            key={i}
            className="bg-white border border-[#ddd8cd] rounded-md px-4 py-3"
          >
            <div className="mb-2">{item.icon}</div>
            <p className="text-[13px] text-[#1e293b] mb-1" style={{ fontWeight: 500 }}>
              {item.title}
            </p>
            <p className="text-[12px] text-[#78716c] leading-snug">{item.desc}</p>
          </div>
        ))}
      </div>

      <p className="text-[12px] text-[#a8a29e] mt-6">
        Select a report from the history panel, or create a new one above
      </p>
    </div>
  );
}

// ── Failed State ───────────────────────────────────────────────────────────
function FailedState({
  report,
  onRetry,
}: {
  report: HistoryReport;
  onRetry: () => void;
}) {
  return (
    <div className="flex-1 flex flex-col items-start px-8 py-8 overflow-y-auto bg-[#f5f2eb]">
      {/* Failed header */}
      <div className="flex items-center gap-2 mb-4">
        <XCircle className="w-5 h-5 text-red-500" />
        <span className="text-[15px] text-red-600" style={{ fontWeight: 500 }}>
          Research Failed
        </span>
      </div>
      <h2 className="text-[#0f172a] mb-1" style={{ fontSize: "20px", fontWeight: 600 }}>
        {report.topic}
      </h2>
      <p className="text-[13px] text-[#a8a29e] mb-6 flex items-center gap-1.5">
        <Clock className="w-3.5 h-3.5" />
        Attempted {formatDateTime(report.created_at)}
      </p>

      {/* Error message */}
      {report.error_message && (
        <div className="w-full max-w-2xl bg-red-50 border border-red-200 rounded-md px-4 py-4 mb-6">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
            <div>
              <p className="text-[13px] text-red-800 mb-2" style={{ fontWeight: 500 }}>
                Error details
              </p>
              <p className="text-[13px] text-red-700 leading-relaxed">{report.error_message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Steps that ran */}
      {report.progress_steps.length > 0 && (
        <div className="w-full max-w-2xl mb-6">
          <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-2" style={{ fontWeight: 600 }}>
            Steps completed before failure
          </p>
          <div className="bg-white border border-[#ddd8cd] rounded-md overflow-hidden">
            {report.progress_steps.map((step, idx) => {
              const isLast = idx === report.progress_steps.length - 1;
              let iconEl;
              if (step.status === "completed") {
                iconEl = <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />;
              } else if (step.status === "running") {
                iconEl = <RefreshCw className="w-4 h-4 text-blue-400 shrink-0" />;
              } else if (step.status === "failed") {
                iconEl = <XCircle className="w-4 h-4 text-red-500 shrink-0" />;
              } else {
                iconEl = <div className="w-4 h-4 rounded-full border-2 border-[#ddd8cd] shrink-0" />;
              }
              return (
                <div
                  key={step.step_id}
                  className={`flex items-start gap-3 px-4 py-2.5 ${!isLast ? "border-b border-[#ebe7de]" : ""} ${step.status === "failed" ? "bg-red-50" : ""}`}
                >
                  {iconEl}
                  <div>
                    <span className={`text-[13px] ${step.status === "pending" ? "text-[#a8a29e]" : step.status === "failed" ? "text-red-700" : "text-[#374151]"}`}>
                      {step.label}
                    </span>
                    {step.message && step.status !== "pending" && (
                      <p className={`text-[12px] mt-0.5 ${step.status === "failed" ? "text-red-500" : "text-[#a8a29e]"}`}>{step.message}</p>
                    )}
                  </div>
                  {step.timestamp && (
                    <span className="ml-auto text-[11px] text-[#a8a29e] shrink-0">{step.timestamp}</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Retry button */}
      <div>
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-[#292524] text-[#e8e4da] text-[13px] rounded-md hover:bg-[#1c1a18] transition-colors shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry with Force Refresh
        </button>
        <p className="text-[12px] text-[#a8a29e] mt-2">
          Force Refresh ignores cache and retries with extended tool call budget
        </p>
      </div>
    </div>
  );
}

// ── Completed Report ───────────────────────────────────────────────────────
const SUBJECT_TYPE_LABELS: Record<string, string> = {
  product: "Product",
  company: "Company",
  concept: "Concept",
  person: "Person",
  technology: "Technology",
  other: "Other",
};

const REPORT_TABS = [
  { value: "overview", label: "Overview", icon: <LayoutDashboard className="w-3.5 h-3.5" /> },
  { value: "vertical", label: "Vertical Analysis", icon: <TrendingUp className="w-3.5 h-3.5" /> },
  { value: "horizontal", label: "Horizontal Analysis", icon: <GitCompare className="w-3.5 h-3.5" /> },
  { value: "narrative", label: "Narrative", icon: <FileText className="w-3.5 h-3.5" /> },
];

const LIKELIHOOD_STYLES: Record<"high" | "medium" | "low", string> = {
  high: "bg-[#e8f0e8] text-[#3a6048]",
  medium: "bg-amber-50 text-amber-700",
  low: "bg-red-50 text-red-700",
};

function EvidenceChip({ id }: { id: string }) {
  return (
    <span className="inline-flex items-center text-[10px] text-[#6b6560] bg-[#eae6de] border border-[#ddd8cd] rounded px-1.5 py-0.5 font-mono cursor-default hover:bg-[#ddd8cd] transition-colors">
      {id}
    </span>
  );
}

function NarrativeSectionCard({ title, content, evidenceIds }: { title: string; content: string; evidenceIds: string[] }) {
  return (
    <div className="bg-white border border-[#ddd8cd] rounded-md px-4 py-4">
      <div className="flex items-start gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h4 className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
            {title}
          </h4>
        </div>
      </div>
      <p className="text-[12px] text-[#44403c] leading-relaxed">{content}</p>
      {evidenceIds.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {evidenceIds.map((id) => (
            <EvidenceChip key={id} id={id} />
          ))}
        </div>
      )}
    </div>
  );
}

function FutureScenarioCard({ scenario }: { scenario: FutureScenarios }) {
  return (
    <div className="bg-white border border-[#ddd8cd] rounded-md px-4 py-4">
      <div className="flex items-start gap-2 mb-2 flex-wrap">
        <h4 className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
          {scenario.most_likely}
        </h4>
        <span className={`text-[10px] px-1.5 py-0.5 rounded ${LIKELIHOOD_STYLES.high}`}>
          Most likely
        </span>
      </div>
      <p className="text-[12px] text-[#44403c] leading-relaxed">{scenario.most_dangerous}</p>
      <p className="text-[12px] text-[#44403c] leading-relaxed mt-2">{scenario.most_optimistic}</p>
      {scenario.supporting_evidence_ids.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {scenario.supporting_evidence_ids.map((id) => (
            <EvidenceChip key={id} id={id} />
          ))}
        </div>
      )}
    </div>
  );
}

function NarrativeTab({ data }: { data: NarrativeReportData | null | undefined }) {
  if (!data) {
    return (
      <div className="flex items-center justify-center py-16 text-center">
        <div>
          <FileText className="w-8 h-8 text-[#c8c0b4] mx-auto mb-2" />
          <p className="text-[13px] text-[#a8a29e]">Narrative report not available</p>
          <p className="text-[12px] text-[#c8c0b4] mt-1">The report has not generated the longform narrative layer yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section>
        <div className="flex items-center gap-1.5 mb-2">
          <FileText className="w-3.5 h-3.5 text-[#a8a29e]" />
          <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
            Narrative Report
          </h3>
        </div>
        <div className="bg-white border border-[#ddd8cd] rounded-md px-5 py-4 space-y-3">
          <div>
            <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1" style={{ fontWeight: 600 }}>
              Definition
            </p>
            <p className="text-[13px] text-[#44403c] leading-relaxed">{data.one_sentence_definition}</p>
          </div>
          <div>
            <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1" style={{ fontWeight: 600 }}>
              Opening Judgment
            </p>
            <p className="text-[13px] text-[#44403c] leading-relaxed">{data.opening_judgment}</p>
          </div>
          <div>
            <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1" style={{ fontWeight: 600 }}>
              Source Notes
            </p>
            <ul className="space-y-1">
              {data.source_notes.map((note) => (
                <li key={note} className="text-[12px] text-[#78716c] leading-snug">
                  {note}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {data.vertical_story.length > 0 && (
        <section>
          <div className="flex items-center gap-1.5 mb-2">
            <TrendingUp className="w-3.5 h-3.5 text-[#a8a29e]" />
            <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
              Vertical Story
            </h3>
          </div>
          <div className="space-y-2">
            {data.vertical_story.map((section) => (
              <NarrativeSectionCard
                key={section.section_id}
                title={section.title}
                content={section.content}
                evidenceIds={section.supporting_evidence_ids}
              />
            ))}
          </div>
        </section>
      )}

      {data.horizontal_comparison.length > 0 && (
        <section>
          <div className="flex items-center gap-1.5 mb-2">
            <GitCompare className="w-3.5 h-3.5 text-[#a8a29e]" />
            <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
              Horizontal Comparison
            </h3>
          </div>
          <div className="space-y-2">
            {data.horizontal_comparison.map((section) => (
              <NarrativeSectionCard
                key={section.section_id}
                title={section.title}
                content={section.content}
                evidenceIds={section.supporting_evidence_ids}
              />
            ))}
          </div>
        </section>
      )}

      {data.intersection_insights.length > 0 && (
        <section>
          <div className="flex items-center gap-1.5 mb-2">
            <FileText className="w-3.5 h-3.5 text-[#a8a29e]" />
            <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
              Intersection Insights
            </h3>
          </div>
          <div className="space-y-2">
            {data.intersection_insights.map((section) => (
              <NarrativeSectionCard
                key={section.section_id}
                title={section.title}
                content={section.content}
                evidenceIds={section.supporting_evidence_ids}
              />
            ))}
          </div>
        </section>
      )}

      <section>
        <div className="flex items-center gap-1.5 mb-2">
          <FileText className="w-3.5 h-3.5 text-[#a8a29e]" />
          <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
            Future Scenarios
          </h3>
        </div>
        <div className="bg-white border border-[#ddd8cd] rounded-md px-5 py-4 space-y-4">
          <div>
            <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1" style={{ fontWeight: 600 }}>
              Most Likely
            </p>
            <p className="text-[13px] text-[#44403c] leading-relaxed">{data.future_scenarios.most_likely}</p>
          </div>
          <div>
            <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1" style={{ fontWeight: 600 }}>
              Most Dangerous
            </p>
            <p className="text-[13px] text-[#44403c] leading-relaxed">{data.future_scenarios.most_dangerous}</p>
          </div>
          <div>
            <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1" style={{ fontWeight: 600 }}>
              Most Optimistic
            </p>
            <p className="text-[13px] text-[#44403c] leading-relaxed">{data.future_scenarios.most_optimistic}</p>
          </div>
          {data.future_scenarios.supporting_evidence_ids.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {data.future_scenarios.supporting_evidence_ids.map((id) => (
                <EvidenceChip key={id} id={id} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function CompletedReport({ report }: { report: HistoryReport }) {
  const [activeTab, setActiveTab] = useState("overview");
  const rd = report.report_data!;

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Report Header */}
      <div className="px-6 py-4 border-b border-[#ddd8cd] bg-white shrink-0">
        <div className="flex items-start gap-3">
          <div className="flex-1 min-w-0">
            {/* Status row */}
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="text-[11px] text-[#6b6560] bg-[#eae6de] border border-[#ddd8cd] px-2 py-0.5 rounded uppercase tracking-wide" style={{ fontWeight: 600 }}>
                {SUBJECT_TYPE_LABELS[rd.subject_type] ?? rd.subject_type}
              </span>
              {report.quality_warning ? (
                <div className="flex items-center gap-1 text-[12px] text-amber-600">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Quality warning</span>
                </div>
              ) : (
                <div className="flex items-center gap-1 text-[12px] text-emerald-600">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Completed</span>
                </div>
              )}
            </div>

            {/* Title */}
            <h1 className="text-[#0f172a] leading-tight mb-0.5" style={{ fontSize: "20px", fontWeight: 600 }}>
              {rd.title}
            </h1>
            {rd.subtitle && (
              <p className="text-[13px] text-[#78716c]">{rd.subtitle}</p>
            )}
          </div>

          {/* Metadata */}
          <div className="flex items-center gap-3 shrink-0">
            <QualityScore score={rd.quality_score} />
            <div className="text-right">
              <p className="text-[11px] text-[#a8a29e]">Generated</p>
              <p className="text-[12px] text-[#78716c]">{formatDateTime(rd.generated_at)}</p>
            </div>
          </div>
        </div>

        {/* Stats bar */}
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[#ebe7de]">
          <div className="flex items-center gap-1.5 text-[12px] text-[#a8a29e]">
            <Database className="w-3 h-3" />
            <span>
              <span className="text-[#374151]" style={{ fontWeight: 500 }}>
                {rd.source_count}
              </span>{" "}
              sources
            </span>
          </div>
          <span className="text-[#ddd8cd]">·</span>
          <div className="flex items-center gap-1.5 text-[12px] text-[#a8a29e]">
            <FileText className="w-3 h-3" />
            <span>
              <span className="text-[#374151]" style={{ fontWeight: 500 }}>
                {rd.evidence_count}
              </span>{" "}
              evidence cards
            </span>
          </div>
          <span className="text-[#ddd8cd]">·</span>
          <div className="flex items-center gap-1.5 text-[12px] text-[#a8a29e]">
            <Users className="w-3 h-3" />
            <span>
              <span className="text-[#374151]" style={{ fontWeight: 500 }}>
                {rd.horizontal.competitor_matrix.length}
              </span>{" "}
              competitors mapped
            </span>
          </div>
          {rd.limitations.length > 0 && (
            <>
              <span className="text-[#ddd8cd]">·</span>
              <div className="flex items-center gap-1 text-[12px] text-[#a8a29e]">
                <AlertTriangle className="w-3 h-3 text-amber-400" />
                <span>{rd.limitations.length} limitation{rd.limitations.length !== 1 ? "s" : ""} noted</span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs.Root
        value={activeTab}
        onValueChange={setActiveTab}
        className="flex-1 flex flex-col overflow-hidden"
      >
        <Tabs.List className="flex items-center px-6 border-b border-[#ddd8cd] bg-white shrink-0">
          {REPORT_TABS.map((tab) => (
            <Tabs.Trigger
              key={tab.value}
              value={tab.value}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-[13px] border-b-2 transition-colors cursor-pointer -mb-px ${
                activeTab === tab.value
                  ? "border-[#292524] text-[#292524]"
                  : "border-transparent text-[#78716c] hover:text-[#292524]"
              }`}
              style={{ fontWeight: activeTab === tab.value ? 500 : 400 }}
            >
              {tab.icon}
              {tab.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <div className="flex-1 overflow-y-auto bg-[#f5f2eb]">
          <Tabs.Content value="overview" className="px-6 py-5 outline-none">
            <OverviewTab
              data={rd.overview}
              qualityWarning={rd.quality_warning}
              qualityIssues={rd.quality_issues}
              qualityScore={rd.quality_score}
            />
          </Tabs.Content>

          <Tabs.Content value="vertical" className="px-6 py-5 outline-none">
            <VerticalAnalysisTab data={rd.vertical} />
          </Tabs.Content>

          <Tabs.Content value="horizontal" className="px-6 py-5 outline-none">
            <HorizontalAnalysisTab data={rd.horizontal} />
          </Tabs.Content>

          <Tabs.Content value="narrative" className="px-6 py-5 outline-none">
            <NarrativeTab data={rd.narrative_report} />
          </Tabs.Content>
        </div>
      </Tabs.Root>
    </div>
  );
}

// ── Main ReportWorkspace ───────────────────────────────────────────────────
interface ReportWorkspaceProps {
  report: HistoryReport | null;
  onRetry: () => void;
}

export function ReportWorkspace({ report, onRetry }: ReportWorkspaceProps) {
  if (!report) {
    return <EmptyState />;
  }

  const isRunning =
    report.status !== "completed" &&
    report.status !== "failed" &&
    report.status !== "empty";

  if (isRunning) {
    return (
      <ProgressPanel
        topic={report.topic}
        progressMessage={report.progress_message}
        steps={report.progress_steps}
        elapsedLabel="3m 22s"
      />
    );
  }

  if (report.status === "failed") {
    return <FailedState report={report} onRetry={onRetry} />;
  }

  if (report.status === "completed" && report.report_data) {
    return <CompletedReport report={report} />;
  }

  return <EmptyState />;
}