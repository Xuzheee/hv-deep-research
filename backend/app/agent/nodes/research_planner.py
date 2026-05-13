from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.llm.prompts import SYSTEM_PROMPT, build_research_planner_prompt
from app.agent.progress_reporter import ProgressReporter
from app.agent.schemas.research_plan import PlannedQuery, ResearchPlan
from app.agent.state import ReportAgentState


def _append_planner_warning(state: ReportAgentState, message: str) -> None:
    state.setdefault("run_log", []).append(
        {
            "level": "warning",
            "node": "research_planner",
            "message": message,
        }
    )


def _is_usable_plan(plan: ResearchPlan) -> bool:
    planned_dimensions = {query.intended_dimension for query in plan.planned_queries}
    return (
        len(plan.initial_queries) >= 6
        and len(plan.planned_queries) >= 6
        and bool(plan.vertical_questions)
        and bool(plan.horizontal_questions)
        and {"vertical", "horizontal"}.issubset(planned_dimensions)
    )


def _deterministic_research_plan(state: ReportAgentState) -> ResearchPlan:
    subject = state["subject"]
    planned_queries = [
        PlannedQuery(query=f"{subject} official product features pricing enterprise", intended_dimension="both"),
        PlannedQuery(query=f"{subject} official blog changelog launch updates", intended_dimension="vertical"),
        PlannedQuery(query=f"{subject} funding revenue valuation customers adoption", intended_dimension="both"),
        PlannedQuery(query=f"{subject} competitors alternatives comparison", intended_dimension="horizontal"),
        PlannedQuery(query=f"{subject} limitations risks weaknesses developer feedback", intended_dimension="horizontal"),
        PlannedQuery(query=f"{subject} market analysis positioning moat", intended_dimension="horizontal"),
        PlannedQuery(query=f"{subject} customer case studies enterprise use cases", intended_dimension="supplementary"),
        PlannedQuery(query=f"{subject} docs github community developer experience", intended_dimension="supplementary"),
        PlannedQuery(query=f"{subject} official changelog release notes roadmap", intended_dimension="vertical"),
        PlannedQuery(query=f"{subject} founder interview origin history", intended_dimension="vertical"),
        PlannedQuery(query=f"{subject} reviews reddit hacker news github issues", intended_dimension="supplementary"),
        PlannedQuery(query=f"{subject} enterprise security compliance", intended_dimension="supplementary"),
    ]
    return ResearchPlan(
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
        initial_queries=[planned_query.query for planned_query in planned_queries],
        planned_queries=planned_queries,
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


def research_planner(state: ReportAgentState) -> ReportAgentState:
    plan = _deterministic_research_plan(state)
    if is_llm_configured():
        try:
            prompt = build_research_planner_prompt(state["subject"], state["subject_type"])
            llm_plan = complete_json(prompt, ResearchPlan, system_prompt=SYSTEM_PROMPT)
            if _is_usable_plan(llm_plan):
                plan = llm_plan
            else:
                _append_planner_warning(state, "LLM research plan was weak; used deterministic fallback.")
        except Exception as exc:
            _append_planner_warning(state, f"LLM research planning failed; used deterministic fallback: {exc.__class__.__name__}")

    state["research_plan"] = plan
    return ProgressReporter().report(state, "searching", "Planning research questions.")
