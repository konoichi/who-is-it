"""
Modulname: api.py
Version: v1.5
Beschreibung: FastAPI-Backend für Gesichtserkennung mit Datei-Persistenz und Personenverwaltung
Autor: AbbyBot
Erstellt am: 2025-08-02
Lizenz: MIT
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faces_utils import extract_faces, save_image_for_person, get_face_encodings, load_known_faces, identify_face, delete_person, list_registered_persons
import uvicorn
import logging
from pathlib import Path

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)8s | %(message)s")
log = logging.getLogger("api")

# App initialisieren
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embeddings-Cache laden
load_cached_embeddings()

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    image_bytes = await file.read()
    faces = faces = extract_faces(image)
    log.info(f"/detect: file, Faces: {len(faces)}")
return {"faces": faces}

@app.post("/register/{name}")
async def register(name: str, file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = register_new_person(name, image_bytes)
    return {"result": result}

@app.post("/register_add/{name}")
async def register_add(name: str, file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = add_image_to_person(name, image_bytes)
    return {"result": result}

@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    results = identify_faces_in_image(image_bytes)
    return {"results": results}

@app.delete("/person/{name}")
async def remove_person(name: str):
    success = delete_person(name)
    return JSONResponse(status_code=200 if success else 404, content={"deleted": success})

@app.delete("/person/{name}/{filename}")
async def remove_image(name: str, filename: str):
    success = delete_image_for_person(name, filename)
    return JSONResponse(status_code=200 if success else 404, content={"deleted": success})

@app.get("/person/{name}")
async def list_person_images(name: str):
    files = list_images_for_person(name)
    return {"images": files}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
