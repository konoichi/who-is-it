"""
Modulname: gradio_ui.py
Version: v1.5
Beschreibung: Gradio-Frontend für Gesichtserkennung (zentrale Bildquelle + Bildpersistenz im Backend)
Autor: AbbyBot
Erstellt am: 2025-08-02
Lizenz: MIT
"""

import gradio as gr
import requests
from PIL import Image, ImageDraw

API_URL = "http://localhost:8001"

def detect_faces(image: Image.Image):
    if image is None:
        return None, "❌ Kein Bild übergeben."

    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}

    try:
        response = requests.post(f"{API_URL}/detect", files=files)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return None, f"❌ Fehler: {e}"

    draw = ImageDraw.Draw(image)
    for face in data["faces"]:
        x, y, w, h = face["x"], face["y"], face["width"], face["height"]
        draw.rectangle([x, y, x + w, y + h], outline="red", width=3)

    return image, f"✅ Gesichter erkannt: {len(data['faces'])}"

def register_person(image: Image.Image, name: str):
    if image is None or not name:
        return "❌ Bild und Name erforderlich."

    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}
    try:
        response = requests.post(f"{API_URL}/register/{name}", files=files)
        response.raise_for_status()
        return f"✅ Registriert als {name}"
    except Exception as e:
        return f"❌ Fehler: {e}"

def add_image_to_person(image: Image.Image, name: str):
    if image is None or not name:
        return "❌ Bild und Name erforderlich."

    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}
    try:
        response = requests.post(f"{API_URL}/register_add/{name}", files=files)
        response.raise_for_status()
        return f"✅ Weiteres Bild für {name} registriert."
    except Exception as e:
        return f"❌ Fehler: {e}"

def identify_faces(image: Image.Image):
    if image is None:
        return None, "❌ Kein Bild übergeben."

    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}

    try:
        response = requests.post(f"{API_URL}/identify", files=files)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return None, f"❌ Fehler: {e}"

    draw = ImageDraw.Draw(image)
    for person in data["results"]:
        name = person["name"]
        top, right, bottom, left = person["box"]
        draw.rectangle([left, top, right, bottom], outline="green", width=3)
        draw.text((left, top - 10), name, fill="green")

    return image, f"✅ Erkannt: {[p['name'] for p in data['results']]}"

def image_to_bytes(image: Image.Image):
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.read()

with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Wer ist das? – Gesichtserkennung im Homelab")

    with gr.Row():
        img_input = gr.Image(type="pil", label="Bildquelle", sources=["upload", "webcam", "clipboard"], image_mode="RGB")

    with gr.Tabs():
        with gr.Tab("👀 Erkennen"):
            btn_detect = gr.Button("Gesichter erkennen")
            img_out_detect = gr.Image()
            msg_detect = gr.Textbox()
            btn_detect.click(fn=detect_faces, inputs=img_input, outputs=[img_out_detect, msg_detect])

        with gr.Tab("🆕 Neue Person registrieren"):
            name_input = gr.Textbox(label="Name")
            btn_register = gr.Button("Registrieren")
            msg_register = gr.Textbox()
            btn_register.click(fn=register_person, inputs=[img_input, name_input], outputs=msg_register)

        with gr.Tab("➕ Bild zu Person hinzufügen"):
            name_input_add = gr.Textbox(label="Existierender Name")
            btn_add = gr.Button("Bild hinzufügen")
            msg_add = gr.Textbox()
            btn_add.click(fn=add_image_to_person, inputs=[img_input, name_input_add], outputs=msg_add)

        with gr.Tab("🔍 Identifizieren"):
            btn_identify = gr.Button("Person(en) erkennen")
            img_out_ident = gr.Image()
            msg_identify = gr.Textbox()
            btn_identify.click(fn=identify_faces, inputs=img_input, outputs=[img_out_ident, msg_identify])

demo.launch(server_name="localhost", server_port=7001)
