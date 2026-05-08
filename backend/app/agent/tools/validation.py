from pydantic import BaseModel

from app.agent.tools.firecrawl_tool import FIRECRAWL_ENDPOINT
from app.agent.tools.tavily_tool import TAVILY_ENDPOINT
from app.config import settings


class ToolValidationResult(BaseModel):
    tool_name: str
    configured: bool
    ok: bool
    status_code: int | None = None
    message: str
    sample_count: int = 0


def validate_tavily_connection(http_client, query: str = "GPT-4o") -> ToolValidationResult:
    if not settings.tavily_api_key.strip():
        return ToolValidationResult(
            tool_name="tavily_search",
            configured=False,
            ok=False,
            message="TAVILY_API_KEY is not configured.",
        )

    try:
        response = http_client.post(
            TAVILY_ENDPOINT,
            json={"api_key": settings.tavily_api_key, "query": query, "max_results": 1},
            timeout=settings.external_tool_validation_timeout_seconds,
        )
        response.raise_for_status()
        sample_count = len(response.json().get("results", []))
        return ToolValidationResult(
            tool_name="tavily_search",
            configured=True,
            ok=True,
            status_code=response.status_code,
            message="Tavily validation request succeeded.",
            sample_count=sample_count,
        )
    except Exception as exc:
        return ToolValidationResult(
            tool_name="tavily_search",
            configured=True,
            ok=False,
            status_code=getattr(getattr(exc, "response", None), "status_code", None),
            message=f"Tavily validation request failed: {exc.__class__.__name__}",
        )


def validate_firecrawl_connection(http_client, url: str = "https://example.com") -> ToolValidationResult:
    if not settings.firecrawl_api_key.strip():
        return ToolValidationResult(
            tool_name="firecrawl_scrape",
            configured=False,
            ok=False,
            message="FIRECRAWL_API_KEY is not configured.",
        )

    try:
        response = http_client.post(
            FIRECRAWL_ENDPOINT,
            headers={"Authorization": f"Bearer {settings.firecrawl_api_key}"},
            json={"url": url, "formats": ["markdown"]},
            timeout=settings.external_tool_validation_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json().get("data", response.json())
        sample_count = 1 if payload.get("markdown") or payload.get("metadata") else 0
        return ToolValidationResult(
            tool_name="firecrawl_scrape",
            configured=True,
            ok=True,
            status_code=response.status_code,
            message="Firecrawl validation request succeeded.",
            sample_count=sample_count,
        )
    except Exception as exc:
        return ToolValidationResult(
            tool_name="firecrawl_scrape",
            configured=True,
            ok=False,
            status_code=getattr(getattr(exc, "response", None), "status_code", None),
            message=f"Firecrawl validation request failed: {exc.__class__.__name__}",
        )


def validate_external_tools(http_client) -> list[ToolValidationResult]:
    return [validate_tavily_connection(http_client), validate_firecrawl_connection(http_client)]
