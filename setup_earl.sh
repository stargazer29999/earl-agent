#!/bin/bash
# setup_earl.sh - Mac Mini M4 Pro Setup Script for Earl Agent
# 
# This script sets up the local environment, checks dependencies,
# and prepares the Earl Agent OS for first run.

set -e

echo "============================================="
echo "   Earl Agent OS — Mac Mini Setup Script     "
echo "============================================="

# 1. Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "[!] Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "[✓] Homebrew is installed."
fi

# 2. Check for required system packages
echo "Checking system dependencies..."
PACKAGES="python@3.11 node ripgrep ffmpeg"
for pkg in $PACKAGES; do
    if ! brew list $pkg &> /dev/null; then
        echo "[!] Installing $pkg..."
        brew install $pkg
    else
        echo "[✓] $pkg is installed."
    fi
done

# 3. Check for uv (Python package manager)
if ! command -v uv &> /dev/null; then
    echo "[!] Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "[✓] uv is installed."
fi

# 4. Verify Local LLM (oMLX or Ollama)
echo "Checking local LLM server (http://localhost:8000/v1)..."
if curl -s http://localhost:8000/v1/models > /dev/null; then
    echo "[✓] Local LLM server detected at localhost:8000."
else
    echo "[!] WARNING: Local LLM server not detected at localhost:8000."
    echo "    Make sure oMLX / LM Studio is running before launching Earl Agent."
fi

# 5. Create Python Virtual Environment
echo "Setting up Python virtual environment..."
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e .

# 6. Create ~/.earl directory structure
echo "Initializing ~/.earl directory structure..."
mkdir -p ~/.earl/{memories,skills,plans,logs,cron,profiles/{sun-tzu,augustus,archimedes,aristotle,medici}}

# 7. Migrate from ~/.hermes if it exists
if [ -d ~/.hermes ] && [ ! -f ~/.earl/config.yaml ]; then
    echo "Found existing ~/.hermes setup. Migrating keys..."
    cp ~/.hermes/.env ~/.earl/.env 2>/dev/null || true
    echo "Migrated .env file."
fi

echo "============================================="
echo "Setup Complete!"
echo "To start the agent, run:"
echo "  source .venv/bin/activate"
echo "  earl chat"
echo "============================================="
