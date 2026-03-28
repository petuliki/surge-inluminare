# RunPod Deployment Anleitung

## Schritt 1: RunPod Pod erstellen

1. Auf **runpod.io** einloggen
2. Links im Menu: **Pods** > **+ Deploy**
3. GPU auswaehlen: **L40S 48 GB** (Community Cloud, ~$0.79/h)
4. Template: **RunPod PyTorch 2.4.0** (CUDA 12.4, Ubuntu 22.04)
5. Container Disk: **50 GB**
6. Volume: **Neues Volume erstellen** > **100 GB** > Mount Path: `/workspace`
7. Exposed HTTP Ports: `8888`
8. Exposed TCP Ports: `8000,8001,8002,8889`
9. Klicke **Deploy**

## Schritt 2: Code klonen und installieren

Oeffne das **Web Terminal** in der RunPod UI und fuehre aus:

```bash
# Code von GitHub klonen
cd /workspace
git clone https://github.com/petuliki/surge-inluminare.git
cd surge-inluminare

# Alles installieren (dauert ~10-15 Min)
bash scripts/runpod_setup.sh
```

Das Setup-Script installiert automatisch:
- vLLM, Pipecat, faster-whisper, CosyVoice 2
- FastAPI + alle Python-Dependencies
- Node.js + Frontend-Build
- Supervisord-Konfiguration

## Schritt 3: Modelle herunterladen (einmalig)

```bash
bash /scripts/download_models.sh
```

Dauert ~15-20 Minuten. Die Modelle werden auf dem persistenten Volume gespeichert
und muessen nur einmal heruntergeladen werden.

## Schritt 4: Starten

```bash
bash /scripts/start.sh
```

Oder bei Neustart des Pods (wenn alles schon installiert ist):
```bash
cd /workspace/surge-inluminare
bash scripts/runpod_setup.sh  # Schnell, da alles gecached
bash /scripts/start.sh
```

## Schritt 5: Zugriff

- **Frontend**: RunPod Proxy URL auf Port **8888**
- **JupyterLab**: RunPod Proxy URL auf Port **8889**
- **Health Check**: `https://POD-URL:8888/health`

## Schritt 6: Erste Nutzung

1. Oeffne die Frontend-URL (Port 8888) im Browser
2. Waehle einen Charakter unter **AGENTIS**
3. Optional: Klone eine Stimme unter **Vox** (Seite 3)
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

## Code aktualisieren

Wenn du Aenderungen am Code vornimmst:

```bash
cd /workspace/surge-inluminare
git pull
bash scripts/runpod_setup.sh
bash /scripts/start.sh
```
