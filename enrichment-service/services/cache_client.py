"""Redis cache client for GenesisSOC enrichment responses."""

import json

from redis.asyncio import Redis

from config import settings
from models.enrichment import EnrichedAlert


class CacheClient:
    """Async Redis cache helper for enriched alert payloads."""

    def __init__(self) -> None:
        """Initialize Redis connection with configured URL."""
        self.client = Redis.from_url(settings.redis_url, decode_responses=True)

    async def get_enriched_alert(self, alert_id: str) -> EnrichedAlert | None:
        """Fetch cached enriched alert by alert identifier when available."""
        if not alert_id:
            return None
        cached = await self.client.get(self._key(alert_id))
        if not cached:
            return None
        return EnrichedAlert.model_validate(json.loads(cached))

    async def set_enriched_alert(self, alert_id: str, payload: EnrichedAlert) -> None:
        """Cache enriched alert for configured TTL duration."""
        if not alert_id:
            return
        await self.client.set(
            self._key(alert_id),
            json.dumps(payload.model_dump()),
            ex=settings.cache_ttl_seconds,
        )

    @staticmethod
    def _key(alert_id: str) -> str:
        """Return stable Redis key name for alert enrichments."""
        return f"genesissoc:enriched:{alert_id}"
