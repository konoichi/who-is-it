# Gesichtserkennung MVP (v1.1)

## ✨ Ziel

Dieses Projekt bietet eine einfache, lokal gehostete Gesichtserkennung mit zwei Frontends:

- **FastAPI** für automatisierte Zugriffe / API-Nutzer
- **Gradio** für schnelle Tests per Webinterface

Läuft auch ohne GPU. Ideal für Homelabs.

---

## 🔧 Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### requirements.txt

```
fastapi
uvicorn
face_recognition
Pillow
numpy
gradio
loguru
```

---

## 🚀 Starten

### FastAPI (API)

```bash
uvicorn api:app --reload
```

Läuft auf: [http://localhost:8000](http://localhost:8000)

Dokumentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### Gradio (UI)

```bash
python gradio_ui.py
```

Läuft auf: [http://localhost:7860](http://localhost:7860)

---

## 📁 API-Endpunkte

### `POST /detect`

- Upload eines Bildes (multipart/form-data)
- Gibt erkannte Gesichter als JSON-Koordinaten zurück

### `GET /healthz`

- Check ob der Dienst läuft

### `GET /version`

- Gibt Version der API zurück

---

## ⚖️ Lizenz

MIT

---

## ⚠️ Hinweise

- Ohne GPU ist das Ganze nicht rasend schnell, aber stabil
- DSGVO: Keine Speicherung der Bilder
- Logs findest du unter: `logs/api.log`

---

## 🌐 Nächste Ausbaustufen (optional)

- Gesichtsvergleich / Identifikation
- Datenbank mit erkannten Personen
- Authentifizierung / Benutzerverwaltung
- Kamera-Feed Anbindung (z. B. RTSP)
- Dockerisierung
