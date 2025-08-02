"""
Modulname: face_db.py
Version: v1.0
Beschreibung: Lädt bekannte Gesichter aus known_faces/-Ordner
Autor: AbbyBot
Erstellt am: 2025-08-02
Lizenz: MIT
"""

import os
import face_recognition
import numpy as np
from PIL import Image

KNOWN_FACES_DIR = "known_faces"


def load_known_faces():
    known_faces = {}

    for person_name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
        if not os.path.isdir(person_dir):
            continue

        embeddings = []
        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            try:
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    embeddings.append(encodings[0])
            except Exception as e:
                print(f"Fehler beim Laden von {filepath}: {e}")

        if embeddings:
            known_faces[person_name] = embeddings

    return known_faces


if __name__ == "__main__":
    faces = load_known_faces()
    for name, vectors in faces.items():
        print(f"{name}: {len(vectors)} Embeddings geladen")
