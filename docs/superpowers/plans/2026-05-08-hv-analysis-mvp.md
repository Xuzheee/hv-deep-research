# HV Analysis MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest runnable end-to-end HV Analysis Deep Research app: submit a topic from the existing Figma/Vite dashboard prototype, run one simplified research workflow, persist artifacts/history, poll status, and render a three-tab report.

**Architecture:** The existing Vite + React + TypeScript dashboard in `Design AI Research Dashboard/` calls a FastAPI backend. FastAPI stores report metadata/events in SQLite, runs a LangGraph workflow in a background task, writes JSON artifacts under `backend/app/outputs/reports/<report_id>/`, and exposes polling endpoints for the frontend. The LangGraph MVP uses one linear `collect_info` node instead of separate parallel collectors, then produces Evidence Cards, vertical analysis, horizontal analysis, quality results, and `report_data.json` matching the frontend prototype types.

**Tech Stack:** Existing Vite React TypeScript frontend from Figma Make, FastAPI + Python, SQLite, Pydantic v2, LangGraph, mockable Tavily/Firecrawl adapters, pytest, Ruff.

---

## Source Documents and Prototype Context

- Read: `PROJECT_DOCUMENT.md`
- Read: `CLAUDE.md`
- Figma Make URL: `https://www.figma.com/make/2PT7aKgTnZvw94gL6O7xqW/Design-AI-Research-Dashboard?t=98hHLlLyXlwy7DYJ-1`
- Figma Make source already exists locally in `Design AI Research Dashboard/`.
- Figma MCP `get_design_context` for node `0:1` confirms the Make file exposes the same source files already present locally.
- Figma Make does not support `get_screenshot`; use local prototype runtime for visual validation.
- Missing: `AGENTS.md` was requested earlier but does not exist under the workspace.

## MVP Boundary

### Included

- Existing Vite single-page dashboard prototype
- FastAPI backend
- SQLite database
- LangGraph MVP workflow with unified `collect_info`
- Mockable Tavily search and Firecrawl scrape wrappers
- Evidence Cards and Pydantic schema validation
- Three Tab report display using existing components
- Historical report saving
- Task status polling
- Local JSON artifacts

### Excluded

- Migrating the prototype to Next.js during MVP
- User accounts and permissions
- Cloud deployment
- PDF export
- Advanced charts beyond existing prototype UI
- Human review nodes
- Celery/Redis
- SSE event stream
- Parallel `vertical_collect` / `horizontal_collect` / `supplementary_collect`
- Multi-theme templates

## Smallest Runnable End-to-End Version

1. User opens the existing Vite dashboard.
2. User enters a topic and subject type, then clicks **Deep Research**.
3. Frontend calls `POST /api/reports`.
4. FastAPI creates a SQLite `reports` row with `pending` status and starts a background LangGraph run.
5. LangGraph runs this MVP path:

```text
initialize_report_run
  -> research_planner
  -> collect_info
  -> evidence_filter
  -> vertical_analysis
  -> horizontal_analysis
  -> synthesis_report_data
  -> quality_check
  -> persist_report_artifacts
```

6. Backend writes `report_data.json`, `evidence_cards.json`, `raw_sources.json`, `run_log.json`, and `quality_check.json`.
7. Frontend polls `GET /api/reports/{report_id}/status` until `completed` or `failed`.
8. On completion, frontend calls `GET /api/reports/{report_id}` and renders existing Overview, Vertical Analysis, and Horizontal Analysis tabs.
9. Left sidebar lists the saved report from `GET /api/reports`.

---

## Planned File Structure

```text
backend/
├─ requirements.txt
├─ pytest.ini
├─ .env.example
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ config.py
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ routes_reports.py
│  │  └─ schemas.py
│  ├─ agent/
│  │  ├─ __init__.py
│  │  ├─ graph.py
│  │  ├─ progress_reporter.py
│  │  ├─ state.py
│  │  ├─ nodes/
│  │  │  ├─ __init__.py
│  │  │  ├─ initialize_report_run.py
│  │  │  ├─ research_planner.py
│  │  │  ├─ collect_info.py
│  │  │  ├─ evidence_filter.py
│  │  │  ├─ vertical_analysis.py
│  │  │  ├─ horizontal_analysis.py
│  │  │  ├─ synthesis_report_data.py
│  │  │  ├─ quality_check.py
│  │  │  └─ persist_report_artifacts.py
│  │  ├─ schemas/
│  │  │  ├─ __init__.py
│  │  │  ├─ evidence.py
│  │  │  ├─ quality.py
│  │  │  ├─ report.py
│  │  │  ├─ research_plan.py
│  │  │  └─ source.py
│  │  └─ tools/
│  │     ├─ __init__.py
│  │     ├─ firecrawl_tool.py
│  │     ├─ file_store.py
│  │     ├─ source_ranker.py
│  │     └─ tavily_tool.py
│  ├─ db/
│  │  ├─ __init__.py
│  │  ├─ models.py
│  │  ├─ repository.py
│  │  └─ session.py
│  └─ outputs/
│     └─ reports/.gitkeep
└─ tests/
   ├─ test_agent_graph.py
   ├─ test_api_reports.py
   ├─ test_db_repository.py
   ├─ test_file_store.py
   ├─ test_health.py
   └─ test_schemas.py

Design AI Research Dashboard/
├─ package.json
├─ vite.config.ts
├─ src/
│  ├─ app/
│  │  ├─ App.tsx
│  │  ├─ components/...
│  │  └─ data/
│  │     ├─ mockData.ts
│  │     └─ types.ts
│  └─ styles/...
```

