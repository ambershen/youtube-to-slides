#!/usr/bin/env bash
# Wrapper: activates virtual environment and runs yt-slides CLI.
# All arguments are forwarded to the yt-slides command.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJ_DIR/.venv"

if [ ! -f "$VENV_DIR/bin/yt-slides" ]; then
    echo "ERROR: yt-slides not found. Run setup.sh first."
    exit 1
fi

# Change to project root so .env is picked up by python-dotenv
cd "$PROJ_DIR"

exec "$VENV_DIR/bin/yt-slides" "$@"
