from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.research_plan import ResearchPlan
from app.agent.state import ReportAgentState


def research_planner(state: ReportAgentState) -> ReportAgentState:
    subject = state["subject"]
    state["research_plan"] = ResearchPlan(
        subject=subject,
        subject_type=state["subject_type"],
        research_motivation=f"Build a commercial-quality evidence-backed report about {subject}.",
        vertical_questions=[
            f"How did {subject} originate and evolve over time?",
            f"What launch, adoption, funding, customer, or product milestones shaped {subject}?",
            f"What major turning points changed {subject}'s market position or product direction?",
        ],
        horizontal_questions=[
            f"What alternatives or competitors are relevant to {subject}?",
            f"Where are the capability boundaries, limitations, and risks for {subject}?",
            f"How do pricing, access, developer workflow fit, and enterprise readiness compare for {subject}?",
        ],
        supplementary_questions=[
            f"What customer, community, developer, or market signals should be noted for {subject}?",
            f"What credible risks or weaknesses should be considered for {subject}?",
        ],
        initial_queries=[
            f"{subject} official product features pricing enterprise",
            f"{subject} official blog changelog launch updates",
            f"{subject} funding revenue valuation customers adoption",
            f"{subject} competitors alternatives comparison",
            f"{subject} limitations risks weaknesses developer feedback",
            f"{subject} market analysis positioning moat",
            f"{subject} customer case studies enterprise use cases",
            f"{subject} docs github community developer experience",
        ],
        expected_competitors=[],
        source_preferences=[
            "official_site",
            "official_docs",
            "official_blog",
            "official_changelog",
            "credible_media",
            "market_analysis",
            "customer_case_studies",
            "community_developer_signals",
        ],
    )
    return ProgressReporter().report(state, "searching", "Planning research questions.")
