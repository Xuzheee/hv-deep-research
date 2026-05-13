# Design AI Research Dashboard

HV Analysis Deep Research Web App is a local research workspace that combines a React dashboard, FastAPI backend, and LangGraph agent pipeline.

The original design bundle is available at https://www.figma.com/design/2PT7aKgTnZvw94gL6O7xqW/Design-AI-Research-Dashboard.

The app lets a user enter a research topic, run a deep research task, track progress, and read a saved three-tab report with evidence-backed overview, vertical analysis, and horizontal analysis.

## Current architecture status

As of 2026-05-13, the backend has advanced beyond the initial MVP skeleton:

```text
React Dashboard
  ↓
FastAPI /api/reports
  ↓
LangGraph report pipeline
  ↓
Tavily search + Firecrawl scrape adapters
  ↓
Pydantic schemas + SQLite metadata + local JSON/HTML artifacts
```

Implemented report pipeline:

```text
initialize_report_run
  ↓
research_planner
  ↓
collect_info
  ↓
evidence_filter
  ↓
vertical_analysis
  ↓
horizontal_analysis
  ↓
cross_insights
  ↓
synthesis_report_data
  ↓
quality_check
  ↓
quality_remediation when needed, once only
  ↓
persist_report_artifacts
```

Implemented backend capabilities:

- Report creation, listing, detail retrieval, and status polling APIs.
- SQLite report metadata and run event storage.
- Local artifacts: `report_data.json`, `evidence_cards.json`, `raw_sources.json`, `run_log.json`, `quality_check.json`, and `index.html`.
- Dimension-aware collection through `planned_queries` for vertical, horizontal, supplementary, and both dimensions.
- Evidence filtering with source prefiltering, deduplication, evidence groups, and deterministic fallback behavior.
- Dedicated `cross_insights` node and bounded `quality_remediation` node.
- JSON repair for Markdown-wrapped or prefixed/suffixed LLM JSON output.

Known remaining architecture gaps:

- Collection is still a single `collect_info` node, not split into parallel `vertical_collect`, `horizontal_collect`, and `supplementary_collect` nodes.
- Vertical and horizontal analysis currently run sequentially, not in parallel.
- Progress uses polling, not SSE.
- Rerun/delete APIs, PDF export, multi-user auth, and cloud deployment are not part of the current MVP.

## Running the frontend

Run `npm i` to install the dependencies.

Run `npm run dev` to start the development server.

## Backend validation baseline

From the repository root, the backend test baseline is:

```bash
"D:/anaconda/python.exe" -m pytest "c:/Users/31009/clauddd/new/backend/tests" -q
```

Current expected result:

```text
89 passed, 2 skipped
```
