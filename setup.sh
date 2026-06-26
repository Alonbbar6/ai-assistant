#!/bin/bash
# One-time setup script

set -e

echo "=== Personal AI Assistant Setup ==="

# 1. Create virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Created .venv"
fi
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip -q
pip install -r requirements.txt

# 3. Copy .env if not present
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "Created .env — open it and add your ANTHROPIC_API_KEY"
fi

# 4. Create credentials dir
mkdir -p credentials

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env and set ANTHROPIC_API_KEY"
echo "  2. For Google Calendar/Gmail:"
echo "     - Go to https://console.cloud.google.com"
echo "     - Create a project, enable Calendar API + Gmail API"
echo "     - Create OAuth 2.0 Desktop credentials"
echo "     - Download JSON → save as credentials/google_credentials.json"
echo "  3. Run: source .venv/bin/activate && python main.py"
