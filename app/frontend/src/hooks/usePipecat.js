import { useRef, useCallback, useState } from 'react'

const SAMPLE_RATE = 16000
const CHUNK_SAMPLES = 2048

/**
 * Audio playback queue for seamless WAV chunk playback.
 */
class AudioQueue {
  constructor() {
    this.ctx = new AudioContext({ sampleRate: 24000 })
    this.nextTime = 0
  }

  async enqueue(base64Wav) {
    const binary = atob(base64Wav)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)

    const buffer = await this.ctx.decodeAudioData(bytes.buffer)
    const source = this.ctx.createBufferSource()
    source.buffer = buffer
    source.connect(this.ctx.destination)

    const now = this.ctx.currentTime
    const startAt = Math.max(now, this.nextTime)
    source.start(startAt)
    this.nextTime = startAt + buffer.duration
  }

  flush() {
    this.nextTime = 0
  }

  close() {
    this.ctx.close()
  }
}

export function usePipecat({ onTranscript, onState, onError }) {
  const wsRef = useRef(null)
  const processorRef = useRef(null)
  const audioCtxRef = useRef(null)
  const audioQueueRef = useRef(null)
  const sendingRef = useRef(true)
  const keepaliveRef = useRef(null)
  const [connected, setConnected] = useState(false)

  const connect = useCallback((character, voice) => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const params = new URLSearchParams()
    if (character) params.set('character', character)
    if (voice) params.set('voice', voice)
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/bot?${params}`)
    ws.binaryType = 'arraybuffer'
    wsRef.current = ws

    audioQueueRef.current = new AudioQueue()

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        if (msg.type === 'audio_chunk' && msg.data) {
          audioQueueRef.current?.enqueue(msg.data).catch(console.error)
        }

        if (msg.type === 'state') {
          onState?.(msg.state)
          sendingRef.current = (msg.state === 'auscultans')
        }

        if (msg.type === 'barge_in') {
          audioQueueRef.current?.flush()
        }

        if (msg.type === 'transcript') {
          onTranscript?.(msg.text, msg.role || 'user')
        }

        if (msg.type === 'error') {
          onError?.(msg.message)
        }
      } catch (e) {
        console.error('WS parse error', e)
      }
    }

    ws.onopen = async () => {
      setConnected(true)
      keepaliveRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN && !sendingRef.current) {
          ws.send(new ArrayBuffer(0))
        }
      }, 15000)
      await startMicrophone(ws)
    }

    ws.onclose = () => {
      setConnected(false)
      clearInterval(keepaliveRef.current)
      stopMicrophone()
      audioQueueRef.current?.close()
      audioQueueRef.current = null
      onState?.('dormit')
    }

    ws.onerror = () => {
      onError?.('Verbindungsfehler')
    }
  }, [onTranscript, onState, onError])

  const disconnect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'stop' }))
    }
    wsRef.current?.close()
    wsRef.current = null
  }, [])

  async function startMicrophone(ws) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: SAMPLE_RATE, channelCount: 1, echoCancellation: true },
      })

      const ctx = new AudioContext({ sampleRate: SAMPLE_RATE })
      audioCtxRef.current = ctx
      if (ctx.state === 'suspended') await ctx.resume()

      const source = ctx.createMediaStreamSource(stream)
      const processor = ctx.createScriptProcessor(CHUNK_SAMPLES, 1, 1)
      processorRef.current = processor

      processor.onaudioprocess = (e) => {
        if (ws.readyState !== WebSocket.OPEN) return
        if (!sendingRef.current) return
        const float32 = e.inputBuffer.getChannelData(0)
        const pcm16 = new Int16Array(float32.length)
        for (let i = 0; i < float32.length; i++) {
          const s = Math.max(-1, Math.min(1, float32[i]))
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
        }
        ws.send(pcm16.buffer)
      }

      source.connect(processor)
      processor.connect(ctx.destination)
    } catch (e) {
      onError?.('Mikrofon-Zugriff verweigert')
      console.error(e)
    }
  }

  function stopMicrophone() {
    processorRef.current?.disconnect()
    processorRef.current = null
    audioCtxRef.current?.close()
    audioCtxRef.current = null
  }

  return { connect, disconnect, connected }
}
