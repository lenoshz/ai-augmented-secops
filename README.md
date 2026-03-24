# GenesisSOC

AI-augmented SecOps platform on top of Elastic Security.

## Quick Start

```bash
cp .env.example .env
docker compose up -d
./elastic/setup/bootstrap.sh
python scripts/seed-test-alerts.py
```

## Verify

```bash
curl http://localhost:8000/health
# {"status":"ok","model":"claude-opus-4-6"}

python scripts/benchmark.py
```
