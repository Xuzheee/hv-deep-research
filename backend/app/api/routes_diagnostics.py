from urllib.parse import urlparse

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.llm.client import complete_json, is_llm_configured
from app.agent.tools.validation import ToolValidationResult, validate_external_tools
from app.api.schemas import (
    DiagnosticsProviderStatus,
    DiagnosticsStatusResponse,
    DiagnosticsValidationResponse,
    DiagnosticsValidationResult,
)
from app.config import settings

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


class LlmValidationPayload(BaseModel):
    name: str


def _mode(configured: bool) -> str:
    return "real" if configured else "mock"


def _safe_base_url() -> str | None:
    parsed = urlparse(settings.llm_base_url)
    if not parsed.scheme or not parsed.hostname:
        return None
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{parsed.hostname}{port}"


def _tool_status(name: str, configured: bool) -> DiagnosticsProviderStatus:
    return DiagnosticsProviderStatus(name=name, configured=configured, mode=_mode(configured))


def _llm_status() -> DiagnosticsProviderStatus:
    configured = is_llm_configured()
    return DiagnosticsProviderStatus(
        name="llm",
        configured=configured,
        mode=_mode(configured),
        details={
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "base_url": _safe_base_url(),
        },
    )


def _skipped_result(name: str, configured: bool, message: str) -> DiagnosticsValidationResult:
    return DiagnosticsValidationResult(name=name, configured=configured, status="skipped", ok=False, message=message)


def _from_tool_validation(result: ToolValidationResult) -> DiagnosticsValidationResult:
    return DiagnosticsValidationResult(
        name=result.tool_name,
        configured=result.configured,
        status="passed" if result.ok else "failed",
        ok=result.ok,
        message=result.message,
        sample_count=result.sample_count,
    )


def _validate_llm() -> DiagnosticsValidationResult:
    configured = is_llm_configured()
    if not settings.run_real_llm_tests:
        return _skipped_result("llm", configured, "Live LLM validation is disabled.")
    if not configured:
        return _skipped_result("llm", False, "LLM is not configured.")

    try:
        result = complete_json(
            'Return exactly this JSON object: {"name":"ok"}',
            LlmValidationPayload,
            system_prompt="Return JSON only.",
        )
    except Exception as exc:
        return DiagnosticsValidationResult(
            name="llm",
            configured=True,
            status="failed",
            ok=False,
            message=f"LLM validation request failed: {exc.__class__.__name__}",
        )

    ok = result.name == "ok"
    return DiagnosticsValidationResult(
        name="llm",
        configured=True,
        status="passed" if ok else "failed",
        ok=ok,
        message="LLM validation request succeeded." if ok else "LLM response did not match expected payload.",
        sample_count=1 if ok else 0,
    )


@router.get("/status", response_model=DiagnosticsStatusResponse)
def get_diagnostics_status() -> DiagnosticsStatusResponse:
    tavily_configured = bool(settings.tavily_api_key.strip())
    firecrawl_configured = bool(settings.firecrawl_api_key.strip())
    return DiagnosticsStatusResponse(
        tools=[
            _tool_status("tavily_search", tavily_configured),
            _tool_status("firecrawl_scrape", firecrawl_configured),
        ],
        llm=_llm_status(),
        live_tool_validation_enabled=settings.run_real_tool_tests,
        live_llm_validation_enabled=settings.run_real_llm_tests,
    )


@router.post("/validate", response_model=DiagnosticsValidationResponse)
def validate_diagnostics() -> DiagnosticsValidationResponse:
    if settings.run_real_tool_tests:
        tool_results = [_from_tool_validation(result) for result in validate_external_tools(httpx)]
    else:
        tool_results = [
            _skipped_result("tavily_search", bool(settings.tavily_api_key.strip()), "Live tool validation is disabled."),
            _skipped_result(
                "firecrawl_scrape", bool(settings.firecrawl_api_key.strip()), "Live tool validation is disabled."
            ),
        ]

    return DiagnosticsValidationResponse(tools=tool_results, llm=_validate_llm())
