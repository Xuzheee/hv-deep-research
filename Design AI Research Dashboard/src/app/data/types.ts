export type SubjectType = "product" | "company" | "concept" | "person" | "technology" | "other";

export type ReportStatus =
  | "empty"
  | "pending"
  | "planning"
  | "searching"
  | "scraping"
  | "filtering"
  | "analyzing_vertical"
  | "analyzing_horizontal"
  | "synthesizing"
  | "quality_checking"
  | "persisting"
  | "completed"
  | "failed";

export type ConfidenceLevel = "high" | "medium" | "low";
export type SourceTier = "tier_1_primary" | "tier_2_authoritative_secondary" | "tier_3_community_signal" | "unknown";
export type BoundaryType = "short_term_feature" | "long_term_moat" | "current_weakness" | "emerging_threat";
export type UpdateType = "product_launch" | "feature_update" | "pricing_change" | "partnership" | "policy_change" | "other";
export type Priority = "high" | "medium" | "low";

export interface EvidenceGroup {
  group_id: string;
  label: string;
  description: string;
  source_count: number;
  evidence_count: number;
  dominant_tier: SourceTier;
  confidence: ConfidenceLevel;
  evidence_ids: string[];
}

export interface KeyFinding {
  finding_id: string;
  title: string;
  content: string;
  confidence: ConfidenceLevel;
  supporting_evidence_ids: string[];
}

export interface ReleaseUpdate {
  update_id: string;
  date: string | null;
  title: string;
  content: string;
  update_type: UpdateType;
  source_url: string | null;
  confidence: ConfidenceLevel;
}

export interface RiskNote {
  risk_id: string;
  title: string;
  content: string;
  severity: "high" | "medium" | "low";
  supporting_evidence_ids: string[];
}

export interface VerticalStage {
  stage_id: string;
  stage_number: number;
  title: string;
  period: string | null;
  summary: string;
  key_events: string[];
  driving_forces: string[];
  path_dependencies: string[];
  supporting_evidence_ids: string[];
}

export interface CompetitorMatrixItem {
  competitor_id: string;
  name: string;
  role: string;
  strengths: string[];
  weaknesses: string[];
  best_for: string;
  pricing_or_access: string | null;
  supporting_evidence_ids: string[];
}

export interface CapabilityBoundary {
  boundary_id: string;
  title: string;
  description: string;
  boundary_type: BoundaryType;
  supporting_evidence_ids: string[];
}

export interface Recommendation {
  rec_id: string;
  title: string;
  content: string;
  priority: Priority;
  target_audience: string | null;
  rationale: string;
  supporting_evidence_ids: string[];
}

export interface OverviewTabData {
  product_overview: string;
  release_updates: ReleaseUpdate[];
  key_findings: KeyFinding[];
  evidence_groups: EvidenceGroup[];
  risk_notes: RiskNote[];
}

export interface VerticalTabData {
  full_text: string;
  stages: VerticalStage[];
  key_turning_points: string[];
  path_dependency_summary: string;
}

export interface HorizontalTabData {
  full_text: string;
  competitor_scenario: "no_direct_competitor" | "few_competitors" | "mature_market";
  competitor_matrix: CompetitorMatrixItem[];
  capability_boundaries: CapabilityBoundary[];
  positioning_summary: string;
  recommendations: Recommendation[];
}

export interface ReportData {
  report_id: string;
  topic: string;
  subject: string;
  subject_type: SubjectType;
  title: string;
  subtitle: string | null;
  overview: OverviewTabData;
  vertical: VerticalTabData;
  horizontal: HorizontalTabData;
  quality_warning: boolean;
  quality_issues: string[];
  quality_score: number;
  source_count: number;
  evidence_count: number;
  generated_at: string;
  limitations: string[];
}

export interface ProgressStep {
  step_id: string;
  label: string;
  status: "pending" | "running" | "completed" | "failed";
  message?: string;
  timestamp?: string;
}

export interface HistoryReport {
  report_id: string;
  topic: string;
  subject_type: SubjectType;
  status: ReportStatus;
  quality_warning: boolean;
  quality_score: number | null;
  created_at: string;
  updated_at: string;
  error_message: string | null;
  report_data: ReportData | null;
  progress_steps: ProgressStep[];
  progress_message: string;
}
