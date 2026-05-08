from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.agent.llm.json_utils import parse_model_json
from app.config import settings

T = TypeVar("T", bound=BaseModel)


def is_llm_configured() -> bool:
    return settings.llm_provider != "mock" and bool(settings.llm_api_key.strip())


def complete_json(prompt: str, schema: type[T], system_prompt: str | None = None) -> T:
    if settings.llm_provider != "openai_compatible":
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    base_url = settings.llm_base_url.rstrip("/")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = httpx.post(
        f"{base_url}/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "temperature": settings.llm_temperature,
            "messages": messages,
            "response_format": {"type": "json_object"},
        },
        timeout=settings.llm_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return parse_model_json(content, schema)
