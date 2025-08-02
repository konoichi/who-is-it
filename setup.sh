#!/bin/bash
# setup.sh
# Version: v1.0
# Beschreibung: Erstellt venv, installiert Abhängigkeiten

set -e

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup abgeschlossen. Starte mit: source .venv/bin/activate && python gradio_ui.py"
