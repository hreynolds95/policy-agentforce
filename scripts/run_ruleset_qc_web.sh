#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}"
  echo "Create it first with:"
  echo "  cp .env.example .env"
  echo
  echo "For the ruleset QC web UI, the required value is:"
  echo "  GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json"
  echo
  echo "Optional values:"
  echo "  ANTHROPIC_API_KEY=..."
  echo "  OPENAI_API_KEY=..."
  exit 1
fi

if [[ ! -d "${ROOT_DIR}/.venv" ]]; then
  echo "Missing virtual environment at ${ROOT_DIR}/.venv"
  echo "Create it first with:"
  echo "  python3 -m venv .venv"
  echo "  source .venv/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

source "${ROOT_DIR}/.venv/bin/activate"

echo "Starting ruleset QC web UI at http://127.0.0.1:8090"
cd "${ROOT_DIR}"
python3 scripts/ruleset_qc_web.py
