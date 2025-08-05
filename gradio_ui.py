# CODE-ID: gradio_ui_v4.3
"""
Modulname: gradio_ui.py
Version: v4.3
Beschreibung: Behebt einen kritischen Fehler in der `clear_ui`-Funktion, der die
             gesamte Update-Logik der UI instabil gemacht hat.
Autor: AbbyBot
Erstellt am: 2025-08-03
Lizenz: MIT
"""
import gradio as gr
import requests
from PIL import Image, ImageDraw
import io
import json
from functools import partial

API_URL = "http://localhost:8001"
MAX_FACES_TO_DISPLAY = 10 # Maximale Anzahl an Gesichtern, die die UI anzeigen kann

# --- API-Helferfunktionen ---

def image_to_bytes(image: Image.Image):
    if image is None: return None
    buffer = io.BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()

def handle_api_request(method: str, endpoint: str, **kwargs):
    try:
        if method.upper() == 'POST':
            response = requests.post(f"{API_URL}{endpoint}", **kwargs)
        else:
             return None, "Ungültige Methode"
        response.raise_for_status()
        if response.status_code == 200 and response.content:
            return response.json(), None
        return {"status": "ok", "message": response.reason}, None
    except requests.exceptions.RequestException as e:
        error_message = f"API-Fehler: {e}"
        if e.response is not None:
            try:
                error_details = e.response.json()
                error_message += f" | Details: {error_details.get('detail', e.response.text)}"
            except ValueError:
                error_message += f" | Details: {e.response.text}"
        return None, error_message

# --- Kernlogik für den Workflow ---

def analyze_image(image: Image.Image):
    """
    Analysiert das Bild, markiert Gesichter und bereitet die einzelnen
    Gesichts-Crops für das gezielte Lernen vor.
    """
    num_components_per_row = 4 # row, crop, name, button
    if image is None:
        updates = [gr.update(visible=False) for _ in range(MAX_FACES_TO_DISPLAY * num_components_per_row)]
        return None, "Bitte zuerst ein Bild hochladen.", None, None, *updates

    original_image_bytes = image_to_bytes(image)
    files = {"file": ("image.png", original_image_bytes, "image/png")}
    data, error = handle_api_request("POST", "/identify", files=files)

    if error:
        updates = [gr.update(visible=False) for _ in range(MAX_FACES_TO_DISPLAY * num_components_per_row)]
        return None, f"❌ Fehler: {error}", None, None, *updates

    results = data.get("results")
    if results == "none" or not results:
        updates = [gr.update(visible=False) for _ in range(MAX_FACES_TO_DISPLAY * num_components_per_row)]
        return image, "Keine Gesichter auf dem Bild gefunden.", None, None, *updates

    draw = ImageDraw.Draw(image)
    for person in results:
        name = person.get("name", "unknown")
        top, right, bottom, left = person.get("box", [0,0,0,0])
        outline_color = "lime" if name != "unknown" else "yellow"
        draw.rectangle([left, top, right, bottom], outline=outline_color, width=4)
        draw.text((left, top - 15), name, fill=outline_color)

    updates = []
    pil_image = Image.open(io.BytesIO(original_image_bytes))

    for i in range(MAX_FACES_TO_DISPLAY):
        if i < len(results):
            person = results[i]
            top, right, bottom, left = person["box"]
            face_crop = pil_image.crop((left, top, right, bottom))
            name = person["name"]
            
            updates.append(gr.update(visible=True))
            updates.append(gr.update(value=face_crop))
            updates.append(gr.update(value=name if name != 'unknown' else ''))
            button_text = f"Bild zu {name} hinzufügen" if name != 'unknown' else "Neue Person lernen"
            updates.append(gr.update(value=button_text))
        else:
            updates.append(gr.update(visible=False))
            updates.append(gr.update(value=None))
            updates.append(gr.update(value=''))
            updates.append(gr.update(value=''))

    status_text = f"Analyse abgeschlossen. {len(results)} Gesicht(er) gefunden."
    return image, status_text, results, original_image_bytes, *updates

def learn_face_ui(face_index, name_input, analysis_results, original_image_bytes):
    if not name_input or not name_input.strip():
        return "❌ Bitte einen Namen eingeben."
    if not analysis_results or face_index >= len(analysis_results):
        return "❌ Analyse-Daten sind veraltet oder fehlerhaft."

    face_data = analysis_results[face_index]
    box_json = json.dumps(face_data['box'])
    encoding_json = json.dumps(face_data['encoding'])

    payload = {"name": (None, name_input.strip()), "box_json": (None, box_json), "encoding_json": (None, encoding_json)}
    files = {"file": ("image.png", original_image_bytes, "image/png")}
    data, error = handle_api_request("POST", "/learn", files=files, data=payload)

    if error:
        return f"❌ Fehler beim Lernen: {error}"
    return f"✅ {data.get('result', 'Erfolgreich gelernt!')}"

def clear_ui():
    """
    Setzt die UI-Komponenten korrekt auf ihren Anfangszustand zurück.
    """
    updates = []
    for _ in range(MAX_FACES_TO_DISPLAY):
        updates.append(gr.update(visible=False)) # row
        updates.append(gr.update(value=None))    # crop_img
        updates.append(gr.update(value=""))      # name_txt
        updates.append(gr.update(value="Aktion"))# learn_btn
    return None, "", None, None, *updates

# --- Gradio Interface ---
with gr.Blocks(theme=gr.themes.Monochrome(), title="Who-Is-It v4.3") as demo:
    gr.Markdown("# 🧠 Who-Is-It v4.3 - Der Forensik-Tisch")
    gr.Markdown("Lade ein Bild hoch, um es zu analysieren. Lerne dann gezielt einzelne Gesichter.")

    state_analysis_results = gr.State()
    state_original_image = gr.State()

    with gr.Row():
        with gr.Column(scale=1):
            img_input = gr.Image(type="pil", label="Bildquelle", sources=["upload", "webcam", "clipboard"])
            with gr.Row():
                btn_clear = gr.Button("🗑️ Alles zurücksetzen", variant="stop")
                btn_analyze = gr.Button("🔍 Analysieren!", variant="primary")
            text_status = gr.Textbox(label="Status", interactive=False)
        with gr.Column(scale=2):
            img_output = gr.Image(label="Analyse-Ergebnis")
    
    gr.Markdown("--- \n ### Gefundene Gesichter zum Lernen:")
    
    face_rows_components = []
    for i in range(MAX_FACES_TO_DISPLAY):
        with gr.Row(visible=False) as row:
            crop_img = gr.Image(label=f"Gesicht {i+1}", interactive=False, height=150, width=150)
            with gr.Column():
                name_txt = gr.Textbox(label="Name")
                learn_btn = gr.Button("Aktion", variant="secondary")
            
            learn_btn.click(
                fn=partial(learn_face_ui, i),
                inputs=[name_txt, state_analysis_results, state_original_image],
                outputs=[text_status]
            )
            face_rows_components.extend([row, crop_img, name_txt, learn_btn])

    outputs_for_analyze = [img_output, text_status, state_analysis_results, state_original_image, *face_rows_components]
    btn_analyze.click(fn=analyze_image, inputs=[img_input], outputs=outputs_for_analyze)
    
    outputs_for_clear = [img_input, text_status, state_analysis_results, state_original_image, *face_rows_components]
    btn_clear.click(fn=clear_ui, inputs=[], outputs=outputs_for_clear)

demo.launch(server_name="0.0.0.0", server_port=7001)
