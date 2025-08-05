# CODE-ID: face_handler_v3.0
"""
Modulname: face_handler.py
Version: v3.0
Beschreibung: Implementiert eine persistente Embedding-Datenbank (.npy-Dateien),
             um die Startzeit drastisch zu reduzieren und Skalierbarkeit zu gewährleisten.
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

KNOWN_FACES_DIR = Path("known_faces")
KNOWN_FACES_DIR.mkdir(exist_ok=True)

known_face_encodings_cache: Dict[str, List[np.ndarray]] = {}

def image_bytes_to_array(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return np.array(image)

def load_and_cache_known_faces():
    """
    NEUE LOGIK: Lädt die vorab berechneten .npy-Embeddings statt die Bilder neu zu verarbeiten.
    Das ist extrem schnell und skalierbar.
    """
    global known_face_encodings_cache
    known_face_encodings_cache.clear()
    
    print("Lade persistente Embeddings...")
    for person_name in os.listdir(KNOWN_FACES_DIR):
        person_dir = KNOWN_FACES_DIR / person_name
        if not person_dir.is_dir():
            continue

        encodings = []
        # Wir laden jetzt die .npy Dateien, nicht die .png Dateien!
        for embedding_file in person_dir.glob("*.npy"):
            try:
                encoding = np.load(embedding_file)
                encodings.append(encoding)
            except Exception as e:
                print(f"Fehler beim Laden von persistentem Embedding {embedding_file}: {e}")
        
        if encodings:
            known_face_encodings_cache[person_name] = encodings
    
    print(f"✅ Cache gefüllt. {len(known_face_encodings_cache)} Person(en) aus der persistenten DB geladen.")

def identify_faces_in_image(image_bytes: bytes, threshold=0.6) -> List[Dict]:
    input_image = image_bytes_to_array(image_bytes)
    input_locations = face_recognition.face_locations(input_image)
    if not input_locations:
        return []
    
    input_encodings = face_recognition.face_encodings(input_image, input_locations)
    results = []

    all_known_encodings = []
    all_known_names = []
    if known_face_encodings_cache:
        for name, encodings in known_face_encodings_cache.items():
            for encoding in encodings:
                all_known_encodings.append(encoding)
                all_known_names.append(name)

    for i, encoding in enumerate(input_encodings):
        name = "unknown"
        if all_known_encodings:
            distances = face_recognition.face_distance(all_known_encodings, encoding)
            if len(distances) > 0:
                best_match_index = np.argmin(distances)
                if distances[best_match_index] <= threshold:
                    name = all_known_names[best_match_index]
        
        top, right, bottom, left = input_locations[i]
        results.append({
            "name": name,
            "box": [top, right, bottom, left],
            "encoding": encoding.tolist()
        })
    return results

def learn_face(name: str, encoding: List[float], image_bytes: bytes, box: List[int]) -> str:
    """
    NEUE LOGIK: Speichert jetzt nicht nur den Bild-Crop, sondern auch das
    dazugehörige Embedding als .npy-Datei für schnelles Neuladen.
    """
    person_dir = KNOWN_FACES_DIR / name
    person_dir.mkdir(exist_ok=True)

    top, right, bottom, left = box
    image_array = image_bytes_to_array(image_bytes)
    face_crop_array = image_array[top:bottom, left:right]
    face_crop_image = Image.fromarray(face_crop_array)
    
    with io.BytesIO() as buffer:
        face_crop_image.save(buffer, format="PNG")
        face_crop_bytes = buffer.getvalue()

    new_hash = hashlib.sha256(face_crop_bytes).hexdigest()
    hashes_path = person_dir / "hashes.json"
    existing_hashes = []
    if hashes_path.exists():
        with open(hashes_path, 'r') as f:
            try: existing_hashes = json.load(f)
            except json.JSONDecodeError: pass
    if new_hash in existing_hashes:
        return f"DUPLICATE: Dieses spezifische Gesicht ist bereits für {name} bekannt."

    # Basisname für Bild und Embedding festlegen
    num_files = len(list(person_dir.glob("*.png")))
    base_filename = f"face_{num_files + 1}"
    
    # Bild-Crop speichern (.png)
    crop_path = person_dir / f"{base_filename}.png"
    face_crop_image.save(crop_path)
    
    # Embedding speichern (.npy)
    np_encoding = np.array(encoding)
    embedding_path = person_dir / f"{base_filename}.npy"
    np.save(embedding_path, np_encoding)

    existing_hashes.append(new_hash)
    with open(hashes_path, 'w') as f:
        json.dump(existing_hashes, f)

    if name in known_face_encodings_cache:
        known_face_encodings_cache[name].append(np_encoding)
    else:
        known_face_encodings_cache[name] = [np_encoding]
        
    return f"SUCCESS: Gesicht wurde erfolgreich für {name} gelernt und persistent gespeichert."

def delete_person_data(name: str) -> bool:
    person_dir = KNOWN_FACES_DIR / name
    if person_dir.exists():
        shutil.rmtree(person_dir)
        if name in known_face_encodings_cache:
            del known_face_encodings_cache[name]
        return True
    return False

def list_persons() -> List[str]:
    return list(known_face_encodings_cache.keys())
