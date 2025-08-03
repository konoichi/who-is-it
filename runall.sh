#!/bin/bash
# runall.sh
# Version: v2.0
# Beschreibung: Startet API und Gradio parallel und sorgt für ein sauberes Beenden.

# Funktion, die beim Beenden aufgerufen wird
cleanup() {
    echo "🚨 Stoppe alle Prozesse..."
    # Sende das TERM-Signal an die Prozess-IDs, die wir gespeichert haben
    kill $API_PID $GRADIO_PID
    # Warte kurz, damit die Prozesse sich beenden können
    wait $API_PID $GRADIO_PID 2>/dev/null
    echo "✅ Alle Prozesse beendet."
}

# Setze die "Falle": Wenn das Skript ein SIGINT (Strg+C) oder SIGTERM erhält,
# rufe die 'cleanup'-Funktion auf.
trap cleanup SIGINT SIGTERM

# Ports freimachen (optional, aber nützlich)
fuser -k 8001/tcp 2>/dev/null
fuser -k 7001/tcp 2>/dev/null

# Virtuelle Umgebung aktivieren
source .venv/bin/activate

# API im Hintergrund starten und die Prozess-ID (PID) speichern
echo "🚀 Starte FastAPI-Server..."
uvicorn api:app --host 0.0.0.0 --port 8001 --reload &
API_PID=$!
echo "✅ API gestartet (PID $API_PID) auf http://0.0.0.0:8001"

# Gradio im Hintergrund starten und die PID speichern
echo "🚀 Starte Gradio-UI..."
python gradio_ui.py &
GRADIO_PID=$!
echo "✅ Gradio gestartet (PID $GRADIO_PID) auf http://0.0.0.0:7001"

# Warte auf das Ende beider Prozesse.
# Das Skript pausiert hier, bis die Prozesse beendet werden (z.B. durch Strg+C).
wait $API_PID $GRADIO_PID

