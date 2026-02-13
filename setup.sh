#!/bin/bash
set -e

echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing crawl4ai and playwright..."
crawl4ai-setup
playwright install chromium

echo "Setup complete! Use 'source venv/bin/activate' to start."
