import { useEffect, useState } from "react";
import { ResearchInputBar } from "./components/ResearchInputBar";
import { HistorySidebar } from "./components/HistorySidebar";
import { ReportWorkspace } from "./components/ReportWorkspace";
import { createReport, getDiagnosticsStatus, getReport, getReportStatus, listReports, runDiagnosticsValidation } from "./data/api";
import { mockReports } from "./data/mockData";
import type {
  DiagnosticsProviderStatus,
  DiagnosticsStatusResponse,
  DiagnosticsValidationResponse,
  HistoryReport,
  SubjectType,
  ReportStatus,
} from "./data/types";

function getActiveStatus(reports: HistoryReport[], activeId: string | null): ReportStatus | null {
  if (!activeId) return null;
  const r = reports.find((r) => r.report_id === activeId);
  return r?.status ?? null;
}

function isTerminalStatus(status: ReportStatus | null): boolean {
  return status === "completed" || status === "failed" || status === "empty";
}

function upsertReport(reports: HistoryReport[], report: HistoryReport): HistoryReport[] {
  const withoutReport = reports.filter((r) => r.report_id !== report.report_id);
  return [report, ...withoutReport];
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Unknown API error";
}

function labelForProvider(name: string): string {
  const labels: Record<string, string> = {
    tavily_search: "Tavily",
    firecrawl_scrape: "Firecrawl",
    llm: "LLM",
  };
  return labels[name] ?? name;
}

function DiagnosticsPill({ provider }: { provider: DiagnosticsProviderStatus }) {
  const isReal = provider.mode === "real";
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-stone-200 bg-white px-2 py-1">
      <span className="text-stone-500">{labelForProvider(provider.name)}</span>
      <span className={isReal ? "font-medium text-emerald-700" : "font-medium text-stone-600"}>
        {isReal ? "Real" : "Mock"}
      </span>
    </span>
  );
}

function validationSummary(result: DiagnosticsValidationResponse | null): string | null {
  if (!result) return null;
  const allResults = [...result.tools, ...(result.llm ? [result.llm] : [])];
  const passed = allResults.filter((item) => item.status === "passed").length;
  const skipped = allResults.filter((item) => item.status === "skipped").length;
  const failed = allResults.filter((item) => item.status === "failed").length;
  return `${passed} passed / ${skipped} skipped / ${failed} failed`;
}

