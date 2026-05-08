from fastapi.testclient import TestClient

from app.agent.tools.validation import ToolValidationResult
from app.api import routes_diagnostics
from app.main import app


def test_diagnostics_status_returns_mock_modes_without_keys(monkeypatch) -> None:
    monkeypatch.setattr(routes_diagnostics.settings, "tavily_api_key", "")
    monkeypatch.setattr(routes_diagnostics.settings, "firecrawl_api_key", "")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_provider", "mock")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_api_key", "")
    monkeypatch.setattr(routes_diagnostics.settings, "run_real_tool_tests", False)
    monkeypatch.setattr(routes_diagnostics.settings, "run_real_llm_tests", False)
    client = TestClient(app)

    response = client.get("/api/diagnostics/status")
    payload = response.json()

    assert response.status_code == 200
    assert [tool["mode"] for tool in payload["tools"]] == ["mock", "mock"]
    assert payload["llm"]["mode"] == "mock"
    assert payload["live_tool_validation_enabled"] is False
    assert payload["live_llm_validation_enabled"] is False


def test_diagnostics_status_returns_real_modes_without_leaking_keys(monkeypatch) -> None:
    monkeypatch.setattr(routes_diagnostics.settings, "tavily_api_key", "secret-tavily")
    monkeypatch.setattr(routes_diagnostics.settings, "firecrawl_api_key", "secret-firecrawl")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_api_key", "secret-llm")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_base_url", "https://secret-user:secret-base-url@api.deepseek.com:443/private/path")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_model", "deepseek-chat")
    client = TestClient(app)

    response = client.get("/api/diagnostics/status")
    text = response.text
    payload = response.json()

    assert response.status_code == 200
    assert [tool["mode"] for tool in payload["tools"]] == ["real", "real"]
    assert payload["llm"]["mode"] == "real"
    assert payload["llm"]["details"]["provider"] == "openai_compatible"
    assert payload["llm"]["details"]["model"] == "deepseek-chat"
    assert payload["llm"]["details"]["base_url"] == "https://api.deepseek.com:443"
    assert "secret-tavily" not in text
    assert "secret-firecrawl" not in text
    assert "secret-llm" not in text
    assert "secret-user" not in text
    assert "secret-base-url" not in text


def test_diagnostics_status_does_not_call_live_validation(monkeypatch) -> None:
    def fail_if_called(http_client):
        raise AssertionError("status endpoint must not validate live tools")

    monkeypatch.setattr(routes_diagnostics, "validate_external_tools", fail_if_called)
    client = TestClient(app)

    response = client.get("/api/diagnostics/status")

    assert response.status_code == 200


def test_diagnostics_validate_skips_when_opt_in_flags_are_false(monkeypatch) -> None:
    monkeypatch.setattr(routes_diagnostics.settings, "run_real_tool_tests", False)
    monkeypatch.setattr(routes_diagnostics.settings, "run_real_llm_tests", False)
    monkeypatch.setattr(routes_diagnostics.settings, "tavily_api_key", "secret-tavily")
    monkeypatch.setattr(routes_diagnostics.settings, "firecrawl_api_key", "secret-firecrawl")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_api_key", "secret-llm")
    client = TestClient(app)

    response = client.post("/api/diagnostics/validate")
    payload = response.json()

    assert response.status_code == 200
    assert all(result["ok"] is False for result in payload["tools"])
    assert [result["status"] for result in payload["tools"]] == ["skipped", "skipped"]
    assert payload["llm"]["ok"] is False
    assert payload["llm"]["status"] == "skipped"
    assert "disabled" in payload["tools"][0]["message"]
    assert "disabled" in payload["llm"]["message"]
    assert "secret" not in response.text


def test_diagnostics_validate_calls_helpers_when_opted_in(monkeypatch) -> None:
    called = {"tools": False, "llm": False}

    def fake_validate_external_tools(http_client):
        called["tools"] = True
        return [
            ToolValidationResult(
                tool_name="tavily_search",
                configured=True,
                ok=True,
                status_code=200,
                message="Tavily validation request succeeded.",
                sample_count=1,
            ),
            ToolValidationResult(
                tool_name="firecrawl_scrape",
                configured=True,
                ok=True,
                status_code=200,
                message="Firecrawl validation request succeeded.",
                sample_count=1,
            ),
        ]

    def fake_complete_json(prompt, schema, system_prompt=None):
        called["llm"] = True
        return schema(name="ok")

    monkeypatch.setattr(routes_diagnostics.settings, "run_real_tool_tests", True)
    monkeypatch.setattr(routes_diagnostics.settings, "run_real_llm_tests", True)
    monkeypatch.setattr(routes_diagnostics.settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_api_key", "secret-llm")
    monkeypatch.setattr(routes_diagnostics, "validate_external_tools", fake_validate_external_tools)
    monkeypatch.setattr(routes_diagnostics, "complete_json", fake_complete_json)
    client = TestClient(app)

    response = client.post("/api/diagnostics/validate")
    payload = response.json()

    assert response.status_code == 200
    assert called == {"tools": True, "llm": True}
    assert [result["ok"] for result in payload["tools"]] == [True, True]
    assert [result["status"] for result in payload["tools"]] == ["passed", "passed"]
    assert payload["llm"]["ok"] is True
    assert payload["llm"]["status"] == "passed"
    assert "secret-llm" not in response.text


def test_diagnostics_validate_sanitizes_llm_exception(monkeypatch) -> None:
    def raise_secret_error(prompt, schema, system_prompt=None):
        raise RuntimeError("secret-llm failed")

    monkeypatch.setattr(routes_diagnostics.settings, "run_real_tool_tests", False)
    monkeypatch.setattr(routes_diagnostics.settings, "run_real_llm_tests", True)
    monkeypatch.setattr(routes_diagnostics.settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(routes_diagnostics.settings, "llm_api_key", "secret-llm")
    monkeypatch.setattr(routes_diagnostics, "complete_json", raise_secret_error)
    client = TestClient(app)

    response = client.post("/api/diagnostics/validate")
    payload = response.json()

    assert response.status_code == 200
    assert payload["llm"]["ok"] is False
    assert payload["llm"]["status"] == "failed"
    assert "RuntimeError" in payload["llm"]["message"]
    assert "secret-llm" not in response.text
