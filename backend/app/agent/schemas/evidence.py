from typing import Literal

from pydantic import BaseModel, Field

from app.agent.schemas.source import ConfidenceLevel, Dimension, Freshness, SourceTier


class EvidenceCard(BaseModel):
    evidence_id: str
    claim: str
    evidence: str
    source_title: str
    url: str
    source_domain: str
    source_type: str
    source_tier: SourceTier
    source_score: float
    dimension: Dimension
    confidence: ConfidenceLevel
    relevance_score: int = Field(ge=0, le=100)
    freshness: Freshness
    supporting_quote: str | None = None
    retrieved_at: str
    notes: str | None = None


class EvidenceGroup(BaseModel):
    group_id: str
    label: str
    description: str
    source_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    dominant_tier: SourceTier
    confidence: ConfidenceLevel
    evidence_ids: list[str]


class KeyFinding(BaseModel):
    finding_id: str
    title: str
    content: str
    confidence: ConfidenceLevel
    supporting_evidence_ids: list[str]


class RiskNote(BaseModel):
    risk_id: str
    title: str
    content: str
    severity: Literal["high", "medium", "low"]
    supporting_evidence_ids: list[str]
