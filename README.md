# 🧠 Who-Is-It v3.1 - Der smarte Workflow

## ✨ Ziel

Dieses Projekt ist ein lokal gehostetes Gesichtserkennungs-Tool mit einem intelligenten, kontextbasierten Workflow. Anstatt nur einzelne Befehle auszuführen, analysiert das System ein Bild und schlägt basierend auf dem Ergebnis die logischen nächsten Schritte vor. Es dient als smarter Assistent für die Verwaltung einer Gesichtsdatenbank.

---

## 🔧 Installation

### 1. Erstelle eine virtuelle Umgebung

```bash
python3 -m venv .venv
```

### 2. Aktiviere die Umgebung

```bash
source .venv/bin/activate
```

### 3. Installiere die Abhängigkeiten

```bash
pip install -r requirements.txt
```

**requirements.txt:**

```
fastapi
uvicorn
face_recognition
Pillow
numpy
gradio
```

---

## 🚀 Starten

Das Projekt wird mit einem einzigen Skript gestartet:

```bash
./runall.sh
```

Das Skript startet:

- **FastAPI (Backend)**: [http://localhost:8001](http://localhost:8001)
- **Gradio (Frontend)**: [http://localhost:7001](http://localhost:7001)

Zum Beenden einfach `Strg+C` im Terminal drücken.

---

## 📁 Dateistruktur & Logik

- `api.py` – Das Herzstück der Logik. Eine FastAPI-App, die alle Anfragen verarbeitet.

- `gradio_ui.py` – Das Interface. Smartes Gradio-UI, das auf Analyseergebnisse reagiert.

- `face_handler.py` – Das Gehirn für alle Gesichtsoperationen:

  - Laden und Cachen von Embeddings
  - Hinzufügen neuer Personen/Bilder
  - Duplikatschutz via Hashvergleich
  - Identifikation in neuen Bildern

- `known_faces/` – Der Datenspeicher

  - `known_faces/{person_name}/` – Ordner pro Person

    - `*.png` – Zugehörige Bilder
    - `hashes.json` – Bild-Hashes zur Duplikatsprüfung

---

## 💡 Workflow

1. **Vorbereitung:** Mindestens ein Bild pro Person in `known_faces/{Name}/` ablegen
2. **Start:** `./runall.sh` ausführen ✔ Meldung: Personen wurden geladen
3. **UI öffnen:** [http://localhost:7001](http://localhost:7001)
4. **Bild hochladen:** Mit Gesicht(er)
5. **Analyse starten:** Klick auf 🔍 _Analysieren!_
6. **Kontext-Aktion:**

   - Wird **eine bekannte Person erkannt**, erscheint: „Dieses Bild zur Sammlung hinzufügen“
   - Wird **ein unbekanntes Gesicht erkannt**, erscheint: Namensfeld + „Diese Person registrieren“

---

## 🌐 API-Endpunkte (v2.1)

Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)

| Methode | Pfad               | Beschreibung                                               |
| ------- | ------------------ | ---------------------------------------------------------- |
| POST    | `/detect`          | Findet Gesichter im Bild, gibt Box-Koordinaten zurück      |
| POST    | `/identify`        | Erkennt bekannte Gesichter im Bild                         |
| POST    | `/register/{name}` | Bild einer (neuen) Person hinzufügen, mit Duplikatsprüfung |
| GET     | `/persons`         | Gibt Liste aller bekannten Personen zurück                 |
| DELETE  | `/person/{name}`   | Löscht eine Person inkl. aller Bilder                      |
| GET     | `/healthz`         | Health-Check                                               |

---

## ⚖️ Lizenz

MIT License
