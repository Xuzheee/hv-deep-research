#CLAUDE.md
You are working on the HV Analysis Deep Research Web App.

Primary goal:
Build a runnable MVP for a Deep Research report workspace.

Core architecture:
- Frontend: Next.js + React + TypeScript
- Backend: FastAPI + Python
- Agent: LangGraph
- Storage: SQLite + local JSON artifacts
- Tools: Tavily search and Firecrawl scrape

Development rules:
- Do not implement everything in one pass.
- Prefer small, verifiable changes.
- Preserve the architecture in PROJECT_DOCUMENT.md.
- Do not hardcode API keys.
- Use .env.example for environment variables.
- Every major change must include a validation command.
- If real external APIs are not available, create mock adapters first.
- Keep frontend and backend independently runnable.
- Prioritize an end-to-end MVP before advanced features.

Validation:
- Frontend: npm run lint and npm run build when available.
- Backend: python -m pytest when tests exist.
- Backend smoke test: start FastAPI and verify /api/reports endpoints.