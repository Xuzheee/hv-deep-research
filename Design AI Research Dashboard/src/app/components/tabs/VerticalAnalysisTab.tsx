import { GitBranch, Milestone, ArrowRight, Layers, ScrollText, Flag, Network } from "lucide-react";
import type { VerticalTabData } from "../../data/types";

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

// Warm-muted stage accent colors — replace saturated Tailwind color classes
const STAGE_COLORS = [
  "border-l-[#5b7fa6]",  // muted slate-blue   (was blue-400)
  "border-l-[#8b7ab0]",  // muted mauve        (was purple-400)
  "border-l-[#4d9070]",  // muted sage-green   (was emerald-400)
  "border-l-[#b07a48]",  // muted amber        (was orange-400)
  "border-l-[#a85870]",  // muted rose         (was rose-400)
];

interface VerticalAnalysisTabProps {
  data: VerticalTabData;
}

export function VerticalAnalysisTab({ data }: VerticalAnalysisTabProps) {
  const hasContent = data.stages.length > 0 || data.full_text || data.key_turning_points.length > 0;

  if (!hasContent) {
    return (
      <div className="flex items-center justify-center py-16 text-center">
        <div>
          <Layers className="w-8 h-8 text-[#c8c0b4] mx-auto mb-2" />
          <p className="text-[13px] text-[#a8a29e]">Vertical analysis not available</p>
          <p className="text-[12px] text-[#c8c0b4] mt-1">
            Insufficient evidence was collected for historical analysis
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Historical Narrative */}
      {data.full_text && (
        <section>
          <SectionHeader icon={<ScrollText className="w-3.5 h-3.5" />} title="Historical Narrative" />
          <div className="bg-white border border-[#ddd8cd] rounded-md px-5 py-4">
            <p className="text-[13px] text-[#44403c] leading-relaxed whitespace-pre-line">
              {data.full_text}
            </p>
          </div>
        </section>
      )}

      {/* Stage Cards */}
      {data.stages.length > 0 && (
        <section>
          <SectionHeader icon={<Layers className="w-3.5 h-3.5" />} title="Evolution Stages" />
          <div className="space-y-3">
            {data.stages.map((stage) => (
              <div
                key={stage.stage_id}
                className={`bg-white border border-[#ddd8cd] border-l-4 ${
                  STAGE_COLORS[(stage.stage_number - 1) % STAGE_COLORS.length]
                } rounded-md px-5 py-4`}
              >
                {/* Stage header */}
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-6 h-6 rounded-full bg-[#eae6de] border border-[#ddd8cd] flex items-center justify-center shrink-0 mt-0.5">
                    <span className="text-[11px] text-[#6b6560]" style={{ fontWeight: 600 }}>
                      {stage.stage_number}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-0.5">
                      <span className="text-[14px] text-[#1e293b]" style={{ fontWeight: 500 }}>
                        {stage.title}
                      </span>
                      {stage.period && (
                        <span className="text-[11px] text-[#a8a29e] bg-[#f5f2eb] border border-[#ddd8cd] px-2 py-0.5 rounded font-mono">
                          {stage.period}
                        </span>
                      )}
                    </div>
                    <p className="text-[13px] text-[#78716c] leading-snug">{stage.summary}</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 ml-9">
                  {/* Key Events */}
                  <div>
                    <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1.5" style={{ fontWeight: 600 }}>
                      Key Events
                    </p>
                    <ul className="space-y-1">
                      {stage.key_events.map((event, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-[12px] text-[#44403c]">
                          {/* Warm muted milestone dot */}
                          <Milestone className="w-3 h-3 text-[#a8a29e] mt-0.5 shrink-0" />
                          <span className="leading-snug">{event}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Driving Forces */}
                  <div>
                    <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1.5" style={{ fontWeight: 600 }}>
                      Driving Forces
                    </p>
                    <ul className="space-y-1">
                      {stage.driving_forces.map((force, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-[12px] text-[#44403c]">
                          {/* Warm muted arrow — was blue-400 */}
                          <ArrowRight className="w-3 h-3 text-[#5b7fa6] mt-0.5 shrink-0" />
                          <span className="leading-snug">{force}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Path Dependencies */}
                  {stage.path_dependencies.length > 0 && (
                    <div>
                      <p className="text-[11px] text-[#a8a29e] uppercase tracking-wider mb-1.5" style={{ fontWeight: 600 }}>
                        Path Dependencies
                      </p>
                      <ul className="space-y-1">
                        {stage.path_dependencies.map((dep, i) => (
                          <li key={i} className="flex items-start gap-1.5 text-[12px] text-[#44403c]">
                            {/* Warm muted branch — was purple-400 */}
                            <GitBranch className="w-3 h-3 text-[#8b7ab0] mt-0.5 shrink-0" />
                            <span className="leading-snug">{dep}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Evidence IDs */}
                {stage.supporting_evidence_ids.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3 ml-9">
                    {stage.supporting_evidence_ids.map((id) => (
                      <EvidenceChip key={id} id={id} />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Key Turning Points */}
      {data.key_turning_points.length > 0 && (
        <section>
          <SectionHeader icon={<Flag className="w-3.5 h-3.5" />} title="Key Turning Points" />
          <div className="bg-white border border-[#ddd8cd] rounded-md overflow-hidden">
            {data.key_turning_points.map((point, idx) => (
              <div
                key={idx}
                className={`px-4 py-3 flex items-start gap-3 ${
                  idx < data.key_turning_points.length - 1 ? "border-b border-[#ebe7de]" : ""
                }`}
              >
                <div className="w-5 h-5 rounded-full bg-[#292524] flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-[9px] text-[#e8e4da]" style={{ fontWeight: 600 }}>
                    {idx + 1}
                  </span>
                </div>
                <p className="text-[13px] text-[#44403c] leading-snug">{point}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Path Dependency Summary */}
      {data.path_dependency_summary && (
        <section>
          <SectionHeader icon={<Network className="w-3.5 h-3.5" />} title="Path Dependency Summary" />
          {/* Was border-l-purple-300 — now warm muted mauve */}
          <div className="bg-white border border-[#ddd8cd] rounded-md px-5 py-4 border-l-4 border-l-[#9b8ab8]">
            <p className="text-[13px] text-[#44403c] leading-relaxed">
              {data.path_dependency_summary}
            </p>
          </div>
        </section>
      )}
    </div>
  );
}