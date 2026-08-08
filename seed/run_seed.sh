#!/usr/bin/env bash
# Populate dummy data into Postgres OLTP DB.
# Tables must already exist (created via docker-entrypoint-initdb.d/ddl.sql
# when the postgres container first starts).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

export POSTGRES_HOST="localhost"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_DB="${POSTGRES_DB:-parkee_oltp}"
export POSTGRES_USER="${POSTGRES_USER:-parkee}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-parkee}"

VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install -q -r "$SCRIPT_DIR/requirements.txt"

python "$SCRIPT_DIR/seed_data.py"
