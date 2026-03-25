"""Tests for GenesisSOC context enricher and response suggester modules."""

import asyncio

from models.alert import AlertPayload
from models.enrichment import AlertContext, MitreMapping
from modules.context_enricher import ContextEnricher
from modules.response_suggester import ResponseSuggester
from services.mitre_client import MitreClient


class FakeAnthropicClient:
    """Fake Anthropic client returning fixed JSON strings."""

    async def complete(self, system: str, user: str, max_tokens: int = 512) -> str:
        """Return deterministic JSON payloads by prompt intent."""
        if "tactic" in system:
            return '{"tactic":"Execution","technique_id":"T1059.001","technique_name":"PowerShell"}'
        return '{"steps":[{"step":1,"action":"Contain","detail":"Isolate host"},{"step":2,"action":"Investigate","detail":"Review process tree"},{"step":3,"action":"Hunt","detail":"Search similar indicators"}],"eql_query":"process where process.name == \"powershell.exe\"","escalate":false}'

    async def complete_with_history(self, system, history):
        """Return deterministic chat answer in tests."""
        return "Use host isolation first."


class FakeElasticClient:
    """Fake Elasticsearch client for controlled enrichment outputs."""

    async def get_asset_criticality(self, host_name: str) -> str:
        """Return criticality by host name mapping."""
        return "critical" if host_name == "dc-01" else "medium"

    async def count_similar_hits(self, rule_id: str) -> int:
        """Return static historical hit count."""
        return 4


class FakeThreatIntelClient:
    """Fake threat intel client returning IOC matches for one test IP."""

    async def lookup_ip(self, ip_address: str) -> list[str]:
        """Return IOC indicators when matching malicious test IP."""
        return ["AbuseIPDB score 90"] if ip_address == "8.8.8.8" else []


def test_context_enricher_returns_expected_context() -> None:
    """Validate context enricher combines MITRE, criticality, IOC, and hit count."""
    enricher = ContextEnricher(
        anthropic_client=FakeAnthropicClient(),
        elastic_client=FakeElasticClient(),
        mitre_client=MitreClient(),
        threat_intel_client=FakeThreatIntelClient(),
    )
    payload = AlertPayload(alert_id="a1", rule_id="r1", host_name="dc-01", destination_ip="8.8.8.8")
    context = asyncio.run(enricher.enrich(payload))

    assert isinstance(context, AlertContext)
    assert isinstance(context.mitre, MitreMapping)
    assert context.asset_criticality == "critical"
    assert context.ioc_matches
    assert context.similar_hits_7d == 4


def test_response_suggester_enforces_escalation_logic() -> None:
    """Ensure escalation is forced when critical asset or IOC hits exist."""
    suggester = ResponseSuggester(FakeAnthropicClient())
    payload = AlertPayload(alert_id="a2", rule_name="test")
    context = AlertContext(
        mitre=MitreMapping(tactic="Execution", technique_id="T1059", technique_name="Command and Scripting Interpreter"),
        asset_criticality="critical",
        ioc_matches=[],
        similar_hits_7d=0,
    )
    response = asyncio.run(suggester.suggest(payload, context))

    assert response.escalate is True
    assert len(response.steps) == 3
    assert "process where" in response.eql_query
