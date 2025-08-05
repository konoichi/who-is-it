# CODE-ID: dockerfile_v2
#
# Bauplan für den "Who-Is-It" Container.
# Enthält jetzt den C++ Compiler, um dlib erfolgreich zu bauen.

# 1. Basis-Image: Ein schlankes Python-System
FROM python:3.9-slim

# 2. System-Abhängigkeiten installieren
# Wichtig: build-essential enthält den g++ Compiler, der für dlib benötigt wird.
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 3. Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# 4. Python-Abhängigkeiten installieren
# Erst die requirements.txt kopieren und installieren, um den Docker-Cache zu nutzen.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Den gesamten App-Code in den Container kopieren
COPY . .

# Der Startbefehl (CMD) wird in der docker-compose.yml-Datei definiert,
# da wir zwei verschiedene Befehle für unsere beiden Dienste benötigen.
