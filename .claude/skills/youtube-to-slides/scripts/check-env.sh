#!/usr/bin/env bash
# Pre-flight check: validate virtual environment, package installation, and API keys.
# Exit 0 if everything is ready, exit 1 with diagnostics if not.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
VENV_DIR="$PROJ_DIR/.venv"

errors=()

# Check 1: Virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    errors+=("Virtual environment not found at $VENV_DIR")
elif [ ! -f "$VENV_DIR/bin/python" ]; then
    errors+=("Virtual environment is missing python binary at $VENV_DIR/bin/python")
fi

# Check 2: yt-slides package is importable
if [ -f "$VENV_DIR/bin/python" ]; then
    if ! "$VENV_DIR/bin/python" -c "import yt_slides" 2>/dev/null; then
        errors+=("yt_slides package is not installed in the virtual environment. Run setup.sh.")
    fi
fi

# Check 3: yt-slides CLI is available
if [ -f "$VENV_DIR/bin/yt-slides" ]; then
    : # OK
else
    errors+=("yt-slides CLI not found at $VENV_DIR/bin/yt-slides")
fi

# Check 4: .env file exists with real API keys
ENV_FILE="$PROJ_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    errors+=("No .env file found at $ENV_FILE. Copy .env.example and fill in your API keys.")
else
    # Check GEMINI_API_KEY
    if grep -q "^GEMINI_API_KEY=" "$ENV_FILE"; then
        gemini_key=$(grep "^GEMINI_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)
        if [ -z "$gemini_key" ] || [ "$gemini_key" = "your_gemini_api_key_here" ]; then
            errors+=("GEMINI_API_KEY in .env is not set. Get one at https://aistudio.google.com/apikey")
        fi
    else
        errors+=("GEMINI_API_KEY not found in .env file.")
    fi

    # Check YOUTUBE_API_KEY
    if grep -q "^YOUTUBE_API_KEY=" "$ENV_FILE"; then
        yt_key=$(grep "^YOUTUBE_API_KEY=" "$ENV_FILE" | cut -d'=' -f2-)
        if [ -z "$yt_key" ] || [ "$yt_key" = "your_youtube_data_api_key_here" ]; then
            errors+=("YOUTUBE_API_KEY in .env is not set. Get one at https://console.cloud.google.com/apis/credentials")
        fi
    else
        errors+=("YOUTUBE_API_KEY not found in .env file.")
    fi
fi

# Report results
if [ ${#errors[@]} -eq 0 ]; then
    echo "All checks passed. Ready to run."
    exit 0
else
    echo "Pre-flight check failed with ${#errors[@]} issue(s):"
    for err in "${errors[@]}"; do
        echo "  - $err"
    done
    exit 1
fi
