# CODE-ID: gradio_ui_v3.1
"""
Modulname: gradio_ui.py
Version: v3.1
Beschreibung: Kompatibilitäts-Fix. Ersetzt gr.Box durch gr.Group für ältere Gradio-Versionen.
Autor: kono
Erstellt am: 2025-08-03
Lizenz: MIT
"""
import gradio as gr
import requests
from PIL import Image, ImageDraw
import io

API_URL = "http://localhost:8001"

# --- API-Helferfunktionen ---

def image_to_bytes(image: Image.Image):
    """Konvertiert ein PIL Image in Bytes."""
    if image is None: return None
    buffer = io.BytesIO()
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()

def handle_api_request(method: str, endpoint: str, **kwargs):
    """Zentrale Funktion für API-Anfragen."""
    try:
        if method.upper() == 'POST':
            response = requests.post(f"{API_URL}{endpoint}", **kwargs)
        elif method.upper() == 'DELETE':
            response = requests.delete(f"{API_URL}{endpoint}", **kwargs)
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
    Der zentrale Schritt: Bild analysieren, Gesichter erkennen und identifizieren.
    """
    if image is None:
        return None, "Bitte zuerst ein Bild hochladen.", gr.update(visible=False), None, gr.update(visible=False), gr.update(visible=False)

    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}
    data, error = handle_api_request("POST", "/identify", files=files)

    if error:
        return None, f"❌ Fehler bei der Analyse: {error}", gr.update(visible=False), None, gr.update(visible=False), gr.update(visible=False)

    results = data.get("results", [])
    draw = ImageDraw.Draw(image)
    
    has_known_person = any(p['name'] != 'unknown' for p in results)
    has_unknown_person = any(p['name'] == 'unknown' for p in results)
    
    for person in results:
        name = person.get("name", "unknown")
        top, right, bottom, left = person.get("box", [0,0,0,0])
        outline_color = "lime" if name != "unknown" else "yellow"
        draw.rectangle([left, top, right, bottom], outline=outline_color, width=4)
        draw.text((left, top - 15), name, fill=outline_color)
    
    info_text = f"Analyse abgeschlossen. {len(results)} Gesicht(er) gefunden."
    
    return image, info_text, gr.update(visible=True), results, gr.update(visible=has_known_person), gr.update(visible=has_unknown_person)

def register_new_person(image: Image.Image, name: str, state_results: list):
    """Registriert eine neue Person."""
    if not name.strip():
        return "❌ Name darf nicht leer sein.", state_results
    
    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}
    data, error = handle_api_request("POST", f"/register/{name.strip()}", files=files)
    
    if error:
        return f"❌ Fehler bei der Registrierung: {error}", state_results
        
    return f"✅ {data.get('result', 'Erfolgreich registriert!')}", state_results

def add_image_to_existing_person(image: Image.Image, state_results: list):
    """Fügt ein Bild zu einer oder mehreren bereits erkannten Personen hinzu."""
    if image is None or not state_results:
        return "Keine Analyseergebnisse vorhanden, um das Bild zuzuordnen.", state_results
    
    known_persons = [p['name'] for p in state_results if p['name'] != 'unknown']
    if not known_persons:
        return "Keine bekannte Person im Bild gefunden, um das Bild zuzuordnen.", state_results

    buffered = image_to_bytes(image)
    files = {"file": ("image.png", buffered, "image/png")}
    
    log = []
    for name in set(known_persons):
        data, error = handle_api_request("POST", f"/register/{name}", files=files)
        if error:
            log.append(f"Fehler bei {name}: {error}")
        else:
            log.append(f"{data.get('result', f'Bild zu {name} hinzugefügt.')}")
            
    return " | ".join(log), state_results

def clear_ui():
    """Setzt die UI-Komponenten auf ihren Anfangszustand zurück."""
    return None, None, gr.update(visible=False), None, gr.update(visible=False), gr.update(visible=False), ""

# --- Gradio Interface ---
with gr.Blocks(theme=gr.themes.Monochrome(), title="Who-Is-It v3.1") as demo:
    state_analysis_results = gr.State([])

    gr.Markdown("# 🧠 Who-Is-It v3.1 - Der smarte Workflow")
    gr.Markdown("Lade ein Bild hoch. Der Rest passiert (fast) von allein.")

    with gr.Row():
        with gr.Column(scale=1):
            img_input = gr.Image(type="pil", label="Bildquelle", sources=["upload", "webcam", "clipboard"])
            
            with gr.Row():
                btn_clear = gr.Button("🗑️ Alles zurücksetzen", variant="stop")
                btn_analyze = gr.Button("🔍 Analysieren!", variant="primary")
            
            with gr.Group(visible=False) as box_context_actions:
                gr.Markdown("--- \n ### Nächste Schritte:")
                
                with gr.Group(visible=False) as box_add_to_person:
                    gr.Markdown("✅ **Bekannte Person(en) gefunden.**")
                    btn_add_image = gr.Button("Dieses Bild zur Sammlung hinzufügen")
                
                with gr.Group(visible=False) as box_register_person:
                    gr.Markdown("❓ **Unbekanntes Gesicht gefunden.**")
                    text_new_name = gr.Textbox(label="Name für die neue Person eingeben")
                    btn_register = gr.Button("Diese Person registrieren")

        with gr.Column(scale=2):
            img_output = gr.Image(label="Analyse-Ergebnis")
            text_status = gr.Textbox(label="Status", interactive=False)
            
    btn_analyze.click(
        fn=analyze_image,
        inputs=[img_input],
        outputs=[img_output, text_status, box_context_actions, state_analysis_results, box_add_to_person, box_register_person]
    )

    btn_add_image.click(
        fn=add_image_to_existing_person,
        inputs=[img_input, state_analysis_results],
        outputs=[text_status, state_analysis_results]
    )

    btn_register.click(
        fn=register_new_person,
        inputs=[img_input, text_new_name, state_analysis_results],
        outputs=[text_status, state_analysis_results]
    )
    
    btn_clear.click(
        fn=clear_ui,
        inputs=[],
        outputs=[img_input, img_output, box_context_actions, state_analysis_results, box_add_to_person, box_register_person, text_status]
    )

demo.launch(server_name="0.0.0.0", server_port=7001)

