import { Database, ExternalLink } from "lucide-react";
import type { EvidenceGroup } from "../data/types";

const TIER_LABELS: Record<EvidenceGroup["dominant_tier"], string> = {
  tier_1_primary: "Tier 1 · Primary",
  tier_2_authoritative_secondary: "Tier 2 · Authoritative",
  tier_3_community_signal: "Tier 3 · Community",
  unknown: "Unknown",
};

// Warm-muted tier badge colors — no cool slate/gray
const TIER_COLORS: Record<EvidenceGroup["dominant_tier"], string> = {
  tier_1_primary: "bg-[#e8edf5] text-[#3a5880] border-[#bfceea]",
  tier_2_authoritative_secondary: "bg-[#ede8f5] text-[#5a4888] border-[#c8bfe0]",
  tier_3_community_signal: "bg-[#f5f2eb] text-[#78716c] border-[#ddd8cd]",
  unknown: "bg-[#eae6de] text-[#a8a29e] border-[#ddd8cd]",
};

// Warm-muted confidence badge colors
const CONFIDENCE_COLORS: Record<EvidenceGroup["confidence"], string> = {
  high: "text-[#3a6048] bg-[#e8f0e8]",
  medium: "text-amber-700 bg-amber-50",
  low: "text-red-600 bg-red-50",
};

interface EvidenceGroupCardProps {
  group: EvidenceGroup;
}

export function EvidenceGroupCard({ group }: EvidenceGroupCardProps) {
  return (
    <div className="border border-[#ddd8cd] rounded-md px-4 py-3 bg-white hover:border-[#ccc7bc] transition-colors">
      <div className="flex items-start gap-3">
        <Database className="w-3.5 h-3.5 text-[#a8a29e] mt-0.5 shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="text-[13px] text-[#1e293b]" style={{ fontWeight: 500 }}>
              {group.label}
            </span>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded border ${TIER_COLORS[group.dominant_tier]}`}
            >
              {TIER_LABELS[group.dominant_tier]}
            </span>
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded ${CONFIDENCE_COLORS[group.confidence]}`}
              style={{ fontWeight: 500 }}
            >
              {group.confidence.charAt(0).toUpperCase() + group.confidence.slice(1)} confidence
            </span>
          </div>
          <p className="text-[12px] text-[#78716c] mb-2">{group.description}</p>
          <div className="flex items-center gap-3 text-[12px] text-[#a8a29e]">
            <span>
              <span className="text-[#44403c]" style={{ fontWeight: 500 }}>
                {group.source_count}
              </span>{" "}
              sources
            </span>
            <span>·</span>
            <span>
              <span className="text-[#44403c]" style={{ fontWeight: 500 }}>
                {group.evidence_count}
              </span>{" "}
              evidence cards
            </span>
            <ExternalLink className="w-3 h-3 ml-auto text-[#c8c0b4] cursor-pointer hover:text-[#7a756e]" />
          </div>
        </div>
      </div>
    </div>
  );
}
