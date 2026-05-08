import httpx
import pytest

from app.agent.tools.validation import validate_external_tools
from app.config import settings


@pytest.mark.skipif(
    not settings.run_real_tool_tests or not settings.tavily_api_key or not settings.firecrawl_api_key,
    reason="Set RUN_REAL_TOOL_TESTS=true with TAVILY_API_KEY and FIRECRAWL_API_KEY to run real tool validation.",
)
def test_real_external_tools_validate_successfully() -> None:
    results = validate_external_tools(httpx)

    assert all(result.configured for result in results)
    assert all(result.ok for result in results), [result.model_dump() for result in results]
