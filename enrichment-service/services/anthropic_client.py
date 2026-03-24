"""Anthropic client wrapper for GenesisSOC AI modules."""

from typing import Any

from anthropic import AsyncAnthropic

from config import settings


class AnthropicClient:
    """Thin async wrapper around AsyncAnthropic completion APIs."""

    def __init__(self) -> None:
        """Initialize the Anthropic SDK client."""
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = "claude-opus-4-6"

    async def complete(self, system: str, user: str, max_tokens: int = 512) -> str:
        """Generate a single-turn completion using fixed model settings."""
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return self._extract_text(response.content)

    async def complete_with_history(self, system: str, history: list[dict[str, Any]]) -> str:
        """Generate a multi-turn completion using provided role/content history."""
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=512,
            system=system,
            messages=history,
        )
        return self._extract_text(response.content)

    @staticmethod
    def _extract_text(content: list[Any]) -> str:
        """Extract text from Anthropic content blocks."""
        text_parts = [block.text for block in content if hasattr(block, "text")]
        return "\n".join(text_parts).strip()
