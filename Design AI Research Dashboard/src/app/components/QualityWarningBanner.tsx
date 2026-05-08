import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

interface QualityWarningBannerProps {
  issues: string[];
  score: number;
}

export function QualityWarningBanner({ issues, score }: QualityWarningBannerProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-amber-200 bg-amber-50 rounded-md px-4 py-3">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[13px] text-amber-800" style={{ fontWeight: 500 }}>
              Quality Warning — Score {score}/100
            </span>
            <span className="text-[11px] text-amber-600 bg-amber-100 px-2 py-0.5 rounded">
              {issues.length} issue{issues.length !== 1 ? "s" : ""} detected
            </span>
            <button
              onClick={() => setExpanded(!expanded)}
              className="ml-auto flex items-center gap-1 text-[12px] text-amber-700 hover:text-amber-900 transition-colors"
            >
              {expanded ? (
                <>
                  <ChevronUp className="w-3 h-3" />
                  Hide
                </>
              ) : (
                <>
                  <ChevronDown className="w-3 h-3" />
                  Show details
                </>
              )}
            </button>
          </div>
          <p className="text-[12px] text-amber-700 mt-0.5">
            This report was generated with insufficient evidence coverage. Review findings with caution.
          </p>
          {expanded && (
            <ul className="mt-2 space-y-1">
              {issues.map((issue, idx) => (
                <li key={idx} className="flex items-start gap-2 text-[12px] text-amber-700">
                  <span className="mt-1 w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0" />
                  {issue}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
