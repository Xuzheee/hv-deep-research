import {
  Target, Shield, TrendingDown, Zap, AlertCircle,
  Star, BarChart3, Globe2, Table2, Lightbulb,
} from "lucide-react";
import type { HorizontalTabData, CapabilityBoundary, Recommendation } from "../../data/types";
import { CompetitorMatrix } from "../CompetitorMatrix";

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

const BOUNDARY_CONFIG: Record<
  CapabilityBoundary["boundary_type"],
  { label: string; icon: React.ReactNode; style: string }
> = {
  // Warm-muted blue — was saturated blue-50/blue-200/blue-600
  short_term_feature: {
    label: "Short-term Feature",
    icon: <Zap className="w-3.5 h-3.5" />,
    style: "text-[#3a5880] bg-[#e8edf5] border-[#bfceea]",
  },
  // Warm-muted green — was saturated emerald-50/emerald-200/emerald-600
  long_term_moat: {
    label: "Long-term Moat",
    icon: <Shield className="w-3.5 h-3.5" />,
    style: "text-[#3a6048] bg-[#e8f0e8] border-[#b0ceb8]",
  },
  // Keep semantic red for weaknesses
  current_weakness: {
    label: "Current Weakness",
    icon: <TrendingDown className="w-3.5 h-3.5" />,
    style: "text-red-700 bg-red-50 border-red-200",
  },
  // Keep semantic amber for threats
  emerging_threat: {
    label: "Emerging Threat",
    icon: <AlertCircle className="w-3.5 h-3.5" />,
    style: "text-amber-700 bg-amber-50 border-amber-200",
  },
};

const PRIORITY_STYLES: Record<Recommendation["priority"], string> = {
  high:   "text-red-700 bg-red-50 border-red-200",
  medium: "text-amber-700 bg-amber-50 border-amber-200",
  // Warm neutral instead of cool slate-50/slate-200/slate-600
  low:    "text-[#78716c] bg-[#eae6de] border-[#ddd8cd]",
};

const SCENARIO_LABELS: Record<HorizontalTabData["competitor_scenario"], string> = {
  no_direct_competitor: "No direct competitors",
  few_competitors:      "Few competitors",
  mature_market:        "Mature market",
};

// Warm-muted scenario tags — was bg-blue-50 / bg-purple-50
const SCENARIO_STYLES: Record<HorizontalTabData["competitor_scenario"], string> = {
  no_direct_competitor: "text-[#3a5880] bg-[#e8edf5]",
  few_competitors:      "text-[#5a4888] bg-[#ede8f5]",
  mature_market:        "text-[#57534e] bg-[#eae6de]",
};

interface HorizontalAnalysisTabProps {
  data: HorizontalTabData;
}

export function HorizontalAnalysisTab({ data }: HorizontalAnalysisTabProps) {
  const hasContent = data.competitor_matrix.length > 0 || data.positioning_summary;

  if (!hasContent) {
    return (
      <div className="flex items-center justify-center py-16 text-center">
        <div>
          <BarChart3 className="w-8 h-8 text-[#c8c0b4] mx-auto mb-2" />
          <p className="text-[13px] text-[#a8a29e]">Horizontal analysis not available</p>
          <p className="text-[12px] text-[#c8c0b4] mt-1">Insufficient evidence for competitive analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Positioning Summary */}
      {data.positioning_summary && (
        <section>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex items-center gap-1.5">
              <span className="text-[#a8a29e]"><Target className="w-3.5 h-3.5" /></span>
              <h3 className="text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
                Positioning Summary
              </h3>
            </div>
            {data.competitor_scenario && (
              <span
                className={`text-[10px] px-2 py-0.5 rounded ${SCENARIO_STYLES[data.competitor_scenario]}`}
                style={{ fontWeight: 500 }}
              >
                {SCENARIO_LABELS[data.competitor_scenario]}
              </span>
            )}
          </div>
          <div className="bg-white border border-[#ddd8cd] border-l-4 border-l-[#292524] rounded-md px-5 py-4">
            <div className="flex items-start gap-2">
              <Target className="w-4 h-4 text-[#292524] shrink-0 mt-0.5" />
              <p className="text-[13px] text-[#44403c] leading-relaxed">{data.positioning_summary}</p>
            </div>
          </div>
        </section>
      )}

      {/* Narrative */}
      {data.full_text && (
        <section>
          <SectionHeader icon={<Globe2 className="w-3.5 h-3.5" />} title="Competitive Landscape Narrative" />
          <div className="bg-white border border-[#ddd8cd] rounded-md px-5 py-4">
            <p className="text-[13px] text-[#44403c] leading-relaxed whitespace-pre-line">
              {data.full_text}
            </p>
          </div>
        </section>
      )}

      {/* Competitor Matrix */}
      {data.competitor_matrix.length > 0 && (
        <section>
          <SectionHeader icon={<Table2 className="w-3.5 h-3.5" />} title="Competitor Comparison Matrix" />
          <CompetitorMatrix competitors={data.competitor_matrix} />
        </section>
      )}

      {/* Capability Boundaries */}
      {data.capability_boundaries.length > 0 && (
        <section>
          <SectionHeader icon={<Shield className="w-3.5 h-3.5" />} title="Capability Boundaries" />
          <div className="grid grid-cols-2 gap-3">
            {data.capability_boundaries.map((boundary) => {
              const config = BOUNDARY_CONFIG[boundary.boundary_type];
              return (
                <div
                  key={boundary.boundary_id}
                  className={`border rounded-md px-4 py-3 ${config.style}`}
                >
                  <div className="flex items-center gap-2 mb-1.5">
                    {config.icon}
                    <span className="text-[12px]" style={{ fontWeight: 600 }}>
                      {config.label}
                    </span>
                  </div>
                  <p className="text-[13px] mb-1" style={{ fontWeight: 500 }}>
                    {boundary.title}
                  </p>
                  <p className="text-[12px] opacity-80 leading-snug">{boundary.description}</p>
                  {boundary.supporting_evidence_ids.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {boundary.supporting_evidence_ids.map((id) => (
                        <EvidenceChip key={id} id={id} />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Recommendations */}
      {data.recommendations.length > 0 && (
        <section>
          <SectionHeader icon={<Lightbulb className="w-3.5 h-3.5" />} title="Recommendations" />
          <div className="space-y-2">
            {data.recommendations.map((rec) => (
              <div
                key={rec.rec_id}
                className="bg-white border border-[#ddd8cd] rounded-md px-4 py-3"
              >
                <div className="flex items-start gap-3">
                  <Star className="w-3.5 h-3.5 text-[#a8a29e] mt-0.5 shrink-0" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
                        {rec.title}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded border ${PRIORITY_STYLES[rec.priority]}`}
                        style={{ fontWeight: 500 }}
                      >
                        {rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1)} priority
                      </span>
                      {rec.target_audience && (
                        <span className="text-[10px] text-[#7a756e] bg-[#eae6de] px-1.5 py-0.5 rounded border border-[#ddd8cd]">
                          For: {rec.target_audience}
                        </span>
                      )}
                    </div>
                    <p className="text-[13px] text-[#44403c] leading-relaxed mb-1.5">{rec.content}</p>
                    <p className="text-[12px] text-[#78716c] italic">{rec.rationale}</p>
                    {rec.supporting_evidence_ids.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {rec.supporting_evidence_ids.map((id) => (
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