# CODE-ID: api_v2.5
"""
Modulname: api.py
Version: v2.5
Beschreibung: Stellt die Konsistenz über alle Endpunkte sicher. Kein Endpunkt
             gibt mehr eine leere Liste zurück.
Autor: kono
Erstellt am: 2025-08-03
Lizenz: MIT
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import List, Dict

# Importiere unsere Handler-Funktionen
from face_handler import (
    image_bytes_to_array,
    extract_face_locations,
    add_image_to_person,
    identify_faces_in_image,
    delete_person_data,
    list_persons,
    load_and_cache_known_faces
)

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)8s | %(message)s")
log = logging.getLogger("api")

# App initialisieren
app = FastAPI(title="Who-Is-It API", version="2.5")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Lädt beim Start der API alle bekannten Gesichter in den Cache."""
    log.info("Server startet... Lade bekannte Gesichter.")
    load_and_cache_known_faces()

@app.post("/detect", summary="Erkennt Gesichter in einem Bild")
async def detect(file: UploadFile = File(...)):
    """
    Lädt ein Bild hoch und gibt die Positionen der erkannten Gesichter zurück.
    Wenn kein Gesicht gefunden wird, gibt es eine explizite Nachricht zurück.
    """
    image_bytes = await file.read()
    image_array = image_bytes_to_array(image_bytes)
    faces = extract_face_locations(image_array)
    log.info(f"/detect: {len(faces)} Gesicht(er) in {file.filename} gefunden.")

    if not faces:
        return {"faces": "none"}
        
    return {"faces": faces}

@app.post("/register/{name}", summary="Registriert ein Bild für eine Person")
async def register(name: str, file: UploadFile = File(...)):
    """
    Speichert ein Bild für eine neue oder existierende Person.
    """
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name darf nicht leer sein.")
    
    image_bytes = await file.read()
    result = add_image_to_person(name, image_bytes)
    log.info(f"/register: {result}")
    
    if "Kein Gesicht" in result:
        raise HTTPException(status_code=400, detail=result)
        
    return {"result": result}

@app.post("/identify", summary="Identifiziert Personen in einem Bild")
async def identify(file: UploadFile = File(...)):
    """
    Gleicht die Gesichter in einem Bild mit der Datenbank ab.
    Wenn kein Gesicht gefunden wird, gibt es eine explizite Nachricht zurück.
    """
    image_bytes = await file.read()
    results = identify_faces_in_image(image_bytes)
    log.info(f"/identify: {len(results)} Ergebnis(se) für {file.filename} gefunden.")

    if not results:
        return {"results": "none"}

    return {"results": results}

@app.delete("/person/{name}", summary="Löscht eine Person")
async def remove_person(name: str):
    """
    Löscht eine Person und alle ihre Bilder aus der Datenbank.
    """
    success = delete_person_data(name)
    if not success:
        log.warning(f"Löschen von '{name}' fehlgeschlagen. Person nicht gefunden.")
        raise HTTPException(status_code=404, detail="Person nicht gefunden.")
    
    log.info(f"Person '{name}' wurde gelöscht.")
    return {"deleted": True, "name": name}

@app.get("/persons", summary="Listet alle registrierten Personen auf", response_model=Dict)
async def get_persons():
    """
    Gibt eine Liste aller Personen zurück, die in der Datenbank registriert sind.
    Wenn keine Personen registriert sind, gibt es eine explizite Nachricht zurück.
    """
    persons = list_persons()
    if not persons:
        return {"persons": "none"}
    
    return {"persons": persons}

@app.get("/healthz", summary="Health Check")
async def health_check():
    """Einfacher Endpunkt um zu prüfen, ob die API läuft."""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
