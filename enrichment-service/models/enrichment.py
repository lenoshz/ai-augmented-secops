"""Enrichment output models for GenesisSOC responses."""

from pydantic import BaseModel, Field


class MitreMapping(BaseModel):
    """MITRE ATT&CK tactic and technique mapping for an alert."""

    tactic: str = "Unknown"
    technique_id: str = "T0000"
    technique_name: str = "Unknown Technique"


class AlertContext(BaseModel):
    """Computed context attributes used for analyst decision support."""

    mitre: MitreMapping
    asset_criticality: str = Field(default="unknown")
    ioc_matches: list[str] = Field(default_factory=list)
    similar_hits_7d: int = Field(default=0)


class ResponseStep(BaseModel):
    """Single playbook step suggested by the AI module."""

    step: int
    action: str
    detail: str


class SuggestedResponse(BaseModel):
    """Suggested response package with steps, query, and escalation signal."""

    steps: list[ResponseStep]
    eql_query: str
    escalate: bool


class EnrichedAlert(BaseModel):
    """Complete enriched alert record returned by the API."""

    alert_id: str
    narrative: str
    context: AlertContext
    response: SuggestedResponse
