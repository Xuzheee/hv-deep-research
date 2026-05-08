from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.research_plan import ResearchPlan
from app.agent.state import ReportAgentState


def research_planner(state: ReportAgentState) -> ReportAgentState:
    subject = state["subject"]
    state["research_plan"] = ResearchPlan(
        subject=subject,
        subject_type=state["subject_type"],
        research_motivation=f"Build an MVP evidence-backed report about {subject}.",
        vertical_questions=[
            f"How has {subject} evolved over time?",
            f"What major milestones shaped {subject}?",
        ],
        horizontal_questions=[
            f"What alternatives or competitors are relevant to {subject}?",
            f"Where are the capability boundaries for {subject}?",
        ],
        supplementary_questions=[f"What limitations should be noted for {subject}?"],
        initial_queries=[
            f"{subject} official launch capabilities",
            f"{subject} competitors alternatives",
        ],
        expected_competitors=[],
        source_preferences=["official_docs", "official_blog", "github_readme"],
    )
    return ProgressReporter().report(state, "searching", "Planning research questions.")
