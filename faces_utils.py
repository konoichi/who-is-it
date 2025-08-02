"""
Modulname: faces_utils.py
Version: v1.2
Beschreibung: Hilfsfunktionen für Gesichtsbild-Verarbeitung, Speicherung und Identifikation.
Autor: AbbyBot
Erstellt am: 2025-08-02
Lizenz: MIT
"""

import os
import face_recognition
import numpy as np
from PIL import Image
from pathlib import Path

FACE_DIR = Path("./faces")
FACE_DIR.mkdir(exist_ok=True)


def save_face_image(name: str, image_path: Path) -> bool:
    img = face_recognition.load_image_file(image_path)
    locations = face_recognition.face_locations(img)
    if not locations:
        return False

    person_dir = FACE_DIR / name
    person_dir.mkdir(exist_ok=True)

    i = 0
    for loc in locations:
        top, right, bottom, left = loc
        face_image = img[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        filename = f"face_{i}.png"
        pil_image.save(person_dir / filename)
        i += 1

    return True


def get_face_encodings(name: str) -> list:
    person_dir = FACE_DIR / name
    if not person_dir.exists():
        return []

    encodings = []
    for file in person_dir.iterdir():
        if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            image = face_recognition.load_image_file(file)
            faces = face_recognition.face_encodings(image)
            if faces:
                encodings.append(faces[0])
    return encodings


def delete_face_data(name: str) -> bool:
    person_dir = FACE_DIR / name
    if person_dir.exists() and person_dir.is_dir():
        for file in person_dir.iterdir():
            file.unlink()
        person_dir.rmdir()
        return True
    return False


def delete_single_image(name: str, filename: str) -> bool:
    file_path = FACE_DIR / name / filename
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def list_face_images(name: str) -> list[str]:
    person_dir = FACE_DIR / name
    if not person_dir.exists():
        return []
    return [file.name for file in person_dir.iterdir() if file.is_file()]
