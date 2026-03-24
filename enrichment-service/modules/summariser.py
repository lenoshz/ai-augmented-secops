"""Alert summarization module for concise SOC analyst narratives."""

from models.alert import AlertPayload
from services.anthropic_client import AnthropicClient


class Summariser:
    """Generate plain-English alert narratives in exactly three sentences."""

    def __init__(self, anthropic_client: AnthropicClient) -> None:
        """Initialize summariser with Anthropic client dependency."""
        self.anthropic_client = anthropic_client

    async def summarise(self, alert: AlertPayload) -> str:
        """Summarize alert details into a strict three-sentence narrative."""
        system_prompt = (
            "You are a senior SOC analyst. Write exactly 3 sentences: "
            "(1) what happened, (2) why it is suspicious, (3) severity rationale. "
            "Never use raw ECS field names. Be decisive."
        )
        user_prompt = (
            f"Rule: {alert.rule_name}\n"
            f"Host: {alert.host_name}\n"
            f"User: {alert.user_name}\n"
            f"Action: {alert.event_action}\n"
            f"Source IP: {alert.source_ip}\n"
            f"Destination IP: {alert.destination_ip}\n"
            f"Process: {alert.process_name}\n"
            f"Severity: {alert.severity}"
        )
        return await self.anthropic_client.complete(system_prompt, user_prompt, max_tokens=256)
