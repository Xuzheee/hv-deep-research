import {
  CheckCircle2,
  XCircle,
  Loader2,
  Clock,
  AlertTriangle,
  FileText,
  Plus,
  Package,
  Building2,
  Brain,
  User,
  Cpu,
  MoreHorizontal,
  History,
} from "lucide-react";
import type { HistoryReport, ReportStatus, SubjectType } from "../data/types";

const SUBJECT_LABELS: Record<SubjectType, string> = {
  product:    "Product",
  company:    "Company",
  concept:    "Concept",
  person:     "Person",
  technology: "Technology",
  other:      "Other",
};

const SUBJECT_ICONS: Record<SubjectType, React.ReactNode> = {
  product:    <Package className="w-2.5 h-2.5" />,
  company:    <Building2 className="w-2.5 h-2.5" />,
  concept:    <Brain className="w-2.5 h-2.5" />,
  person:     <User className="w-2.5 h-2.5" />,
  technology: <Cpu className="w-2.5 h-2.5" />,
  other:      <MoreHorizontal className="w-2.5 h-2.5" />,
};

const STATUS_RUNNING_LABELS: Partial<Record<ReportStatus, string>> = {
  pending:              "Pending...",
  planning:             "Planning...",
  searching:            "Searching...",
  scraping:             "Scraping...",
  filtering:            "Filtering...",
  analyzing_vertical:   "Analyzing...",
  analyzing_horizontal: "Analyzing...",
  synthesizing:         "Synthesizing...",
  quality_checking:     "QC check...",
  persisting:           "Saving...",
};

function isRunning(status: ReportStatus): boolean {
  return !["completed", "failed", "empty"].includes(status);
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const min  = Math.floor(diff / 60000);
  const hr   = Math.floor(diff / 3600000);
  const day  = Math.floor(diff / 86400000);
  if (min < 1)  return "just now";
  if (min < 60) return `${min}m ago`;
  if (hr  < 24) return `${hr}h ago`;
  return `${day}d ago`;
}

function StatusIcon({ status }: { status: ReportStatus }) {
  if (isRunning(status))      return <Loader2 className="w-3 h-3 text-[#a8a29e] animate-spin shrink-0" />;
  if (status === "completed") return <CheckCircle2 className="w-3 h-3 text-[#4d9070] shrink-0" />;
  if (status === "failed")    return <XCircle className="w-3 h-3 text-red-500 shrink-0" />;
  return <Clock className="w-3 h-3 text-[#a8a29e] shrink-0" />;
}

interface HistoryItemProps {
  report: HistoryReport;
  isActive: boolean;
  onClick: () => void;
}

function HistoryItem({ report, isActive, onClick }: HistoryItemProps) {
  const running = isRunning(report.status);

  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-2.5 rounded-md transition-colors group ${
        isActive
          ? "bg-[#292524] text-white"           // warm charcoal — not cold navy
          : "hover:bg-[#e8e4da] text-[#374151]"
      }`}
    >
      {/* Title row */}
      <div className="flex items-start gap-2 mb-1">
        <FileText
          className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${
            isActive ? "text-[#c8c3bc]" : "text-[#a8a29e]"  // warm cream instead of blue-200
          }`}
        />
        <span
          className={`text-[13px] leading-snug truncate flex-1 ${
            isActive ? "text-white" : "text-[#1e293b]"
          }`}
          style={{ fontWeight: 500 }}
        >
          {report.topic}
        </span>
        {report.quality_warning && (
          <AlertTriangle className={`w-3 h-3 shrink-0 mt-0.5 ${isActive ? "text-amber-300" : "text-amber-400"}`} />
        )}
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-2 pl-5 flex-wrap">
        {/* Subject type badge */}
        <span
          className={`text-[10px] px-1.5 py-0.5 rounded flex items-center gap-1 ${
            isActive
              ? "bg-[#1c1a18] text-[#c8c3bc]"  // dark warm bg + warm cream text
              : "bg-[#eae6de] text-[#6b6560]"
          }`}
        >
          {SUBJECT_ICONS[report.subject_type]}
          {SUBJECT_LABELS[report.subject_type]}
        </span>

        {/* Status */}
        <div className="flex items-center gap-1">
          <StatusIcon status={report.status} />
          <span
            className={`text-[11px] ${
              isActive
                ? report.status === "failed"
                  ? "text-red-300"
                  : running
                  ? "text-[#c8c3bc]"   // warm cream instead of blue-200
                  : "text-[#a8c8a8]"   // muted warm green instead of green-200
                : report.status === "failed"
                ? "text-red-500"
                : running
                ? "text-[#78716c]"     // warm neutral instead of blue-500
                : "text-[#4d9070]"     // warm muted green instead of emerald-600
            }`}
          >
            {running
              ? STATUS_RUNNING_LABELS[report.status] ?? "Running..."
              : report.status === "completed"
              ? report.quality_score != null
                ? `Score ${report.quality_score}`
                : "Done"
              : "Failed"}
          </span>
        </div>

        {/* Time */}
        <span className={`text-[11px] ml-auto ${isActive ? "text-[#a89e98]" : "text-[#a8a29e]"}`}>
          {timeAgo(report.created_at)}
        </span>
      </div>
    </button>
  );
}

interface HistorySidebarProps {
  reports: HistoryReport[];
  activeReportId: string | null;
  onSelectReport: (id: string) => void;
  onNewResearch: () => void;
}

export function HistorySidebar({
  reports,
  activeReportId,
  onSelectReport,
  onNewResearch,
}: HistorySidebarProps) {
  return (
    <aside className="w-60 shrink-0 bg-[#f0ede5] border-r border-[#ddd8cd] flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#ddd8cd] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-1.5">
          <History className="w-3.5 h-3.5 text-[#8c8278]" />
          <span className="text-[11px] text-[#6b6560] uppercase tracking-widest" style={{ fontWeight: 600, letterSpacing: "0.1em" }}>
            History
          </span>
        </div>
        <button
          onClick={onNewResearch}
          className="w-6 h-6 flex items-center justify-center rounded hover:bg-[#e2ddd4] transition-colors text-[#7a756e]"
          title="Clear selection / New research"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Report list */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
        {reports.length === 0 ? (
          <div className="px-3 py-6 text-center">
            <FileText className="w-8 h-8 text-[#c8c0b4] mx-auto mb-2" />
            <p className="text-[12px] text-[#a8a29e]">No reports yet</p>
            <p className="text-[11px] text-[#c8c0b4] mt-1">
              Enter a research topic above to get started
            </p>
          </div>
        ) : (
          reports.map((report) => (
            <HistoryItem
              key={report.report_id}
              report={report}
              isActive={report.report_id === activeReportId}
              onClick={() => onSelectReport(report.report_id)}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2.5 border-t border-[#ddd8cd] shrink-0 flex items-center gap-1.5">
        <FileText className="w-3 h-3 text-[#a8a29e]" />
        <p className="text-[11px] text-[#a8a29e]">
          {reports.length} report{reports.length !== 1 ? "s" : ""}
        </p>
      </div>
    </aside>
  );
}
