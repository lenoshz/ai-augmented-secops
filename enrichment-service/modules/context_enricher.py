"""Context enrichment module for MITRE, asset criticality, and IOC data."""

import json

from models.alert import AlertPayload
from models.enrichment import AlertContext, MitreMapping
from services.anthropic_client import AnthropicClient
from services.elastic_client import ElasticClient
from services.mitre_client import MitreClient
from services.threat_intel_client import ThreatIntelClient


class ContextEnricher:
    """Build contextual enrichment signals used for analyst decisioning."""

    def __init__(
        self,
        anthropic_client: AnthropicClient,
        elastic_client: ElasticClient,
        mitre_client: MitreClient,
        threat_intel_client: ThreatIntelClient,
    ) -> None:
        """Initialize enricher dependencies for external lookups."""
        self.anthropic_client = anthropic_client
        self.elastic_client = elastic_client
        self.mitre_client = mitre_client
        self.threat_intel_client = threat_intel_client

    async def enrich(self, alert: AlertPayload) -> AlertContext:
        """Return contextual enrichment for the provided alert payload."""
        system_prompt = (
            "Return JSON only with keys tactic, technique_id, technique_name. "
            "Map the described behavior to MITRE ATT&CK."
        )
        user_prompt = (
            f"Rule: {alert.rule_name}; Action: {alert.event_action}; "
            f"Process: {alert.process_name}; Severity: {alert.severity}"
        )

        mitre_json = await self.anthropic_client.complete(system_prompt, user_prompt, max_tokens=256)
        mitre_mapping = self._parse_mitre_mapping(mitre_json, user_prompt)

        asset_criticality = await self.elastic_client.get_asset_criticality(alert.host_name)
        ioc_matches = await self.threat_intel_client.lookup_ip(alert.destination_ip)
        similar_hits_7d = await self.elastic_client.count_similar_hits(alert.rule_id)

        return AlertContext(
            mitre=mitre_mapping,
            asset_criticality=asset_criticality,
            ioc_matches=ioc_matches,
            similar_hits_7d=similar_hits_7d,
        )

    def _parse_mitre_mapping(self, content: str, fallback_text: str) -> MitreMapping:
        """Parse LLM JSON output with a deterministic fallback mapping."""
        try:
            parsed = json.loads(content)
            return MitreMapping(
                tactic=str(parsed.get("tactic", "Unknown")),
                technique_id=str(parsed.get("technique_id", "T0000")),
                technique_name=str(parsed.get("technique_name", "Unknown Technique")),
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            tactic, technique_id, technique_name = self.mitre_client.map_from_text(fallback_text)
            return MitreMapping(tactic=tactic, technique_id=technique_id, technique_name=technique_name)
