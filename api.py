# CODE-ID: api_v2.8
"""
Modulname: api.py
Version: v2.8
Beschreibung: Ersetzt den /register-Endpunkt durch einen neuen /learn-Endpunkt,
             der das gezielte Lernen einzelner Gesichter ermöglicht.
Autor: kono
Erstellt am: 2025-08-03
Lizenz: MIT
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import json
from typing import List, Dict

from face_handler import (
    identify_faces_in_image,
    delete_person_data,
    list_persons,
    load_and_cache_known_faces,
    learn_face
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)8s | %(message)s")
log = logging.getLogger("api")

app = FastAPI(title="Who-Is-It API", version="2.8")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    log.info("Server startet... Lade bekannte Gesichter.")
    load_and_cache_known_faces()

@app.post("/identify", summary="Identifiziert Personen in einem Bild")
async def identify(file: UploadFile = File(...)):
    """
    Gleicht die Gesichter in einem Bild mit der Datenbank ab.
    Gibt für jedes Gesicht Name, Box und Encoding zurück.
    """
    image_bytes = await file.read()
    results = identify_faces_in_image(image_bytes)
    log.info(f"/identify: {len(results)} Ergebnis(se) für {file.filename} gefunden.")
    if not results:
        return {"results": "none"}
    return {"results": results}

@app.post("/learn", summary="Lernt ein spezifisches Gesicht aus einem Bild")
async def learn(
    name: str = Form(...),
    box_json: str = Form(...),
    encoding_json: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Nimmt die Daten eines Gesichts (Name, Box, Encoding) und das Originalbild,
    um dieses Gesicht gezielt zu lernen.
    """
    try:
        box = json.loads(box_json)
        encoding = json.loads(encoding_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Ungültiges JSON für Box oder Encoding.")

    image_bytes = await file.read()
    result = learn_face(name, encoding, image_bytes, box)
    
    log.info(f"/learn: {result}")
    if result.startswith("DUPLICATE"):
        raise HTTPException(status_code=409, detail=result)

    return {"result": result}


@app.delete("/person/{name}", summary="Löscht eine Person")
async def remove_person(name: str):
    success = delete_person_data(name)
    if not success:
        log.warning(f"Löschen von '{name}' fehlgeschlagen. Person nicht gefunden.")
        raise HTTPException(status_code=404, detail="Person nicht gefunden.")
    log.info(f"Person '{name}' wurde gelöscht.")
    return {"deleted": True, "name": name}

@app.get("/persons", summary="Listet alle registrierten Personen auf")
async def get_persons():
    persons = list_persons()
    if not persons:
        return {"persons": "none"}
    return {"persons": persons}

@app.get("/healthz", summary="Health Check")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
