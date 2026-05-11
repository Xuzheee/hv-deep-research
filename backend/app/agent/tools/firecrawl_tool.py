from datetime import UTC, datetime
from uuid import uuid4

import httpx

from app.agent.schemas.source import CollectedNote, Dimension
from app.agent.tools.source_ranker import extract_domain
from app.config import settings

FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v2/scrape"
NOISE_PHRASES = (
    "just a moment",
    "checking your browser",
    "cloudflare",
    "enable javascript",
    "share this",
    "cookie",
    "subscribe",
)
NAV_LABELS = {"home", "pricing", "login", "log in", "sign up", "signup"}



def _clean_markdown_excerpt(markdown: str, max_chars: int = 4000) -> str:
    cleaned_lines = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if lowered in NAV_LABELS:
            continue
        if any(phrase in lowered for phrase in NOISE_PHRASES):
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)[:max_chars]


def scrape_firecrawl(url: str, query: str, intended_dimension: Dimension = "both") -> CollectedNote:
    if not settings.firecrawl_api_key:
        return mock_firecrawl_note(url, query, intended_dimension)

    response = httpx.post(
        FIRECRAWL_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.firecrawl_api_key}"},
        json={"url": url, "formats": ["markdown"]},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json().get("data", response.json())
    metadata = payload.get("metadata", {})
    return CollectedNote(
        note_id=f"note_{uuid4().hex}",
        query=query,
        tool_name="firecrawl_scrape",
        title=metadata.get("title") or url,
        url=url,
        source_domain=extract_domain(url),
        snippet=metadata.get("description"),
        raw_markdown_excerpt=_clean_markdown_excerpt(payload.get("markdown") or ""),
        intended_dimension=intended_dimension,
        source_type_guess=metadata.get("sourceType"),
        retrieved_at=datetime.now(UTC).isoformat(),
    )


def mock_firecrawl_note(url: str, query: str, intended_dimension: Dimension = "both") -> CollectedNote:
    domain = extract_domain(url)
    return CollectedNote(
        note_id="note_mock_scrape",
        query=query,
        tool_name="firecrawl_scrape",
        title=f"Mock scraped page for {query}",
        url=url,
        source_domain=domain,
        snippet=f"Mock scrape summary for {query} from {domain}.",
        raw_markdown_excerpt=(
            f"# Mock source for {query}\n\n"
            f"This deterministic mock content represents scraped evidence from {domain}. "
            "It is used when FIRECRAWL_API_KEY is not configured."
        ),
        intended_dimension=intended_dimension,
        source_type_guess="mock_scrape",
        retrieved_at=datetime.now(UTC).isoformat(),
    )
