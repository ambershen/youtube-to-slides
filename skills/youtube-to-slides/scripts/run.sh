#!/usr/bin/env bash
# Wrapper: activates virtual environment and runs yt-slides CLI.
# All arguments are forwarded to the yt-slides command.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../.." && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

if [ ! -f "$VENV_DIR/bin/yt-slides" ]; then
    echo "ERROR: yt-slides not found. Run setup.sh first."
    exit 1
fi

# Load API keys from skill directory's .env
set -a
[ -f "$SKILL_DIR/.env" ] && . "$SKILL_DIR/.env"
set +a

# Pass explicit output path so slides always land in the repo root output/
exec "$VENV_DIR/bin/yt-slides" --output "$REPO_DIR/output" "$@"
