"""Tests for GenesisSOC summariser module behavior."""

import asyncio

from models.alert import AlertPayload
from modules.summariser import Summariser


class FakeAnthropicClient:
    """Simple fake client to assert summariser invocation behavior."""

    async def complete(self, system: str, user: str, max_tokens: int = 512) -> str:
        """Return deterministic three-sentence summary for tests."""
        return "A suspicious script executed on a user endpoint. The execution path aligns with known malicious staging behavior. The alert is high severity due to elevated compromise risk."


def test_summariser_returns_three_sentence_narrative() -> None:
    """Ensure summariser returns a concise narrative string."""
    summariser = Summariser(FakeAnthropicClient())
    payload = AlertPayload(alert_id="1", rule_name="Rule", host_name="host", severity="high")
    result = asyncio.run(summariser.summarise(payload))
    assert isinstance(result, str)
    assert result.count(".") >= 3
