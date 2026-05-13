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


def _extract_json_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    in_string = False
    escaped = False
    depth = 0
    for index, char in enumerate(text[start:], start=start):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def _load_json_with_repair(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError as original_exc:
        extracted = _extract_json_object(text)
        if extracted is None or extracted == text:
            raise original_exc
        return json.loads(extracted)


def parse_model_json(raw: str, schema: type[T]) -> T:
    text = strip_json_markdown(raw)
    try:
        payload = _load_json_with_repair(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM response was not valid JSON: {exc.msg}") from exc

    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"LLM response did not match {schema.__name__}: {exc}") from exc
