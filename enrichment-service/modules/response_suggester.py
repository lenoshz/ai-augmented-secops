"""Response suggestion module for playbook steps and EQL hunting queries."""

import json
from typing import Any

from models.alert import AlertPayload
from models.enrichment import AlertContext, ResponseStep, SuggestedResponse
from services.anthropic_client import AnthropicClient


class ResponseSuggester:
    """Generate top response actions and analyst-facing hunt guidance."""

    def __init__(self, anthropic_client: AnthropicClient) -> None:
        """Initialize suggester with Anthropic client dependency."""
        self.anthropic_client = anthropic_client

    async def suggest(self, alert: AlertPayload, context: AlertContext) -> SuggestedResponse:
        """Generate suggested response steps and EQL query from alert context."""
        system_prompt = (
            "Return JSON only: "
            "{steps:[{step,action,detail},{step,action,detail},{step,action,detail}],"
            "eql_query,escalate}. Ensure eql_query is valid Elastic Security 8.x EQL."
        )
        user_prompt = (
            f"Alert rule: {alert.rule_name}; action: {alert.event_action}; "
            f"criticality: {context.asset_criticality}; "
            f"ioc_matches: {context.ioc_matches}; similar_hits_7d: {context.similar_hits_7d}"
        )
        raw = await self.anthropic_client.complete(system_prompt, user_prompt, max_tokens=512)
        suggested = self._parse_suggestion(raw)

        must_escalate = context.asset_criticality.lower() == "critical" or bool(context.ioc_matches)
        suggested.escalate = bool(suggested.escalate or must_escalate)
        return suggested

    async def handle_analyst_chat(self, history: list[dict[str, Any]], alert_context: dict[str, Any]) -> str:
        """Handle multi-turn analyst chat with in-context alert enrichment details."""
        system_prompt = (
            "You are GenesisSOC analyst assistant. Use alert context to give concise, "
            f"actionable guidance. Alert context: {json.dumps(alert_context)}"
        )
        return await self.anthropic_client.complete_with_history(system_prompt, history)

    def _parse_suggestion(self, raw: str) -> SuggestedResponse:
        """Parse structured suggestion output with safe fallback defaults."""
        default = SuggestedResponse(
            steps=[
                ResponseStep(step=1, action="Contain host", detail="Isolate the endpoint from the network."),
                ResponseStep(step=2, action="Collect evidence", detail="Acquire volatile and process telemetry."),
                ResponseStep(step=3, action="Hunt related", detail="Run environment-wide hunt for linked indicators."),
            ],
            eql_query='process where process.name == "powershell.exe"',
            escalate=False,
        )

        try:
            parsed = json.loads(raw)
            steps = [ResponseStep(**item) for item in parsed.get("steps", [])[:3]]
            if len(steps) < 3:
                steps = default.steps
            eql_query = str(parsed.get("eql_query", default.eql_query))
            escalate = bool(parsed.get("escalate", False))
            return SuggestedResponse(steps=steps, eql_query=eql_query, escalate=escalate)
        except (json.JSONDecodeError, TypeError, ValueError):
            return default
