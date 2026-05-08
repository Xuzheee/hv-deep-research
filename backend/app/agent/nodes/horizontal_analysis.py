from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.report import CapabilityBoundary, CompetitorMatrixItem, HorizontalTabData, Recommendation
from app.agent.state import ReportAgentState


def horizontal_analysis(state: ReportAgentState) -> ReportAgentState:
    evidence_ids = [card.evidence_id for card in state["evidence_cards"][:3]]
    subject = state["subject"]
    state["horizontal"] = HorizontalTabData(
        full_text=f"{subject} is positioned against adjacent products and developer ecosystem signals.",
        competitor_scenario="few_competitors",
        competitor_matrix=[
            CompetitorMatrixItem(
                competitor_id="comp_001",
                name="Adjacent AI research tools",
                role="Alternative workflow category",
                strengths=["Comparable research assistance"],
                weaknesses=["Evidence traceability varies by tool"],
                best_for="Teams evaluating research workflows",
                pricing_or_access=None,
                supporting_evidence_ids=evidence_ids,
            )
        ],
        capability_boundaries=[
            CapabilityBoundary(
                boundary_id="boundary_001",
                title="Evidence quality boundary",
                description="The MVP output is bounded by available sources and deterministic mock adapters.",
                boundary_type="current_weakness",
                supporting_evidence_ids=evidence_ids,
            )
        ],
        positioning_summary=f"{subject} is framed through a small evidence-backed MVP comparison.",
        recommendations=[
            Recommendation(
                rec_id="rec_001",
                title="Validate with live source adapters",
                content="Replace mock tool outputs with real Tavily and Firecrawl calls before using the report for decisions.",
                priority="medium",
                target_audience="product researchers",
                rationale="The MVP proves the workflow shape but not live-source coverage.",
                supporting_evidence_ids=evidence_ids,
            )
        ],
    )
    return ProgressReporter().report(state, "synthesizing", "Completed horizontal analysis.")
