import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def strip_json_markdown(raw: str) -> str:
    text = raw.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return text


def parse_model_json(raw: str, schema: type[T]) -> T:
    text = strip_json_markdown(raw)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response was not valid JSON: {exc.msg}") from exc

    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"LLM response did not match {schema.__name__}: {exc}") from exc
