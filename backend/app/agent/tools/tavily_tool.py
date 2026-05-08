from datetime import UTC, datetime
from uuid import uuid4

import httpx

from app.agent.schemas.source import CandidateSource, Dimension
from app.agent.tools.source_ranker import extract_domain, freshness_from_date, rank_candidate_sources, source_tier_for_domain
from app.config import settings

TAVILY_ENDPOINT = "https://api.tavily.com/search"


def search_tavily(query: str, intended_dimension: Dimension = "both", max_results: int = 5) -> list[CandidateSource]:
    if not settings.tavily_api_key:
        return mock_tavily_results(query, intended_dimension, max_results)

    response = httpx.post(
        TAVILY_ENDPOINT,
        json={"api_key": settings.tavily_api_key, "query": query, "max_results": max_results},
        timeout=20,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    return rank_candidate_sources(
        [candidate_from_tavily_result(result, query, intended_dimension) for result in results]
    )[:max_results]


def candidate_from_tavily_result(result: dict, query: str, intended_dimension: Dimension) -> CandidateSource:
    url = result.get("url", "")
    domain = extract_domain(url)
    freshness = freshness_from_date(result.get("published_date"))
    tier = source_tier_for_domain(domain)
    return CandidateSource(
        source_id=f"src_{uuid4().hex}",
        url=url,
        title=result.get("title") or query,
        source_domain=domain,
        source_type="search_result",
        source_tier=tier,
        source_score=0.0,
        intended_dimension=intended_dimension,
        snippet=result.get("content"),
        retrieved_at=datetime.now(UTC).isoformat(),
        freshness=freshness,
    )


def mock_tavily_results(query: str, intended_dimension: Dimension = "both", max_results: int = 5) -> list[CandidateSource]:
    now = datetime.now(UTC).isoformat()
    candidates = [
        CandidateSource(
            source_id="src_mock_official",
            url=f"https://openai.com/index/{query.replace(' ', '-').lower()}",
            title=f"Official information about {query}",
            source_domain="openai.com",
            source_type="official_blog",
            source_tier="unknown",
            source_score=0.0,
            intended_dimension=intended_dimension,
            snippet=f"Official launch and capability notes for {query}.",
            retrieved_at=now,
            freshness="current",
        ),
        CandidateSource(
            source_id="src_mock_github",
            url=f"https://github.com/search?q={query.replace(' ', '+')}",
            title=f"Developer references for {query}",
            source_domain="github.com",
            source_type="github_readme",
            source_tier="unknown",
            source_score=0.0,
            intended_dimension=intended_dimension,
            snippet=f"Repository and developer ecosystem signals for {query}.",
            retrieved_at=now,
            freshness="recent",
        ),
        CandidateSource(
            source_id="src_mock_hn",
            url=f"https://news.ycombinator.com/item?id={abs(hash(query)) % 100000}",
            title=f"Community discussion about {query}",
            source_domain="news.ycombinator.com",
            source_type="community_hn",
            source_tier="unknown",
            source_score=0.0,
            intended_dimension=intended_dimension,
            snippet=f"Community sentiment and adoption discussion for {query}.",
            retrieved_at=now,
            freshness="recent",
        ),
    ]
    return rank_candidate_sources(candidates)[:max_results]
