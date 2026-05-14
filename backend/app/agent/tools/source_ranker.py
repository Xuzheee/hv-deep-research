import re
from datetime import UTC, datetime
from urllib.parse import urlparse

from app.agent.schemas.source import CandidateSource, Freshness, SourceTier

TIER_DOMAIN_MAP: dict[SourceTier, set[str]] = {
    "tier_1_primary": {
        "openai.com",
        "cursor.com",
        "api-docs.deepseek.com",
        "docs.tavily.com",
        "docs.firecrawl.dev",
        "github.com",
    },
    "tier_2_authoritative_secondary": {
        "arxiv.org",
        "huggingface.co",
        "semianalysis.com",
        "techcrunch.com",
    },
    "tier_3_community_signal": {
        "news.ycombinator.com",
        "reddit.com",
        "x.com",
    },
    "unknown": set(),
}

TIER_SCORES: dict[SourceTier, float] = {
    "tier_1_primary": 3.0,
    "tier_2_authoritative_secondary": 2.0,
    "tier_3_community_signal": 1.0,
    "unknown": 0.5,
}

FRESHNESS_SCORES: dict[Freshness, float] = {
    "current": 1.0,
    "recent": 0.5,
    "outdated": 0.0,
    "unknown": 0.2,
}

DOMAIN_BONUSES = {
    "arxiv.org": 0.5,
    "github.com": 0.3,
    "huggingface.co": 0.3,
}

BLOCKED_DOMAINS = {"coupon.example.com", "promo.example.com"}
LOW_QUALITY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"/coupon",
        r"/promo",
        r"/discount",
        r"/affiliate",
        r"best-\w+-alternatives",
        r"top-\d+-tools",
        r"vs\.html$",
    ]
]
LOW_QUALITY_TITLE_KEYWORDS = [
    "sponsored",
    "advertisement",
    "affiliate",
    "best deals",
    "discount code",
]


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return domain.removeprefix("www.")


def source_tier_for_domain(domain: str) -> SourceTier:
    normalized = domain.removeprefix("www.")
    for tier, domains in TIER_DOMAIN_MAP.items():
        if any(normalized == trusted or normalized.endswith(f".{trusted}") for trusted in domains):
            return tier
    return "unknown"


def freshness_from_date(published_at: str | None, now: datetime | None = None) -> Freshness:
    if not published_at:
        return "unknown"
    reference = now or datetime.now(UTC)
    try:
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    age_days = (reference - published).days
    if age_days <= 92:
        return "current"
    if age_days <= 365:
        return "recent"
    return "outdated"


def score_source(domain: str, source_tier: SourceTier, freshness: Freshness) -> float:
    normalized = domain.removeprefix("www.")
    bonus = next(
        (value for bonus_domain, value in DOMAIN_BONUSES.items() if normalized.endswith(bonus_domain)),
        0.0,
    )
    return min(5.0, TIER_SCORES[source_tier] + FRESHNESS_SCORES[freshness] + bonus)


def is_blocked(url: str) -> bool:
    domain = extract_domain(url)
    return domain in BLOCKED_DOMAINS or any(pattern.search(url) for pattern in LOW_QUALITY_PATTERNS)


def is_low_quality(url: str, title: str) -> bool:
    lowered_title = title.lower()
    return is_blocked(url) or any(keyword in lowered_title for keyword in LOW_QUALITY_TITLE_KEYWORDS)


def rank_candidate_sources(sources: list[CandidateSource]) -> list[CandidateSource]:
    filtered: list[CandidateSource] = []
    seen_urls: set[str] = set()
    domain_counts: dict[str, int] = {}

    for source in sources:
        if source.url in seen_urls:
            continue
        seen_urls.add(source.url)
        if is_low_quality(source.url, source.title):
            continue
        domain = source.source_domain or extract_domain(source.url)
        if domain_counts.get(domain, 0) >= 3:
            continue
        tier = source_tier_for_domain(domain)
        source.source_domain = domain
        source.source_tier = tier
        source.source_score = score_source(domain, tier, source.freshness)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        filtered.append(source)

    return sorted(filtered, key=lambda source: source.source_score, reverse=True)
