#!/usr/bin/env bash
# One-time setup: create virtual environment and install yt-slides package.
# Idempotent — safe to run multiple times.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJ_DIR/.venv"

echo "=== youtube-to-slides setup ==="
echo "Project directory: $PROJ_DIR"

# Step 1: Find a suitable Python (3.9+)
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ] 2>/dev/null; then
            PYTHON="$candidate"
            echo "Found Python $version at $(command -v "$candidate")"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.9+ is required but not found."
    echo "Install Python from https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    "$PYTHON" -m venv "$VENV_DIR"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists at $VENV_DIR."
fi

# Step 3: Install the package in editable mode
echo "Installing yt-slides package..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e "$PROJ_DIR"
echo "Package installed."

# Step 4: Verify installation
if "$VENV_DIR/bin/python" -c "import yt_slides" 2>/dev/null; then
    echo "Verification passed: yt_slides is importable."
else
    echo "ERROR: Installation completed but yt_slides cannot be imported."
    exit 1
fi

if [ -f "$VENV_DIR/bin/yt-slides" ]; then
    echo "Verification passed: yt-slides CLI is available."
else
    echo "ERROR: yt-slides CLI binary not found."
    exit 1
fi

# Step 5: Check for .env file
if [ ! -f "$PROJ_DIR/.env" ]; then
    echo ""
    echo "WARNING: No .env file found."
    if [ -f "$PROJ_DIR/.env.example" ]; then
        echo "Copy the example and fill in your API keys:"
        echo "  cp $PROJ_DIR/.env.example $PROJ_DIR/.env"
    else
        echo "Create a .env file in $PROJ_DIR with:"
        echo "  GEMINI_API_KEY=your_key_here"
        echo "  YOUTUBE_API_KEY=your_key_here"
    fi
fi

echo ""
echo "=== Setup complete ==="
