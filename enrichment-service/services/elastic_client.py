"""Elasticsearch client helpers for enrichment workflows."""

from elasticsearch import AsyncElasticsearch

from config import settings


class ElasticClient:
    """Async helper for indexing and querying GenesisSOC alert data."""

    def __init__(self) -> None:
        """Initialize asynchronous Elasticsearch transport."""
        self.client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])

    async def index_enriched_alert(self, doc: dict) -> None:
        """Write enriched alert record to the genesissoc-enriched index."""
        await self.client.index(index="genesissoc-enriched", document=doc)

    async def index_feedback(self, doc: dict) -> None:
        """Write analyst feedback entry to the genesissoc-feedback index."""
        await self.client.index(index="genesissoc-feedback", document=doc)

    async def get_asset_criticality(self, host_name: str) -> str:
        """Lookup asset criticality from asset inventory index by host name."""
        if not host_name:
            return "unknown"
        query = {
            "size": 1,
            "query": {
                "term": {
                    "host.name.keyword": host_name,
                }
            },
        }
        result = await self.client.search(index="asset-inventory", body=query, ignore_unavailable=True)
        hits = result.get("hits", {}).get("hits", [])
        if not hits:
            return "unknown"
        source = hits[0].get("_source", {})
        return source.get("asset_criticality", "unknown")

    async def count_similar_hits(self, rule_id: str) -> int:
        """Count alerts matching the same rule id over the previous seven days."""
        if not rule_id:
            return 0
        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"rule_id.keyword": rule_id}},
                        {"range": {"@timestamp": {"gte": "now-7d"}}},
                    ]
                }
            }
        }
        result = await self.client.count(index="genesissoc-alerts", body=query, ignore_unavailable=True)
        return int(result.get("count", 0))

    async def list_enriched_alerts(self, size: int = 50) -> list[dict]:
        """Return the latest enriched alerts for UI polling endpoints."""
        query = {
            "size": size,
            "sort": [{"_id": {"order": "desc"}}],
            "query": {"match_all": {}},
        }
        result = await self.client.search(index="genesissoc-enriched", body=query, ignore_unavailable=True)
        hits = result.get("hits", {}).get("hits", [])
        return [hit.get("_source", {}) for hit in hits]
