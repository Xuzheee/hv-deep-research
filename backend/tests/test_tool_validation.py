import httpx

from app.agent.tools import validation


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "request failed",
                request=httpx.Request("POST", "https://example.test"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> dict:
        return self.payload


class FakeHttpClient:
    def __init__(self, response: FakeResponse | Exception) -> None:
        self.response = response
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_validate_tavily_connection_reports_missing_key(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "tavily_api_key", "")
    fake_client = FakeHttpClient(FakeResponse({"results": []}))

    result = validation.validate_tavily_connection(fake_client)

    assert result.tool_name == "tavily_search"
    assert result.configured is False
    assert result.ok is False
    assert fake_client.calls == []


def test_validate_tavily_connection_reports_success(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "tavily_api_key", "test-key")
    monkeypatch.setattr(validation.settings, "external_tool_validation_timeout_seconds", 7)
    fake_client = FakeHttpClient(FakeResponse({"results": [{"url": "https://example.com"}]}))

    result = validation.validate_tavily_connection(fake_client, query="GPT-4o")

    assert result.configured is True
    assert result.ok is True
    assert result.status_code == 200
    assert result.sample_count == 1
    assert fake_client.calls[0]["json"]["api_key"] == "test-key"
    assert fake_client.calls[0]["timeout"] == 7


def test_validate_tavily_connection_reports_timeout_without_leaking_key(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "tavily_api_key", "secret-key")
    fake_client = FakeHttpClient(httpx.TimeoutException("secret-key timed out"))

    result = validation.validate_tavily_connection(fake_client)

    assert result.configured is True
    assert result.ok is False
    assert "TimeoutException" in result.message
    assert "secret-key" not in result.message


def test_validate_firecrawl_connection_reports_missing_key(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "firecrawl_api_key", "")
    fake_client = FakeHttpClient(FakeResponse({"data": {"markdown": "ok"}}))

    result = validation.validate_firecrawl_connection(fake_client)

    assert result.tool_name == "firecrawl_scrape"
    assert result.configured is False
    assert result.ok is False
    assert fake_client.calls == []


def test_validate_firecrawl_connection_reports_success(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "firecrawl_api_key", "test-key")
    fake_client = FakeHttpClient(FakeResponse({"data": {"markdown": "# Example"}}))

    result = validation.validate_firecrawl_connection(fake_client, url="https://example.com")

    assert result.configured is True
    assert result.ok is True
    assert result.status_code == 200
    assert result.sample_count == 1
    assert fake_client.calls[0]["headers"]["Authorization"] == "Bearer test-key"


def test_validate_firecrawl_connection_reports_http_error(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "firecrawl_api_key", "secret-key")
    fake_client = FakeHttpClient(FakeResponse({"error": "bad secret-key"}, status_code=401))

    result = validation.validate_firecrawl_connection(fake_client)

    assert result.configured is True
    assert result.ok is False
    assert result.status_code == 401
    assert "HTTPStatusError" in result.message
    assert "secret-key" not in result.message


def test_validate_external_tools_returns_both_results(monkeypatch) -> None:
    monkeypatch.setattr(validation.settings, "tavily_api_key", "")
    monkeypatch.setattr(validation.settings, "firecrawl_api_key", "")

    results = validation.validate_external_tools(FakeHttpClient(FakeResponse({})))

    assert [result.tool_name for result in results] == ["tavily_search", "firecrawl_scrape"]
