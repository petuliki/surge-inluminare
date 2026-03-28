---
name: german-voice-agent
description: Erstellt einen deutschsprachigen AI Voice Agent auf einem einzelnen RunPod GPU-Pod. Verwende diesen Skill immer dann, wenn der Nutzer einen sprachbasierten KI-Agenten, Voice Bot, Sprach-Chatbot oder Sprachassistenten bauen will – insbesondere für deutsche Sprache auf RunPod oder ähnlicher GPU-Cloud-Infrastruktur. Trigger-Phrasen umfassen "Voice Agent", "Sprachassistent", "Sprach-KI", "Voice Bot", "TTS + LLM + STT Pipeline", "Echtzeit-Sprachdialog", "RunPod Voice", "deutschsprachiger Agent", "Spracherkennung + Sprachausgabe", "Conversational AI auf GPU". Der Skill deckt die gesamte Pipeline ab: STT (faster-whisper), unzensiertes LLM (Qwen3-14B abliterated via vLLM), TTS mit Voice Cloning (CosyVoice 2 / Qwen3-TTS), orchestriert durch Pipecat auf einem einzelnen GPU-Pod. Auch bei Teilaspekten wie "TTS auf RunPod", "vLLM für Deutsch", "Voice Cloning Pipeline" oder "niedrige Latenz Sprachsystem" soll dieser Skill getriggert werden.
---

# German Voice Agent auf RunPod

Dieser Skill erstellt einen vollständigen deutschsprachigen AI Voice Agent, der auf einem **einzelnen RunPod GPU-Pod** läuft. Alle drei Inferenz-Modelle (STT, LLM, TTS) teilen sich eine GPU. Das LLM ist unzensiert (abliterated). Die Ziellatenz liegt bei **500–800ms End-to-End** (Spracheingabe → Sprachausgabe).

## Voraussetzungen

- RunPod-Account mit Zugang zu Community Cloud Pods
- Budget: CHF 0.70–1.80/Stunde (≈ USD 0.79–2.00/h)
- Grundkenntnisse Docker, Python, Terminal
- Optional: WAV-Referenzdatei für Voice Cloning (3–10 Sekunden, 24kHz mono)

## Architektur-Überblick

```
Client (Browser) ←→ WebRTC / WebSocket
                         ↓
┌─────────────────────────────────────────────┐
│  Pipecat Orchestrator (Python, CPU)         │
│                                             │
│  Silero VAD  →  faster-whisper  →  vLLM     │
│  (CPU, 1ms)    (GPU, ~1.5 GB)    (GPU,~10GB)│
│                        ↓                    │
│                    CosyVoice 2 / Qwen3-TTS  │
│                    (GPU, ~5 GB)             │
└─────────────────────────────────────────────┘
          Einzelne GPU, ~19–25 GB VRAM
```

## Schritt-für-Schritt-Anleitung

### Phase 1: GPU und Tier auswählen

Lies die Referenzdatei `references/gpu-tiers.md` für die vollständige Kostenübersicht.

Für den Nutzer die passende Konfiguration ermitteln basierend auf:
- **Budget** (CHF/h)
- **Latenz-Anforderung** (natürlicher Dialog vs. toleranter)
- **Voice Cloning** (ja/nein, welches Referenz-Audio?)

**Empfohlene Standardkonfiguration** (Balanced Tier, CHF ~0.85/h):

| Komponente | Modell | VRAM |
|-----------|--------|------|
| GPU | **L40S 48 GB** (RunPod Community, ~$0.79/h) | 48 GB |
| LLM | `mlabonne/Qwen3-14B-abliterated` AWQ 4-bit via vLLM | ~10 GB |
| STT | `faster-whisper` large-v3-turbo fp16 + Silero VAD | ~2.5 GB |
| TTS | `CosyVoice2-0.5B` (streaming, Voice Cloning) | ~5 GB |
| Orchestrator | Pipecat (CPU) | — |
| **Gesamt-VRAM** | | **~19.5 GB / 48 GB** |

**Latenz-Breakdown**: VAD ~250ms → STT ~100ms → LLM TTFT ~150–200ms → TTS TTFA ~100–150ms → **Total ~500–650ms**

### Phase 2: RunPod Pod erstellen

1. Auf RunPod einloggen → "Pods" → "Deploy"
2. GPU auswählen gemäss gewähltem Tier (siehe `references/gpu-tiers.md`)
3. Template: **RunPod PyTorch 2.4.0** (CUDA 12.4, Ubuntu 22.04)
4. Container Disk: mindestens **50 GB** (Modelle: ~25 GB, Dependencies: ~10 GB)
5. Volume: **100 GB** persistent (für Modell-Cache unter `/workspace/models`)
6. Exposed Ports: `8000` (vLLM), `8001` (TTS), `8002` (STT), `8888` (Pipecat/WebSocket)

### Phase 3: Modelle installieren

Lies `references/model-setup.md` für die vollständigen Installationsscripte.

**Kurzfassung der drei Services:**

#### 3a. vLLM (LLM-Server)

```bash
pip install vllm
vllm serve mlabonne/Qwen3-14B-abliterated \
  --quantization awq_marlin \
  --gpu-memory-utilization 0.50 \
  --max-model-len 4096 \
  --host 0.0.0.0 --port 8000 \
  --dtype float16
```

