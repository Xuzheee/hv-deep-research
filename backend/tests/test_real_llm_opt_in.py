import pytest
from pydantic import BaseModel

from app.agent.llm.client import complete_json
from app.config import settings


class RealLlmSmokeResult(BaseModel):
    name: str


@pytest.mark.skipif(
    not settings.run_real_llm_tests or not settings.llm_api_key,
    reason="Set RUN_REAL_LLM_TESTS=true with LLM_PROVIDER=openai_compatible and LLM_API_KEY to run real LLM validation.",
)
def test_real_llm_returns_schema_valid_json() -> None:
    result = complete_json(
        'Return exactly this JSON object: {"name":"ok"}',
        RealLlmSmokeResult,
        system_prompt="Return JSON only.",
    )

    assert result.name == "ok"
