# RunPod Deployment Anleitung

## Schritt 1: Docker Image bauen und pushen

```bash
# Lokal bauen
docker build -t surge-inluminare .

# Auf Docker Hub pushen (ersetze USERNAME)
docker tag surge-inluminare USERNAME/surge-inluminare:latest
docker push USERNAME/surge-inluminare:latest
```

## Schritt 2: RunPod Pod erstellen

1. Auf **runpod.io** einloggen
2. Links im Menu: **Pods** > **+ Deploy**
3. GPU auswaehlen: **L40S 48 GB** (Community Cloud, ~$0.79/h)
4. Template: **Custom Docker Image**
5. Docker Image: `USERNAME/surge-inluminare:latest`
6. Container Disk: **50 GB**
7. Volume: **Neues Volume erstellen** > **100 GB** > Mount Path: `/workspace`
8. Exposed HTTP Ports: `8888` (API + Frontend)
9. Exposed TCP Ports: `8000,8001,8002,8889`
10. Klicke **Deploy**

## Schritt 3: Modelle herunterladen (einmalig)

Nach dem Start des Pods:

1. Oeffne das **Web Terminal** in der RunPod UI
2. Fuehre aus:
```bash
bash /scripts/download_models.sh
```
3. Warte bis alle Modelle heruntergeladen sind (~15-20 Minuten)
4. Starte den Pod neu: **Stop** > **Start**

## Schritt 4: Zugriff

- **Frontend**: RunPod Proxy URL auf Port 8888
- **JupyterLab**: RunPod Proxy URL auf Port 8889
- **Health Check**: `https://POD-URL:8888/health`

## Schritt 5: Erste Nutzung

1. Oeffne die Frontend-URL im Browser
2. Waehle einen Charakter unter **AGENTIS**
3. Optional: Klone eine Stimme unter **Vox**
4. Waehle die Stimme unter **VOX**
5. Klicke **INCHOATE** um das Gespraech zu starten
6. Klicke **FINISCI** um zu beenden

## Kostenueberblick

| GPU | Preis/Stunde | VRAM | Empfehlung |
|-----|-------------|------|------------|
| RTX A6000 48GB | ~$0.33/h | 48 GB | Budget |
| L40S 48GB | ~$0.79/h | 48 GB | Empfohlen |
| A100 80GB | ~$1.19/h | 80 GB | Maximale Geschwindigkeit |

## Ports

| Port | Service | Beschreibung |
|------|---------|-------------|
| 8000 | vLLM | LLM API (OpenAI-kompatibel) |
| 8001 | TTS | CosyVoice 2 Sprachsynthese |
| 8002 | STT | faster-whisper Spracherkennung |
| 8888 | API | FastAPI + Pipecat + Frontend |
| 8889 | JupyterLab | Modell-Management |