Kritische Parameter:
- `--gpu-memory-utilization 0.50`: Reserviert 50% der GPU für LLM, Rest für STT+TTS
- `--max-model-len 4096`: Begrenzt KV-Cache-Verbrauch für Voice-Agent-Kontext
- AWQ-Marlin-Kernel liefert ~10x Speedup gegenüber naivem AWQ

#### 3b. faster-whisper (STT-Server)

```bash
pip install faster-whisper
```

Server als separater Prozess mit eigenem CUDA-Kontext. Für die FastAPI-Wrapper-Implementation siehe `references/model-setup.md`.

Konfiguration:
- Modell: `large-v3-turbo` (809M Parameter, int8 oder fp16)
- Deutsch-optimiert: Optional `TheChola/whisper-large-v3-turbo-german-faster-whisper`
- Silero VAD: `vad_filter=True`, `min_silence_duration_ms=300`

#### 3c. TTS-Server (CosyVoice 2 oder Qwen3-TTS)

Für CosyVoice 2 (empfohlen für Voice Cloning):
```bash
git clone https://github.com/FunAudioLLM/CosyVoice.git
cd CosyVoice && pip install -r requirements.txt
```

Für Qwen3-TTS (niedrigste Latenz, 97ms TTFA):
```bash
pip install transformers torch
# Modell: Qwen/Qwen3-TTS-0.6B
```

**Voice Cloning**: Referenz-Audio als WAV bereitstellen (24kHz, mono, 3–10 Sekunden). Beide Modelle unterstützen Zero-Shot-Cloning aus einer einzigen Referenzdatei.

Für vollständige Server-Implementation inkl. Streaming: Lies `references/model-setup.md`.

### Phase 4: Pipecat-Orchestrator

Pipecat verbindet die drei Services zu einer Echtzeit-Pipeline mit WebRTC-Transport.

```bash
pip install "pipecat-ai[silero,websocket,daily]"
```

Für die vollständige Pipeline-Implementation lies `references/pipecat-pipeline.md`.

**Kritische Latenz-Optimierungen:**

1. **Turn Detection**: Silero VAD mit `min_silence_duration_ms=300` (Standard ist 1500ms – das allein spart 1+ Sekunde)
2. **Streaming-Strategie**: `TextAggregationMode.SENTENCE` – TTS beginnt mit dem ersten Satz, während das LLM weitergeneriert
3. **Barge-in**: Bei erkannter Nutzer-Sprache sofort TTS stoppen, Audio-Buffer flushen, LLM-Generation abbrechen
4. **GPU-Sharing**: Drei separate Prozesse mit eigenen CUDA-Kontexten, Kommunikation via localhost HTTP (<1ms Overhead)

### Phase 5: Docker-Container bauen

Für Produktion alles in einen Container packen. Lies `references/dockerfile.md` für das vollständige Dockerfile.

Kernpunkte:
- Base Image: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- Supervisor oder ein Shell-Script startet die drei Services + Pipecat
- Health-Checks auf allen vier Ports
- Volume-Mount für persistenten Modell-Cache

### Phase 6: Client-Integration

Für den Browser-Client gibt es zwei Ansätze:

1. **Daily.co WebRTC** (empfohlen): Pipecat hat native Daily-Integration. Erfordert Daily-Account (Free Tier reicht für Entwicklung).
2. **Raw WebSocket**: Simpler, aber höhere Latenz als WebRTC. Nutzt `pipecat-ai[websocket]`.

Minimaler HTML-Client für WebSocket-Variante: Siehe `references/client-setup.md`.

## Modell-Alternativen

| Wenn... | Dann statt... | Verwende... |
|---------|--------------|-------------|
| Beste deutsche Sprachqualität beim LLM | Qwen3-14B-abliterated | SauerkrautLM-v2-14b-DPO + Heretic-Abliteration |
| Niedrigste TTS-Latenz (97ms) | CosyVoice 2 | Qwen3-TTS-0.6B |
| MIT-Lizenz für TTS | CosyVoice 2 | Chatterbox Multilingual (350M, MIT) |
| Budget unter CHF 0.40/h | L40S | RTX A6000 48GB ($0.33/h) |
| Maximale LLM-Geschwindigkeit | L40S | A100 80GB ($1.19/h) – HBM2e-Bandbreite |
| Deutsch-optimiertes STT | Standard Whisper turbo | `TheChola/whisper-large-v3-turbo-german-faster-whisper` |

## Wichtige Hinweise

- **Kokoro TTS** ist zwar das schnellste Open-Source-TTS-Modell (~82M, <100ms), unterstützt aber **kein Deutsch**. Nicht verwenden.
- **Memory Bandwidth > TFLOPS**: Für autoregressive LLM-Inferenz ist die Speicherbandbreite wichtiger als rohe Rechenleistung. Die A100 (2039 GB/s HBM2e) schlägt die L40S (864 GB/s GDDR6) deutlich beim Token-Decoding.
- **Turn Detection ist die grösste Latenz-Variable**: Schlechtes Endpointing (Standard 1.5s Stille) kann über 1 Sekunde Totzeit hinzufügen – mehr als jede Modell-Optimierung einsparen kann.
- Alle empfohlenen Modelle sind **Apache 2.0** lizenziert (kommerziell nutzbar).
- Voice Cloning Referenz-Audio: 24kHz WAV, mono, 3–10 Sekunden klare Sprache ohne Hintergrundgeräusche.
