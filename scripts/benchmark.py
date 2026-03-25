"""Benchmark enrichment API latency and estimate token-related payload sizes."""

import json
import statistics
import time
from pathlib import Path

import httpx

ENRICHMENT_URL = "http://localhost:8000/api/v1/enrich"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "enrichment-service" / "tests" / "fixtures" / "sample_alerts.json"


def _percentile(values: list[float], percentile: float) -> float:
    """Compute percentile using nearest-rank approximation."""
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(round((percentile / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def main() -> None:
    """Run 50 enrichment calls and print latency and approximate token metrics."""
    alerts = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    latencies_ms: list[float] = []
    token_counts: list[int] = []

    with httpx.Client(timeout=60.0) as client:
        for i in range(50):
            alert = alerts[i % len(alerts)]
            started = time.perf_counter()
            response = client.post(ENRICHMENT_URL, json=alert)
            elapsed_ms = (time.perf_counter() - started) * 1000
            response.raise_for_status()
            payload = response.json()

            latencies_ms.append(elapsed_ms)
            token_counts.append(len(json.dumps(payload)) // 4)

    print(f"runs=50 mean_ms={statistics.mean(latencies_ms):.2f} p95_ms={_percentile(latencies_ms, 95):.2f} p99_ms={_percentile(latencies_ms, 99):.2f}")
    print(
        "token_estimate_approx "
        f"mean={statistics.mean(token_counts):.2f} "
        f"p95={_percentile(token_counts, 95):.2f} "
        f"p99={_percentile(token_counts, 99):.2f} "
        "(derived from response JSON bytes/4)"
    )


if __name__ == "__main__":
    main()
