# CODE-ID: face_handler_v2.2
"""
Modulname: face_handler.py
Version: v2.2
Beschreibung: Stellt sicher, dass gefundene, aber nicht identifizierte Gesichter
             explizit als "unknown" zurückgegeben werden, auch wenn die Datenbank leer ist.
Autor: kono
Erstellt am: 2025-08-03
Lizenz: MIT
"""
import os
import shutil
from pathlib import Path
import face_recognition
import numpy as np
from PIL import Image
import io
import hashlib
import json
from typing import List, Dict

# Verzeichnis für bekannte Gesichter
KNOWN_FACES_DIR = Path("known_faces")
KNOWN_FACES_DIR.mkdir(exist_ok=True)

# In-Memory-Cache für die Embeddings
known_face_encodings_cache: Dict[str, List[np.ndarray]] = {}

def image_bytes_to_array(image_bytes: bytes) -> np.ndarray:
    """Konvertiert Bild-Bytes in ein Numpy-Array."""
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return np.array(image)

def extract_face_locations(image_array: np.ndarray) -> List[Dict[str, int]]:
    """Extrahiert die Bounding-Boxen von Gesichtern im Bild."""
    locations = face_recognition.face_locations(image_array)
    return [{"x": left, "y": top, "width": right - left, "height": bottom - top} 
            for top, right, bottom, left in locations]

def load_and_cache_known_faces():
    """Lädt alle bekannten Gesichter aus dem Verzeichnis und cacht die Encodings."""
    global known_face_encodings_cache
    known_face_encodings_cache.clear()

    for person_name in os.listdir(KNOWN_FACES_DIR):
        person_dir = KNOWN_FACES_DIR / person_name
        if not person_dir.is_dir():
            continue

        encodings = []
        for image_file in person_dir.glob("*.png"):
            try:
                image = face_recognition.load_image_file(image_file)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    encodings.append(face_encodings[0])
            except Exception as e:
                print(f"Fehler beim Verarbeiten von {image_file}: {e}")
        
        if encodings:
            known_face_encodings_cache[person_name] = encodings
    
    print(f"✅ Cache gefüllt. {len(known_face_encodings_cache)} Person(en) geladen.")

def add_image_to_person(name: str, image_bytes: bytes) -> str:
    """Fügt ein neues Bild zu einer Person hinzu, aber nur, wenn es kein Duplikat ist."""
    new_image_hash = hashlib.sha256(image_bytes).hexdigest()
    person_dir = KNOWN_FACES_DIR / name
    person_dir.mkdir(exist_ok=True)
    hashes_path = person_dir / "hashes.json"
    
    existing_hashes = []
    if hashes_path.exists():
        with open(hashes_path, 'r') as f:
            try:
                existing_hashes = json.load(f)
            except json.JSONDecodeError:
                pass

    if new_image_hash in existing_hashes:
        return f"Dieses Bild existiert bereits in der Sammlung für {name}."

    image_array = image_bytes_to_array(image_bytes)
    face_encodings = face_recognition.face_encodings(image_array)

    if not face_encodings:
        return "Kein Gesicht im Bild gefunden. Nichts gespeichert."

    num_files = len(list(person_dir.glob("*.png")))
    image_path = person_dir / f"{name.lower()}_{num_files + 1}.png"
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    existing_hashes.append(new_image_hash)
    with open(hashes_path, 'w') as f:
        json.dump(existing_hashes, f)

    if name in known_face_encodings_cache:
        known_face_encodings_cache[name].append(face_encodings[0])
    else:
        known_face_encodings_cache[name] = [face_encodings[0]]
        
    return f"Neues Bild für {name} erfolgreich hinzugefügt."

def identify_faces_in_image(image_bytes: bytes, threshold=0.6) -> List[Dict]:
    """Identifiziert Gesichter in einem Bild und gleicht sie mit der Datenbank ab."""
    input_image = image_bytes_to_array(image_bytes)
    input_locations = face_recognition.face_locations(input_image)

    # Wenn überhaupt keine Gesichter im Bild sind, gib eine leere Liste zurück.
    if not input_locations:
        return []

    input_encodings = face_recognition.face_encodings(input_image, input_locations)
    results = []

    # Wenn die Datenbank leer ist, sind alle gefundenen Gesichter "unknown".
    if not known_face_encodings_cache:
        for loc in input_locations:
            top, right, bottom, left = loc
            results.append({"name": "unknown", "box": [top, right, bottom, left]})
        return results

    # Wenn die Datenbank gefüllt ist, führe den Vergleich durch.
    all_known_encodings = []
    all_known_names = []
    for name, encodings in known_face_encodings_cache.items():
        for encoding in encodings:
            all_known_encodings.append(encoding)
            all_known_names.append(name)
            
    for i, unknown_encoding in enumerate(input_encodings):
        distances = face_recognition.face_distance(all_known_encodings, unknown_encoding)
        
        name = "unknown"
        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            if distances[best_match_index] <= threshold:
                name = all_known_names[best_match_index]

        top, right, bottom, left = input_locations[i]
        results.append({
            "name": name,
            "box": [top, right, bottom, left]
        })
        
    return results

def delete_person_data(name: str) -> bool:
    """Löscht eine Person und alle zugehörigen Daten."""
    person_dir = KNOWN_FACES_DIR / name
    if person_dir.exists():
        shutil.rmtree(person_dir)
        if name in known_face_encodings_cache:
            del known_face_encodings_cache[name]
        return True
    return False

def list_persons() -> List[str]:
    """Listet alle registrierten Personen auf."""
    return list(known_face_encodings_cache.keys())
