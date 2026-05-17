#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ ! -f ".env" ]]; then
  cp .env.example .env
fi

python - <<'PY'
from pathlib import Path
import secrets

env_file = Path(".env")
lines = env_file.read_text().splitlines()
secret_line_idx = None

for i, line in enumerate(lines):
    if line.startswith("SECRET_KEY="):
        secret_line_idx = i
        break

new_secret = f"SECRET_KEY={secrets.token_hex(32)}"
if secret_line_idx is None:
    lines.append(new_secret)
elif not lines[secret_line_idx].split("=", 1)[1].strip():
    lines[secret_line_idx] = new_secret

env_file.write_text("\n".join(lines).rstrip() + "\n")
PY

python setup_db.py --username CARE-E_ADMIN --password CARE-E-2026

echo "Offline setup complete."
echo "Admin username: CARE-E_ADMIN"
echo "Admin password: CARE-E-2026"
echo "Run the app with: source venv/bin/activate && python run.py"
