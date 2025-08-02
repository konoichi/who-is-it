#!/bin/bash
# run.sh
# Version: v1.0
# Beschreibung: Aktiviert die virtuelle Umgebung und startet den FastAPI-Server

source .venv/bin/activate
uvicorn api:app --reload
