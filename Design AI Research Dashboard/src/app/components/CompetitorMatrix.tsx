import { CheckCircle2, XCircle, Minus } from "lucide-react";
import type { CompetitorMatrixItem } from "../data/types";

function EvidenceChip({ id }: { id: string }) {
  return (
    <span className="inline-flex items-center text-[10px] text-[#6b6560] bg-[#eae6de] border border-[#ddd8cd] rounded px-1.5 py-0.5 font-mono">
      {id}
    </span>
  );
}

interface CompetitorMatrixProps {
  competitors: CompetitorMatrixItem[];
}

export function CompetitorMatrix({ competitors }: CompetitorMatrixProps) {
  if (competitors.length === 0) {
    return (
      <div className="border border-[#ddd8cd] rounded-md px-6 py-8 text-center bg-white">
        <Minus className="w-6 h-6 text-[#c8c0b4] mx-auto mb-2" />
        <p className="text-[13px] text-[#a8a29e]">No competitor matrix available</p>
      </div>
    );
  }

  return (
    <div className="border border-[#ddd8cd] rounded-md overflow-hidden bg-white">
      <div className="overflow-x-auto">
        <table className="w-full text-[12px]">
          <thead>
            <tr className="border-b border-[#ddd8cd] bg-[#f5f2eb]">
              <th className="text-left px-4 py-2.5 text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600, width: "140px" }}>
                Competitor
              </th>
              <th className="text-left px-4 py-2.5 text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
                Role / Positioning
              </th>
              <th className="text-left px-4 py-2.5 text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
                Strengths
              </th>
              <th className="text-left px-4 py-2.5 text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
                Weaknesses
              </th>
              <th className="text-left px-4 py-2.5 text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
                Best For
              </th>
              <th className="text-left px-4 py-2.5 text-[11px] text-[#6b6560] uppercase tracking-wider" style={{ fontWeight: 600 }}>
                Pricing
              </th>
            </tr>
          </thead>
          <tbody>
            {competitors.map((comp, idx) => (
              <tr
                key={comp.competitor_id}
                className={`border-b border-[#ebe7de] ${idx % 2 === 0 ? "bg-white" : "bg-[#faf8f4]"} hover:bg-[#f5f2eb] transition-colors`}
              >
                <td className="px-4 py-3 align-top">
                  <div>
                    <span className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
                      {comp.name}
                    </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {comp.supporting_evidence_ids.slice(0, 2).map((id) => (
                        <EvidenceChip key={id} id={id} />
                      ))}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 align-top">
                  <p className="text-[12px] text-[#374151] leading-snug">{comp.role}</p>
                </td>
                <td className="px-4 py-3 align-top">
                  <ul className="space-y-1">
                    {comp.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-[12px] text-[#374151]">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500 mt-0.5 shrink-0" />
                        <span className="leading-snug">{s}</span>
                      </li>
                    ))}
                  </ul>
                </td>
                <td className="px-4 py-3 align-top">
                  <ul className="space-y-1">
                    {comp.weaknesses.map((w, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-[12px] text-[#374151]">
                        <XCircle className="w-3 h-3 text-red-400 mt-0.5 shrink-0" />
                        <span className="leading-snug">{w}</span>
                      </li>
                    ))}
                  </ul>
                </td>
                <td className="px-4 py-3 align-top">
                  <p className="text-[12px] text-[#374151] leading-snug">{comp.best_for}</p>
                </td>
                <td className="px-4 py-3 align-top">
                  {comp.pricing_or_access ? (
                    <p className="text-[12px] text-[#6b6560] font-mono leading-snug">
                      {comp.pricing_or_access}
                    </p>
                  ) : (
                    <span className="text-[#c8c0b4]">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}