export default function App() {
  const [reports, setReports] = useState<HistoryReport[]>(mockReports);
  const [activeReportId, setActiveReportId] = useState<string | null>(mockReports[0].report_id);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [diagnosticsStatus, setDiagnosticsStatus] = useState<DiagnosticsStatusResponse | null>(null);
  const [diagnosticsResult, setDiagnosticsResult] = useState<DiagnosticsValidationResponse | null>(null);
  const [diagnosticsError, setDiagnosticsError] = useState<string | null>(null);
  const [diagnosticsLoading, setDiagnosticsLoading] = useState(false);

  const activeReport = reports.find((r) => r.report_id === activeReportId) ?? null;
  const activeStatus = getActiveStatus(reports, activeReportId);

  useEffect(() => {
    let cancelled = false;

    async function loadDiagnostics() {
      try {
        const status = await getDiagnosticsStatus();
        if (cancelled) return;
        setDiagnosticsStatus(status);
        setDiagnosticsError(null);
      } catch (error) {
        if (cancelled) return;
        setDiagnosticsStatus(null);
        setDiagnosticsError(`Diagnostics unavailable: ${errorMessage(error)}`);
      }
    }

    loadDiagnostics();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadHistory() {
      try {
        const backendReports = await listReports();
        if (cancelled) return;
        setConnectionError(null);
        setReports(backendReports);
        setActiveReportId((currentId) => {
          if (currentId && backendReports.some((report) => report.report_id === currentId)) {
            return currentId;
          }
          return backendReports[0]?.report_id ?? null;
        });
      } catch (error) {
        if (cancelled) return;
        setConnectionError(`Backend unavailable: ${errorMessage(error)}. Showing prototype mock reports.`);
        setReports(mockReports);
        setActiveReportId(mockReports[0]?.report_id ?? null);
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!activeReport || activeReport.status !== "completed" || activeReport.report_data) return;

    let cancelled = false;

    async function loadReportDetail() {
      try {
        const detail = await getReport(activeReport.report_id);
        if (cancelled) return;
        setConnectionError(null);
        setReports((prev) => upsertReport(prev, detail.report));
      } catch (error) {
        if (cancelled) return;
        setConnectionError(`Could not load report detail: ${errorMessage(error)}`);
      }
    }

    loadReportDetail();

    return () => {
      cancelled = true;
    };
  }, [activeReport?.report_id, activeReport?.status, activeReport?.report_data]);

  useEffect(() => {
    if (!activeReport || isTerminalStatus(activeReport.status)) return;

    let cancelled = false;

    async function pollStatus() {
      try {
        const status = await getReportStatus(activeReport.report_id);
        if (cancelled) return;
        setConnectionError(null);
        setReports((prev) =>
          prev.map((report) =>
            report.report_id === status.report_id
              ? {
                  ...report,
                  status: status.status,
                  progress_message: status.progress_message,
                  progress_steps: status.progress_steps,
                  error_message: status.error_message,
                  updated_at: new Date().toISOString(),
                }
              : report
          )
        );

        if (status.status === "completed") {
          const detail = await getReport(status.report_id);
          if (!cancelled) {
            setReports((prev) => upsertReport(prev, detail.report));
          }
        }
      } catch (error) {
        if (cancelled) return;
        setConnectionError(`Lost backend connection while polling: ${errorMessage(error)}`);
      }
    }

    pollStatus();
    const intervalId = window.setInterval(pollStatus, 2000);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
    };
  }, [activeReport?.report_id, activeReport?.status]);

  async function handleSubmit(topic: string, subjectType: SubjectType, forceRefresh: boolean) {
    try {
      setConnectionError(null);
      const detail = await createReport({ topic, subjectType, forceRefresh });
      setReports((prev) => upsertReport(prev, detail.report));
      setActiveReportId(detail.report.report_id);
    } catch (error) {
      setConnectionError(`Could not create report: ${errorMessage(error)}`);
    }
  }

  async function handleRunDiagnostics() {
    try {
      setDiagnosticsLoading(true);
      setDiagnosticsError(null);
      const result = await runDiagnosticsValidation();
      setDiagnosticsResult(result);
    } catch (error) {
      setDiagnosticsError(`Could not run diagnostics: ${errorMessage(error)}`);
    } finally {
      setDiagnosticsLoading(false);
    }
  }

  function handleRetry() {
    if (!activeReport) return;
    handleSubmit(activeReport.topic, activeReport.subject_type, true);
  }

  function handleNewResearch() {
    setActiveReportId(null);
  }

  return (
    <div className="h-screen w-full bg-[#f5f2eb] flex flex-col overflow-hidden" style={{ minWidth: "1200px" }}>
      <ResearchInputBar activeStatus={activeStatus} onSubmit={handleSubmit} />

      {connectionError && (
        <div className="px-5 py-2 bg-amber-50 border-b border-amber-200 text-[12px] text-amber-800 shrink-0">
          {connectionError}
        </div>
      )}

      {(diagnosticsStatus || diagnosticsError) && (
        <div className="px-5 py-2 bg-stone-50 border-b border-stone-200 text-[12px] text-stone-700 shrink-0 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-stone-900">Runtime</span>
            {diagnosticsStatus?.tools.map((tool) => <DiagnosticsPill key={tool.name} provider={tool} />)}
            {diagnosticsStatus && <DiagnosticsPill provider={diagnosticsStatus.llm} />}
            {diagnosticsStatus?.llm.details.provider && (
              <span className="text-stone-500">
                {String(diagnosticsStatus.llm.details.provider)} / {String(diagnosticsStatus.llm.details.model ?? "unknown")}
              </span>
            )}
            {diagnosticsError && <span className="text-amber-700">{diagnosticsError}</span>}
            {validationSummary(diagnosticsResult) && (
              <span className="text-stone-500">Last validation: {validationSummary(diagnosticsResult)}</span>
            )}
          </div>
          {diagnosticsStatus && (
            <button
              type="button"
              onClick={handleRunDiagnostics}
              disabled={diagnosticsLoading}
              className="rounded-full border border-stone-300 bg-white px-3 py-1 text-[12px] font-medium text-stone-700 disabled:opacity-60"
            >
              {diagnosticsLoading ? "Running..." : "Run live diagnostics"}
            </button>
          )}
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        <HistorySidebar
          reports={reports}
          activeReportId={activeReportId}
          onSelectReport={setActiveReportId}
          onNewResearch={handleNewResearch}
        />

        <main className="flex-1 bg-[#f5f2eb] flex flex-col overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden bg-white border-t-0">
            <ReportWorkspace report={activeReport} onRetry={handleRetry} />
          </div>
        </main>
      </div>
    </div>
  );
}
