import { useEffect, useState } from "react";
import { ResearchInputBar } from "./components/ResearchInputBar";
import { HistorySidebar } from "./components/HistorySidebar";
import { ReportWorkspace } from "./components/ReportWorkspace";
import { createReport, getReport, getReportStatus, listReports } from "./data/api";
import { mockReports } from "./data/mockData";
import type { HistoryReport, SubjectType, ReportStatus } from "./data/types";

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

export default function App() {
  const [reports, setReports] = useState<HistoryReport[]>(mockReports);
  const [activeReportId, setActiveReportId] = useState<string | null>(mockReports[0].report_id);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const activeReport = reports.find((r) => r.report_id === activeReportId) ?? null;
  const activeStatus = getActiveStatus(reports, activeReportId);

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
