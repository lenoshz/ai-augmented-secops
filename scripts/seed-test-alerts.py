"""Seed sample alerts into Elasticsearch and invoke enrichment endpoint."""

import json
from pathlib import Path

import httpx

ELASTICSEARCH_URL = "http://localhost:9200"
ENRICHMENT_URL = "http://localhost:8000/api/v1/enrich"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "enrichment-service" / "tests" / "fixtures" / "sample_alerts.json"


def main() -> None:
    """Load fixture alerts, index them, and trigger enrichment sequentially."""
    alerts = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    with httpx.Client(timeout=30.0) as client:
        for alert in alerts:
            client.post(f"{ELASTICSEARCH_URL}/genesissoc-alerts/_doc", json=alert).raise_for_status()
            client.post(ENRICHMENT_URL, json=alert).raise_for_status()

    print(f"Seeded and enriched {len(alerts)} alerts.")


if __name__ == "__main__":
    main()