---

## Task 1: Backend Runtime, Health Check, and Existing Frontend Baseline

**Purpose:** Create the backend runtime while preserving the existing Vite/Figma frontend prototype as the UI baseline.

**Files:**

- Create: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/tests/test_health.py`
- Modify only if needed for install/build compatibility: `Design AI Research Dashboard/package.json`

**Implementation notes:**

- Backend starts with only `GET /health`.
- Preserve all existing frontend components and mock data.
- Do not create a new `frontend/` directory.
- Use CORS in FastAPI for local development from `http://localhost:5173` because the current frontend is Vite.
- Add `.env.example` but do not hardcode API keys.

**Steps:**

- [ ] Create the backend package skeleton.

```bash
mkdir -p backend/app backend/tests backend/app/outputs/reports
```

- [ ] Create `backend/requirements.txt` with MVP dependencies.

```text
fastapi==0.128.0
uvicorn[standard]
pydantic>=2.0
pydantic-settings
sqlalchemy>=2.0
langgraph==1.0.8
httpx
python-dotenv
pytest
ruff
```

- [ ] Create `backend/.env.example` with:

```text
DATABASE_URL=sqlite:///./hv_analysis.db
BACKEND_CORS_ORIGINS=http://localhost:5173
TAVILY_API_KEY=
FIRECRAWL_API_KEY=
```

- [ ] Create `backend/app/config.py` using `pydantic-settings` for `database_url`, `backend_cors_origins`, `tavily_api_key`, and `firecrawl_api_key`.
- [ ] Create `backend/app/main.py` with `FastAPI()`, CORS middleware, and `GET /health` returning `{"status": "ok"}`.
- [ ] Create `backend/tests/test_health.py` using `fastapi.testclient.TestClient` and assert `GET /health` returns 200 and `{"status": "ok"}`.
- [ ] Install and build the existing frontend without changing visual/component code unless the baseline build is broken.

**Validation commands:**

```bash
python -m pip install -r backend/requirements.txt
python -m pytest backend/tests/test_health.py -q
python -m ruff check backend/app backend/tests
npm --prefix "Design AI Research Dashboard" install
npm --prefix "Design AI Research Dashboard" run build
```

**Expected result:**

- Backend health test passes.
- Backend lint passes.
- Existing Figma/Vite frontend builds successfully.

---

## Task 2: Shared Schemas and SQLite Persistence

**Purpose:** Establish backend contracts that match the existing frontend `src/app/data/types.ts` shape.

**Files:**

- Create: `backend/app/agent/schemas/research_plan.py`
- Create: `backend/app/agent/schemas/source.py`
- Create: `backend/app/agent/schemas/evidence.py`
- Create: `backend/app/agent/schemas/report.py`
- Create: `backend/app/agent/schemas/quality.py`
- Create: `backend/app/agent/schemas/__init__.py`
- Create: `backend/app/agent/state.py`
- Create: `backend/app/api/schemas.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/models.py`
- Create: `backend/app/db/repository.py`
- Create: `backend/tests/test_schemas.py`
- Create: `backend/tests/test_db_repository.py`
- Modify: `backend/app/config.py`

**Implementation notes:**

- Backend `ReportData` must serialize fields used by `Design AI Research Dashboard/src/app/data/types.ts`:
  - `report_id`, `topic`, `subject`, `subject_type`, `title`, `subtitle`
  - `overview`, `vertical`, `horizontal`
  - `quality_warning`, `quality_issues`, `quality_score`
  - `source_count`, `evidence_count`, `generated_at`, `limitations`
- Keep richer internal evidence/source schemas, but API detail response should include a `report_data` object compatible with the frontend.
- Use SQLAlchemy 2.0 with SQLite.
- Store artifact paths as text columns in `reports`.
- Keep `report_artifacts` out of MVP because the spec marks it optional.

**Validation commands:**

```bash
python -m pytest backend/tests/test_schemas.py backend/tests/test_db_repository.py -q
python -m ruff check backend/app backend/tests
```

**Expected result:**

