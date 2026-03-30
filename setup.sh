#!/usr/bin/env bash
# setup.sh — first-time local development setup
set -e

# 1. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --quiet -r requirements.txt

# 3. Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Generate a secure SECRET_KEY using the venv's Python interpreter
    SECRET_KEY=$(./venv/bin/python3 -c "import secrets; print(secrets.token_hex(32))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^SECRET_KEY=.*/SECRET_KEY=\"$SECRET_KEY\"/" .env
    else
        sed -i "s/^SECRET_KEY=.*/SECRET_KEY=\"$SECRET_KEY\"/" .env
    fi
    echo ".env created with a generated SECRET_KEY."
else
    echo ".env already exists — skipping."
fi

echo ""
echo "Setup complete. Run the application with:"
echo "  source venv/bin/activate && python3 run.py"
