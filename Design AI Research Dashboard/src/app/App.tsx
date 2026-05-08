import { useState } from "react";
import { ResearchInputBar } from "./components/ResearchInputBar";
import { HistorySidebar } from "./components/HistorySidebar";
import { ReportWorkspace } from "./components/ReportWorkspace";
import { mockReports } from "./data/mockData";
import type { HistoryReport, SubjectType, ReportStatus } from "./data/types";

function getActiveStatus(reports: HistoryReport[], activeId: string | null): ReportStatus | null {
  if (!activeId) return null;
  const r = reports.find((r) => r.report_id === activeId);
  return r?.status ?? null;
}

export default function App() {
  const [reports, setReports] = useState<HistoryReport[]>(mockReports);
  const [activeReportId, setActiveReportId] = useState<string | null>(
    // Default to the first completed report for demo purposes
    mockReports[0].report_id
  );

  const activeReport = reports.find((r) => r.report_id === activeReportId) ?? null;
  const activeStatus = getActiveStatus(reports, activeReportId);

  function handleSubmit(topic: string, subjectType: SubjectType, _forceRefresh: boolean) {
    const newId = `rpt_${Date.now()}_${topic.toLowerCase().replace(/\s+/g, "_").slice(0, 12)}`;

    const newReport: HistoryReport = {
      report_id: newId,
      topic,
      subject_type: subjectType,
      status: "searching",
      quality_warning: false,
      quality_score: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      error_message: null,
      report_data: null,
      progress_steps: [
        { step_id: "ps_01", label: "Initializing research run", status: "completed", timestamp: new Date().toLocaleTimeString("en-US", { hour12: false }) },
        { step_id: "ps_02", label: "Planning research questions", status: "completed", timestamp: new Date().toLocaleTimeString("en-US", { hour12: false }) },
        { step_id: "ps_03", label: "Collecting information (0/12 tool calls)", status: "running", message: `Searching for "${topic}"...` },
        { step_id: "ps_04", label: "Filtering evidence cards", status: "pending" },
        { step_id: "ps_05", label: "Running vertical analysis", status: "pending" },
        { step_id: "ps_06", label: "Running horizontal analysis", status: "pending" },
        { step_id: "ps_07", label: "Synthesizing report data", status: "pending" },
        { step_id: "ps_08", label: "Quality check", status: "pending" },
        { step_id: "ps_09", label: "Saving report artifacts", status: "pending" },
      ],
      progress_message: `Searching web for information on "${topic}"...`,
    };

    setReports((prev) => [newReport, ...prev]);
    setActiveReportId(newId);
  }

  function handleRetry() {
    if (!activeReport) return;
    const updatedReport: HistoryReport = {
      ...activeReport,
      status: "searching",
      error_message: null,
      updated_at: new Date().toISOString(),
      progress_steps: activeReport.progress_steps.map((s) =>
        s.status === "failed" ? { ...s, status: "pending" as const } : s
      ),
      progress_message: `Retrying research for "${activeReport.topic}"...`,
    };
    setReports((prev) =>
      prev.map((r) => (r.report_id === activeReport.report_id ? updatedReport : r))
    );
  }

  function handleNewResearch() {
    setActiveReportId(null);
  }

  return (
    <div className="h-screen w-full bg-[#f5f2eb] flex flex-col overflow-hidden" style={{ minWidth: "1200px" }}>
      {/* Top Input Bar */}
      <ResearchInputBar activeStatus={activeStatus} onSubmit={handleSubmit} />

      {/* Main Layout: Sidebar + Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* History Sidebar */}
        <HistorySidebar
          reports={reports}
          activeReportId={activeReportId}
          onSelectReport={setActiveReportId}
          onNewResearch={handleNewResearch}
        />

        {/* Report Workspace */}
        <main className="flex-1 bg-[#f5f2eb] flex flex-col overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden bg-white border-t-0">
            <ReportWorkspace report={activeReport} onRetry={handleRetry} />
          </div>
        </main>
      </div>
    </div>
  );
}