- Schema validation tests pass.
- Repository can create a report, update status, insert events, update artifact paths, and list history.

---

## Task 3: File Store, Source Ranking, and Mockable Tool Wrappers

**Purpose:** Provide deterministic local artifact writes and search/scrape adapters that can run without real API keys during MVP validation.

**Files:**

- Create: `backend/app/agent/tools/file_store.py`
- Create: `backend/app/agent/tools/source_ranker.py`
- Create: `backend/app/agent/tools/tavily_tool.py`
- Create: `backend/app/agent/tools/firecrawl_tool.py`
- Create: `backend/app/agent/tools/__init__.py`
- Create: `backend/tests/test_file_store.py`
- Modify: `backend/.env.example`
- Modify: `backend/app/config.py`

**Implementation notes:**

- `file_store.py` owns `backend/app/outputs/reports/<report_id>/` creation and JSON writes.
- `source_ranker.py` implements tier scoring, domain bonuses, and low-quality URL/title filtering from `PROJECT_DOCUMENT.md` sections 11 and 24.
- `tavily_tool.py` and `firecrawl_tool.py` should expose functions returning project-owned schema objects.
- If API keys are missing, wrappers should return deterministic mock data for development/test runs instead of failing the MVP path.
- Tests must not call external services.

**Validation commands:**

```bash
python -m pytest backend/tests/test_file_store.py -q
python -m pytest backend/tests/test_schemas.py backend/tests/test_db_repository.py backend/tests/test_file_store.py -q
python -m ruff check backend/app backend/tests
```

**Expected result:**

- Artifact write paths are stable and testable.
- Source ranking filters low-quality URLs and assigns source scores.
- Tool wrappers are importable and testable without network calls.

---

## Task 4: LangGraph MVP Workflow

**Purpose:** Create the linear agent path that generates a frontend-compatible `ReportData` artifact from one request.

**Files:**

- Create: `backend/app/agent/graph.py`
- Create: `backend/app/agent/progress_reporter.py`
- Create: `backend/app/agent/nodes/initialize_report_run.py`
- Create: `backend/app/agent/nodes/research_planner.py`
- Create: `backend/app/agent/nodes/collect_info.py`
- Create: `backend/app/agent/nodes/evidence_filter.py`
- Create: `backend/app/agent/nodes/vertical_analysis.py`
- Create: `backend/app/agent/nodes/horizontal_analysis.py`
- Create: `backend/app/agent/nodes/synthesis_report_data.py`
- Create: `backend/app/agent/nodes/quality_check.py`
- Create: `backend/app/agent/nodes/persist_report_artifacts.py`
- Create: `backend/app/agent/nodes/__init__.py`
- Create: `backend/tests/test_agent_graph.py`

**Implementation notes:**

- Use LangGraph `StateGraph` with explicit node names and linear edges.
- `collect_info` is the only node allowed to call Tavily/Firecrawl wrappers.
- `MAX_TOOL_CALLS = 12` belongs in `collect_info.py`.
- Analysis nodes should consume evidence cards, not raw scraped pages.
- For MVP, node implementations can be deterministic and evidence-derived; real LLM integration can come after the runnable end-to-end slice.
- `persist_report_artifacts` writes all JSON artifacts through `ReportFileStore`.

**Validation commands:**

```bash
python -m pytest backend/tests/test_agent_graph.py -q
python -m pytest backend/tests -q
python -m ruff check backend/app backend/tests
```

**Expected result:**

- The graph completes without external API keys.
- The graph produces valid Pydantic `ReportData` compatible with existing frontend types.
- JSON artifacts are written in the expected output directory.

---

## Task 5: Reports API and Background Execution

**Purpose:** Expose the backend API contract required by the existing dashboard.

**Files:**

- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/routes_reports.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/db/repository.py`
- Modify: `backend/app/agent/progress_reporter.py`
- Create: `backend/tests/test_api_reports.py`

**Implementation notes:**

- Implement only these MVP endpoints:
  - `POST /api/reports`
  - `GET /api/reports`
  - `GET /api/reports/{report_id}`
  - `GET /api/reports/{report_id}/status`
- Do not implement SSE, rerun, or delete in MVP.
- `POST /api/reports` creates a pending DB record before starting the background task.
- `GET /api/reports` returns list items compatible with `HistoryReport` except `report_data` may be `null`.
- `GET /api/reports/{report_id}` returns a detail object including `report_data` when completed.
- API tests can use a synchronous test hook for the background runner rather than starting real network calls.

**Validation commands:**

```bash
python -m pytest backend/tests/test_api_reports.py -q
python -m pytest backend/tests -q
python -m ruff check backend/app backend/tests
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Manual checks while the server is running:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/reports
```

**Expected result:**

- Backend API contract is test-covered.
- A report can be created, listed, polled, and fetched.

---

## Task 6: Connect Existing Figma/Vite Dashboard to Backend API

**Purpose:** Replace prototype-only local submit/history behavior with backend API calls while preserving the existing design and component structure.

**Files:**

- Create: `Design AI Research Dashboard/src/app/data/api.ts`
- Modify: `Design AI Research Dashboard/src/app/App.tsx`
- Modify if needed: `Design AI Research Dashboard/src/app/data/types.ts`
- Modify if needed: `Design AI Research Dashboard/src/app/components/ResearchInputBar.tsx`
- Modify if needed: `Design AI Research Dashboard/src/app/components/HistorySidebar.tsx`
- Modify if needed: `Design AI Research Dashboard/src/app/components/ReportWorkspace.tsx`
- Modify if needed: `Design AI Research Dashboard/src/app/components/ProgressPanel.tsx`

**Implementation notes:**

- Preserve the current visual structure and components from the Figma Make prototype.
- Add API functions:
  - `createReport(input)`
  - `listReports()`
  - `getReport(reportId)`
  - `getReportStatus(reportId)`
- Backend base URL should come from `VITE_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`.
- On load, fetch history from backend. If backend is unavailable, show the existing mock reports as a design fallback and a visible connection error.
- On submit, call backend `POST /api/reports`, insert returned report into state, and start polling.
- Poll every 2 seconds until `completed` or `failed`.
- On `completed`, fetch report detail and replace `report_data` in the active report.
- Do not add new chart libraries or redesign components.

**Validation commands:**

```bash
npm --prefix "Design AI Research Dashboard" run build
```

**Expected result:**

- Existing dashboard builds successfully.
- When backend is running, submit/history/status/detail use real API data.
- When backend is not running, the prototype still opens with mock data and visible connection feedback.

---

## Task 7: End-to-End Local Verification and MVP Acceptance

**Purpose:** Prove the smallest runnable product works through the browser and API.

**Files:**

- Modify only if validation reveals bugs in files from Tasks 1-6.
- No new feature files should be created in this task.

**Implementation notes:**

- This task is for integration fixes only.
- Do not expand scope to SSE, rerun, delete, export, auth, charts, deployment, migration to Next.js, or parallel collectors.
- The MVP must work without real external API keys through deterministic mock adapters.

**Validation commands:**

```bash
python -m pytest backend/tests -q
python -m ruff check backend/app backend/tests
npm --prefix "Design AI Research Dashboard" run build
```

Manual validation:

```bash
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
npm --prefix "Design AI Research Dashboard" run dev
```

Browser checks:

- Open the Vite dev server URL.
- Enter topic `GPT-4o`.
- Select subject type `product`.
- Click **Deep Research**.
- Confirm progress appears and changes from `pending` to later statuses.
- Confirm final state is `completed` or a visible `failed` state with an error message.
- If completed, confirm Overview, Vertical Analysis, and Horizontal Analysis tabs render.
- Confirm the report appears in the left history sidebar.
- Click the history item and confirm it reloads the same report.

Artifact validation:

```bash
ls backend/app/outputs/reports
```

For the generated report directory, confirm these files exist:

```text
report_data.json
evidence_cards.json
raw_sources.json
run_log.json
quality_check.json
```

**Expected result:**

- Automated backend tests pass.
- Existing Vite frontend build passes.
- Manual browser flow proves: create report, poll status, render three tabs, save history, reload history, and write JSON artifacts.

---

## Self-Review Against `PROJECT_DOCUMENT.md`

### Coverage

- Dashboard UI: existing Figma/Vite prototype, connected in Task 6
- FastAPI backend: Tasks 1 and 5
- SQLite database: Task 2
- LangGraph Agent workflow: Task 4
- Tavily search: Task 3 and Task 4 via mockable wrapper
- Firecrawl scrape: Task 3 and Task 4 via mockable wrapper
- Evidence Cards: Task 2 and Task 4
- Pydantic Schema validation: Task 2 and Task 4
- Three Tab report display: existing prototype + Task 6
- History report saving: Tasks 2, 5, and 6
- Task status polling: Tasks 5 and 6
- JSON artifacts: Tasks 3, 4, and 7

### Explicitly Deferred Non-MVP Items

- Next.js migration: deferred because existing completed prototype is Vite and MVP prioritizes runnable end-to-end flow
- SSE events: deferred
- Rerun endpoint: deferred
- Delete endpoint: deferred
- PDF export: deferred
- User system: deferred
- Redis/Celery: deferred
- Cloud deployment: deferred
- Human review: deferred
- Parallel collectors: deferred

### Type Consistency

The backend API must align with these existing frontend names from `Design AI Research Dashboard/src/app/data/types.ts`:

- `SubjectType`
- `ReportStatus`
- `ReportData`
- `HistoryReport`
- `ProgressStep`

