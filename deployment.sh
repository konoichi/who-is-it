#!/bin/bash
#
# CODE-ID: deploy_script_v1
#
# Dieses Skript automatisiert den Build- und Push-Prozess für das Docker-Image.
# Es liest die Konfiguration aus der `docker.env`-Datei.

# --- Sicherheitscheck und Konfiguration laden ---
set -e # Bricht das Skript bei einem Fehler sofort ab

# Prüfen, ob die Konfigurationsdatei existiert
if [ ! -f docker.env ]; then
    echo "🚨 Fehler: Die Konfigurationsdatei 'docker.env' wurde nicht gefunden."
    exit 1
fi

# Konfiguration laden
source docker.env
echo "✅ Konfiguration geladen."

# --- Variablen zusammensetzen ---
# Der Name des lokalen Images, das von docker-compose erstellt wird.
# Wir nehmen das UI-Image, da beide identisch sind.
LOCAL_IMAGE_NAME="${COMPOSE_PROJECT_NAME}-ui:latest"
# Die vollständige Adresse des Images in deiner Gitea Registry
REMOTE_IMAGE_TAG="${GITEA_REGISTRY_URL}/${GITEA_USER}/${IMAGE_NAME}:latest"


# --- Funktionen ---

build() {
    echo "🚀 Baue das Docker-Image..."
    docker-compose build
    echo "✅ Image erfolgreich gebaut."
}

push() {
    echo "🏷️  Tagge das lokale Image für den Push..."
    echo "     Lokales Image: ${LOCAL_IMAGE_NAME}"
    echo "     Remote Tag:    ${REMOTE_IMAGE_TAG}"
    docker tag "$LOCAL_IMAGE_NAME" "$REMOTE_IMAGE_TAG"
    echo "✅ Image getaggt."

    echo "🔐 Logge dich bei der Gitea Registry ein..."
    docker login "$GITEA_REGISTRY_URL"
    echo "✅ Login erfolgreich."

    echo "📤 Pushe das Image zur Registry..."
    docker push "$REMOTE_IMAGE_TAG"
    echo "✅ Push abgeschlossen. Das Image ist jetzt in deiner Gitea Registry."
}

# --- Skript-Logik ---

# Hauptfunktion, die basierend auf dem ersten Argument entscheidet, was zu tun ist.
case "$1" in
    build)
        build
        ;;
    push)
        push
        ;;
    all)
        build
        push
        ;;
    *)
        echo "Verwendung: $0 {build|push|all}"
        echo "  build: Baut das Docker-Image lokal."
        echo "  push:  Taggt das letzte gebaute Image und pusht es zur Gitea Registry."
        echo "  all:   Führt 'build' und dann 'push' aus."
        exit 1
        ;;
esac

