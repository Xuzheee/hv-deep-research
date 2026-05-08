import {
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  ShieldAlert,
  BookOpen,
  Lightbulb,
  CalendarDays,
  Database,
} from "lucide-react";
import type { OverviewTabData } from "../../data/types";
import { EvidenceGroupCard } from "../EvidenceGroupCard";
import { QualityWarningBanner } from "../QualityWarningBanner";

function EvidenceChip({ id }: { id: string }) {
  return (
    <span className="inline-flex items-center text-[10px] text-[#6b6560] bg-[#eae6de] border border-[#ddd8cd] rounded px-1.5 py-0.5 font-mono cursor-default hover:bg-[#ddd8cd] transition-colors">
      {id}
    </span>
  );
}

function SectionHeader({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-1.5 mb-2">
      <span className="text-[#a8a29e]">{icon}</span>
      <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
        {title}
      </h3>
    </div>
  );
}

// Warm-muted confidence — high uses warm green instead of cool emerald-50
const CONFIDENCE_STYLES = {
  high: "text-[#3a6048] bg-[#e8f0e8] border-[#b0ceb8]",
  medium: "text-amber-700 bg-amber-50 border-amber-200",
  low: "text-red-700 bg-red-50 border-red-200",
};

const UPDATE_TYPE_LABELS: Record<string, string> = {
  product_launch: "Launch",
  feature_update: "Feature",
  pricing_change: "Pricing",
  partnership: "Partnership",
  policy_change: "Policy",
  other: "Update",
};

// Warm-muted category pills — no saturated rainbow
const UPDATE_TYPE_STYLES: Record<string, string> = {
  product_launch:  "bg-[#e8edf5] text-[#3a5880]",
  feature_update:  "bg-[#ede8f5] text-[#5a4888]",
  pricing_change:  "bg-[#e8f0e8] text-[#3a6048]",
  partnership:     "bg-[#e8ebf5] text-[#384878]",
  policy_change:   "bg-[#f5ede6] text-[#7a4828]",
  other:           "bg-[#eae6de] text-[#6b6560]",
};

// Keep red/amber/yellow for risk — these are semantic
const SEVERITY_STYLES = {
  high:   "border-red-200 bg-red-50",
  medium: "border-amber-200 bg-amber-50",
  low:    "border-yellow-200 bg-yellow-50",
};

const SEVERITY_ICON_COLOR = {
  high:   "text-red-500",
  medium: "text-amber-500",
  low:    "text-yellow-500",
};

interface OverviewTabProps {
  data: OverviewTabData;
  qualityWarning: boolean;
  qualityIssues: string[];
  qualityScore: number;
}

export function OverviewTab({ data, qualityWarning, qualityIssues, qualityScore }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Quality Warning */}
      {qualityWarning && (
        <QualityWarningBanner issues={qualityIssues} score={qualityScore} />
      )}

      {/* Product Overview */}
      <section>
        <SectionHeader icon={<BookOpen className="w-3.5 h-3.5" />} title="Product Overview" />
        <div className="bg-white border border-[#ddd8cd] rounded-md px-4 py-4">
          <p className="text-[13px] text-[#44403c] leading-relaxed">{data.product_overview}</p>
        </div>
      </section>

      <div className="grid grid-cols-2 gap-6">
        {/* Key Findings */}
        <section>
          <SectionHeader icon={<Lightbulb className="w-3.5 h-3.5" />} title="Key Findings" />
          <div className="space-y-2">
            {data.key_findings.map((finding) => (
              <div
                key={finding.finding_id}
                className="bg-white border border-[#ddd8cd] rounded-md px-4 py-3 hover:border-[#ccc7bc] transition-colors"
              >
                <div className="flex items-start gap-2 mb-1">
                  <ChevronRight className="w-3.5 h-3.5 text-[#a8a29e] mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
                        {finding.title}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded border ${CONFIDENCE_STYLES[finding.confidence]}`}
                      >
                        {finding.confidence.charAt(0).toUpperCase() + finding.confidence.slice(1)}
                      </span>
                    </div>
                    <p className="text-[12px] text-[#78716c] leading-relaxed">{finding.content}</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {finding.supporting_evidence_ids.map((id) => (
                        <EvidenceChip key={id} id={id} />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Release Updates */}
        <section>
          <SectionHeader icon={<CalendarDays className="w-3.5 h-3.5" />} title="Release Updates" />
          <div className="bg-white border border-[#ddd8cd] rounded-md overflow-hidden">
            {data.release_updates.map((update, idx) => (
              <div
                key={update.update_id}
                className={`px-4 py-3 ${idx < data.release_updates.length - 1 ? "border-b border-[#ebe7de]" : ""}`}
              >
                <div className="flex items-start gap-3">
                  {/* Date column */}
                  <div className="w-20 shrink-0">
                    <span className="text-[11px] text-[#a8a29e] font-mono">
                      {update.date
                        ? new Date(update.date).toLocaleDateString("en-US", {
                            month: "short",
                            year: "numeric",
                          })
                        : "—"}
                    </span>
                  </div>
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                      <span className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
                        {update.title}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded ${UPDATE_TYPE_STYLES[update.update_type] ?? "bg-[#eae6de] text-[#6b6560]"}`}
                      >
                        {UPDATE_TYPE_LABELS[update.update_type] ?? "Update"}
                      </span>
                      {update.source_url && (
                        <a
                          href={update.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-auto text-[#a8a29e] hover:text-[#6b6560] transition-colors"
                          title="Source"
                        >
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                    <p className="text-[12px] text-[#78716c] leading-snug">{update.content}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Evidence Groups */}
      <section>
        <SectionHeader icon={<Database className="w-3.5 h-3.5" />} title="Evidence Groups" />
        <div className="grid grid-cols-2 gap-3">
          {data.evidence_groups.map((group) => (
            <EvidenceGroupCard key={group.group_id} group={group} />
          ))}
        </div>
      </section>

      {/* Risk Notes */}
      {data.risk_notes.length > 0 && (
        <section>
          <SectionHeader icon={<ShieldAlert className="w-3.5 h-3.5" />} title="Risk Notes" />
          <div className="space-y-2">
            {data.risk_notes.map((risk) => (
              <div
                key={risk.risk_id}
                className={`border rounded-md px-4 py-3 ${SEVERITY_STYLES[risk.severity]}`}
              >
                <div className="flex items-start gap-2">
                  <ShieldAlert
                    className={`w-4 h-4 mt-0.5 shrink-0 ${SEVERITY_ICON_COLOR[risk.severity]}`}
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
                        {risk.title}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded ${
                          risk.severity === "high"
                            ? "bg-red-100 text-red-700"
                            : risk.severity === "medium"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-yellow-100 text-yellow-700"
                        }`}
                        style={{ fontWeight: 500 }}
                      >
                        {risk.severity.charAt(0).toUpperCase() + risk.severity.slice(1)} risk
                      </span>
                    </div>
                    <p className="text-[12px] text-[#44403c] leading-relaxed">{risk.content}</p>
                    {risk.supporting_evidence_ids.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {risk.supporting_evidence_ids.map((id) => (
                          <EvidenceChip key={id} id={id} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
