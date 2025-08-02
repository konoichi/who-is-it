#!/bin/bash
# runall.sh
# Version: v1.0
# Beschreibung: Startet API und Gradio parallel in separaten Terminals

fuser -k 8001/tcp 2>/dev/null
fuser -k 7001/tcp 2>/dev/null

source .venv/bin/activate

# API in Hintergrund starten
uvicorn api:app --host 0.0.0.0 --port 8001 --reload &
API_PID=$!
echo "✅ API gestartet (PID $API_PID) auf http://0.0.0.0:8001"

# Gradio starten
python gradio_ui.py --server-name 0.0.0.0 --server-port 7001 &
GRADIO_PID=$!
echo "✅ Gradio gestartet (PID $GRADIO_PID) auf http://0.0.0.0:7001"

# Warten auf Prozesse
wait $API_PID $GRADIO_PID
