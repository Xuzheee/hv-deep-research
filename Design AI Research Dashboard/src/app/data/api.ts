import type { DiagnosticsStatusResponse, DiagnosticsValidationResponse, HistoryReport, SubjectType } from "./types";

const DEFAULT_API_BASE_URL = "";
const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? DEFAULT_API_BASE_URL;

interface ReportDetailResponse {
  report: HistoryReport;
}

interface ReportStatusResponse {
  report_id: string;
  status: HistoryReport["status"];
  progress_message: string;
  progress_steps: HistoryReport["progress_steps"];
  error_message: string | null;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export function createReport(input: {
  topic: string;
  subjectType: SubjectType;
  forceRefresh: boolean;
}): Promise<ReportDetailResponse> {
  return requestJson<ReportDetailResponse>("/api/reports", {
    method: "POST",
    body: JSON.stringify({
      topic: input.topic,
      subject_type: input.subjectType,
      force_refresh: input.forceRefresh,
    }),
  });
}

export function listReports(): Promise<HistoryReport[]> {
  return requestJson<HistoryReport[]>("/api/reports");
}

export function getReport(reportId: string): Promise<ReportDetailResponse> {
  return requestJson<ReportDetailResponse>(`/api/reports/${reportId}`);
}

export function getReportStatus(reportId: string): Promise<ReportStatusResponse> {
  return requestJson<ReportStatusResponse>(`/api/reports/${reportId}/status`);
}

export function getDiagnosticsStatus(): Promise<DiagnosticsStatusResponse> {
  return requestJson<DiagnosticsStatusResponse>("/api/diagnostics/status");
}

export function runDiagnosticsValidation(): Promise<DiagnosticsValidationResponse> {
  return requestJson<DiagnosticsValidationResponse>("/api/diagnostics/validate", { method: "POST" });
}
