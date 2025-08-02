"""
Modulname: face_utils.py
Version: v1.0
Beschreibung: Hilfsfunktionen für Gesichtserkennung und -vergleich
Autor: AbbyBot
Erstellt am: 2025-08-02
Lizenz: MIT
"""

import face_recognition
import numpy as np
from typing import List, Dict, Tuple


def extract_faces(image: np.ndarray):
    """Gibt Bounding-Boxen der Gesichter im Bild zurück."""
    return face_recognition.face_locations(image)


def encode_faces(image: np.ndarray):
    """Berechnet Face Embeddings für alle erkannten Gesichter im Bild."""
    return face_recognition.face_encodings(image)


def match_embedding(embedding, known_faces: Dict[str, List[np.ndarray]], threshold=0.6) -> Tuple[str, float]:
    """
    Vergleicht ein Gesichtsembedding mit bekannten Personen.
    Gibt den besten Match + Abstand zurück. Falls keiner unter Threshold, dann "unknown".
    """
    best_match = "unknown"
    best_distance = float("inf")

    for name, embeddings in known_faces.items():
        distances = face_recognition.face_distance(embeddings, embedding)
        min_dist = np.min(distances) if len(distances) > 0 else float("inf")

        if min_dist < best_distance:
            best_distance = min_dist
            best_match = name

    if best_distance > threshold:
        return "unknown", best_distance
    return best_match, best_distance


def match_all_embeddings(embeddings: List[np.ndarray], known_faces: Dict[str, List[np.ndarray]], threshold=0.6):
    """
    Vergleicht eine Liste von Embeddings mit bekannten Personen.
    Gibt Liste von Tupeln (Name, Distance) zurück.
    """
    results = []
    for emb in embeddings:
        name, score = match_embedding(emb, known_faces, threshold)
        results.append((name, score))
    return results
