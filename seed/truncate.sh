#!/usr/bin/env bash
# Truncate all OLTP tables in Postgres and reset identity, so seed_data.py
# can be re-run from a clean state. Runs via `docker exec` into the
# postgres container, no local psql client required.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

CONTAINER="${POSTGRES_CONTAINER:-parkee_postgres}"

docker exec -i "$CONTAINER" psql \
  -U "${POSTGRES_USER:-parkee}" \
  -d "${POSTGRES_DB:-parkee_oltp}" \
  -c "TRUNCATE TABLE transaction_items, transactions, products, customers RESTART IDENTITY CASCADE;"

echo "Postgres OLTP tables truncated. Run seed/run_seed.sh to reseed."
