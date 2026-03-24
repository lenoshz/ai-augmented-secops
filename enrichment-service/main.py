"""FastAPI application entrypoint for GenesisSOC enrichment APIs."""

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from models.alert import AlertPayload
from models.enrichment import EnrichedAlert
from modules.context_enricher import ContextEnricher
from modules.response_suggester import ResponseSuggester
from modules.summariser import Summariser
from services.anthropic_client import AnthropicClient
from services.elastic_client import ElasticClient
from services.cache_client import CacheClient
from services.mitre_client import MitreClient
from services.threat_intel_client import ThreatIntelClient

app = FastAPI(title="GenesisSOC Enrichment Service", version="1.0.0")

anthropic_client = AnthropicClient()
elastic_client = ElasticClient()
cache_client = CacheClient()
mitre_client = MitreClient()
threat_intel_client = ThreatIntelClient()

summariser = Summariser(anthropic_client)
context_enricher = ContextEnricher(anthropic_client, elastic_client, mitre_client, threat_intel_client)
response_suggester = ResponseSuggester(anthropic_client)


class ChatPayload(BaseModel):
    """Request schema for analyst chat endpoint."""

    history: list[dict[str, Any]]
    alert_context: dict[str, Any]


class FeedbackPayload(BaseModel):
    """Request schema for analyst feedback endpoint."""

    alert_id: str
    rating: str
    analyst_id: str


@app.post("/api/v1/enrich", response_model=EnrichedAlert)
async def enrich_alert(payload: AlertPayload) -> EnrichedAlert:
    """Enrich an incoming alert and persist the result in Elasticsearch."""
    alert_id = payload.alert_id or payload.rule_id or "unknown-alert"
    cached = await cache_client.get_enriched_alert(alert_id)
    if cached is not None:
        return cached

    narrative = await summariser.summarise(payload)
    context = await context_enricher.enrich(payload)
    response = await response_suggester.suggest(payload, context)

    enriched = EnrichedAlert(
        alert_id=alert_id,
        narrative=narrative,
        context=context,
        response=response,
    )

    await elastic_client.index_enriched_alert(enriched.model_dump())
    await cache_client.set_enriched_alert(alert_id, enriched)
    return enriched


@app.post("/api/v1/chat")
async def analyst_chat(payload: ChatPayload) -> dict[str, str]:
    """Process analyst multi-turn chat using alert context."""
    answer = await response_suggester.handle_analyst_chat(payload.history, payload.alert_context)
    return {"response": answer}


@app.post("/api/v1/feedback")
async def feedback(payload: FeedbackPayload) -> dict[str, str]:
    """Store analyst feedback for enrichment quality loop."""
    await elastic_client.index_feedback(payload.model_dump())
    return {"status": "stored"}


@app.get("/api/v1/alerts/enriched")
async def list_enriched_alerts() -> list[dict[str, Any]]:
    """Return latest enriched alerts for Kibana plugin polling."""
    return await elastic_client.list_enriched_alerts()


@app.get("/health")
async def health() -> dict[str, str]:
    """Return health state and active model metadata."""
    return {"status": "ok", "model": "claude-opus-4-6"}
