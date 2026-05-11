from typing import Literal

from pydantic import BaseModel, Field

SourceTier = Literal[
    "tier_1_primary",
    "tier_2_authoritative_secondary",
    "tier_3_community_signal",
    "unknown",
]
Freshness = Literal["current", "recent", "outdated", "unknown"]
Dimension = Literal["vertical", "horizontal", "both", "supplementary"]
ConfidenceLevel = Literal["high", "medium", "low"]


class CandidateSource(BaseModel):
    source_id: str
    url: str
    title: str
    source_domain: str
    source_type: str
    source_tier: SourceTier
    source_score: float
    intended_dimension: Dimension
    snippet: str | None = None
    was_scraped: bool = False
    scrape_failed: bool = False
    retrieved_at: str
    freshness: Freshness = "unknown"
    notes: str | None = None


class CollectedNote(BaseModel):
    note_id: str
    query: str
    tool_name: Literal["tavily_search", "firecrawl_scrape"]
    title: str
    url: str
    source_domain: str
    snippet: str | None = None
    raw_markdown_excerpt: str | None = None
    intended_dimension: Dimension
    source_type_guess: str | None = None
    retrieved_at: str


class SelectedPassage(BaseModel):
    quote: str
    why_it_matters: str
    dimension: Literal["vertical", "horizontal", "both"]
    relevance_score: int = Field(ge=0, le=100)


class RelevanceSelectionResult(BaseModel):
    is_relevant: bool
    relevance_reason: str
    selected_passages: list[SelectedPassage]


class SourceItem(BaseModel):
    source_id: str
    title: str
    url: str
    source_domain: str
    source_type: str
    source_tier: SourceTier
    confidence: ConfidenceLevel
    freshness: Freshness
    was_scraped: bool = False
    retrieved_at: str
