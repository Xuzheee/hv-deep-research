from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.research_plan import ResearchPlan
from app.agent.state import ReportAgentState


def research_planner(state: ReportAgentState) -> ReportAgentState:
    subject = state["subject"]
    state["research_plan"] = ResearchPlan(
        subject=subject,
        subject_type=state["subject_type"],
        research_motivation=f"为 {subject} 生成一份 evidence-backed 的 commercial-quality 横纵分析研究报告。",
        vertical_questions=[
            f"{subject} 的 origin story 是什么？它为什么会在那个时间点出现？",
            f"{subject} 从 launch 到现在经历了哪些关键 milestone、turning point 和 product evolution？",
            f"哪些 early decisions、strategic shifts 或 path dependencies 塑造了 {subject} 今天的位置？",
        ],
        horizontal_questions=[
            f"{subject} 当前的 direct competitors、indirect substitutes 或 alternative workflows 是什么？",
            f"{subject} 的 capability boundaries、limitations 和 risks 分别在哪里？",
            f"pricing、access、developer workflow fit、enterprise readiness 在同类方案里怎么比较？",
        ],
        supplementary_questions=[
            f"有哪些 customer signals、community signals、developer signals 或 market signals 值得补充？",
            f"有哪些 credible risks、weaknesses 或 controversy 需要在报告里明确说明？",
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
