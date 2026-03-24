#!/usr/bin/env bash
set -euo pipefail

ELASTICSEARCH_URL="${ELASTICSEARCH_URL:-http://localhost:9200}"
KIBANA_URL="${KIBANA_URL:-http://localhost:5601}"
ELASTIC_PASSWORD="${ELASTIC_PASSWORD:-}"

AUTH_ARGS=()
if [[ -n "${ELASTIC_PASSWORD}" ]]; then
  AUTH_ARGS=(-u "elastic:${ELASTIC_PASSWORD}")
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating genesissoc-alerts index template..."
curl -sS "${AUTH_ARGS[@]}" -X PUT "${ELASTICSEARCH_URL}/_index_template/genesissoc-alerts-template" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["genesissoc-alerts*"],
    "template": {
      "settings": {"number_of_shards": 1},
      "mappings": {"dynamic": true}
    }
  }' >/dev/null

echo "Creating genesissoc-enriched index template..."
curl -sS "${AUTH_ARGS[@]}" -X PUT "${ELASTICSEARCH_URL}/_index_template/genesissoc-enriched-template" \
  -H "Content-Type: application/json" \
  -d '{
    "index_patterns": ["genesissoc-enriched*"],
    "template": {
      "settings": {"number_of_shards": 1},
      "mappings": {"dynamic": true}
    }
  }' >/dev/null

if [[ -f "${SCRIPT_DIR}/detection-rules.ndjson" ]]; then
  echo "Importing detection rules from detection-rules.ndjson..."
  curl -sS "${AUTH_ARGS[@]}" -X POST "${KIBANA_URL}/api/detection_engine/rules/_import?overwrite=true" \
    -H "kbn-xsrf: true" \
    -F "file=@${SCRIPT_DIR}/detection-rules.ndjson" >/dev/null
else
  echo "Skipping rules import: detection-rules.ndjson not found in ${SCRIPT_DIR}."
fi

echo "Installing GenesisSOC watcher..."
curl -sS "${AUTH_ARGS[@]}" -X PUT "${ELASTICSEARCH_URL}/_watcher/watch/genesissoc-alert-trigger" \
  -H "Content-Type: application/json" \
  -d @"${SCRIPT_DIR}/watcher-trigger.json" >/dev/null

echo "Bootstrap complete."
