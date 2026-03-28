import { useState, useRef } from 'react'
import BottomNav from '../components/BottomNav'
import Header from '../components/Header'
import { useVoices, deleteVoice } from '../hooks/useApi'

export default function Vox() {
  const { voices, reload } = useVoices()
  const [voiceName, setVoiceName] = useState('')
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState(null)
  const [message, setMessage] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(null)
  const fileInputRef = useRef()
  const [dragging, setDragging] = useState(false)

  const handleFile = (f) => {
    if (!f) return
    const ext = f.name.split('.').pop().toLowerCase()
    if (!['wav', 'mp3', 'm4a', 'ogg', 'opus'].includes(ext)) {
      setStatus('error')
      setMessage('Nicht unterstuetztes Format. Erlaubt: WAV, MP3, M4A, OGG, OPUS')
      return
    }
    setFile(f)
    setMessage('')
    setStatus(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!voiceName.trim() || !file) return

    setStatus('loading')
    setMessage('')

    const form = new FormData()
    form.append('voice_name', voiceName.trim())
    form.append('audio_file', file)

    try {
      const res = await fetch('/api/voices/clone', { method: 'POST', body: form })
      const data = await res.json()
      if (res.ok) {
        setStatus('success')
        setMessage(`Vox '${data.voice_name}' in archivum addita`)
        setVoiceName('')
        setFile(null)
        reload()
      } else {
        setStatus('error')
        setMessage(data.detail || 'Fehler beim Klonen')
      }
    } catch {
      setStatus('error')
      setMessage('Verbindungsfehler')
    }
  }

  const handleDelete = async (name) => {
    try {
      await deleteVoice(name)
      setConfirmDelete(null)
      reload()
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="bg-surface text-on-surface font-body min-h-screen flex flex-col">
      <div className="absolute inset-0 opacity-5 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/natural-paper.png')]" />

      <Header backLabel="Curator" />

      <main className="flex-grow px-8 pt-4 pb-32 max-w-sm mx-auto w-full">

        <h1 className="font-headline text-3xl font-bold mb-1">Vox</h1>
        <p className="font-label text-xs uppercase tracking-[0.2em] text-secondary mb-10">
          Clonatio et Administratio Vocis
        </p>

        {/* Clone form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          <div>
            <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
              Nomen Vocis
            </label>
            <input
              type="text"
              value={voiceName}
              onChange={e => setVoiceName(e.target.value)}
              placeholder="z.B. bariton_profundus"
              className="w-full bg-transparent border-b border-outline-variant/40 focus:border-primary focus:border-b-2 py-2 font-headline text-lg italic outline-none transition-colors placeholder:text-secondary/40"
            />
          </div>

          <div>
            <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
              Speculum Vocis
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
              className={`cursor-pointer bg-surface-container-low p-8 flex flex-col items-center gap-3 transition-colors ${
                dragging ? 'bg-surface-container-high' : ''
              }`}
            >
              <span className="material-symbols-outlined text-tertiary" style={{ fontSize: 36 }}>audio_file</span>
              {file ? (
                <span className="font-label text-sm text-on-surface">{file.name}</span>
              ) : (
                <span className="font-label text-xs text-secondary text-center">
                  Audio ablegen oder klicken<br />
                  <span className="text-[10px] uppercase tracking-widest">WAV {'\u00B7'} MP3 {'\u00B7'} OPUS {'\u00B7'} 3-10 Sek.</span>
                </span>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".wav,.mp3,.m4a,.ogg,.opus,audio/*"
              onChange={e => handleFile(e.target.files[0])}
              className="hidden"
            />
          </div>

          {message && (
            <p className={`font-label text-xs tracking-wide ${
              status === 'error' ? 'text-error' : 'text-secondary'
            }`}>
              {message}
            </p>
          )}

          <button
            type="submit"
            disabled={!voiceName.trim() || !file || status === 'loading'}
            className="w-full py-5 bg-gradient-to-r from-primary to-primary-container text-on-primary font-label text-sm font-bold tracking-[0.15em] uppercase shadow-lg active:scale-95 transition-transform disabled:opacity-40"
          >
            {status === 'loading' ? 'Creatio...' : 'Creatio'}
          </button>
        </form>

        {/* Voices archive */}
        {voices.length > 0 && (
          <div className="mt-14">
            <p className="font-label text-[10px] uppercase tracking-widest text-secondary mb-4">
              Voces in Archivum
            </p>
            <div className="space-y-0">
              {voices.map((v, i) => (
                <div
                  key={v}
                  className={`flex items-center justify-between py-4 ${
                    i % 2 === 0 ? 'bg-surface' : 'bg-surface-container-low'
                  } px-2`}
                >
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-tertiary" style={{ fontSize: 18 }}>
                      graphic_eq
                    </span>
                    <span className="font-headline italic text-base">{v.replace(/_/g, ' ')}</span>
                  </div>
                  {confirmDelete === v ? (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDelete(v)}
                        className="font-label text-[10px] uppercase tracking-widest text-error hover:underline"
                      >
                        Confirmare?
                      </button>
                      <button
                        onClick={() => setConfirmDelete(null)}
                        className="font-label text-[10px] uppercase tracking-widest text-secondary hover:underline"
                      >
                        Abire
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirmDelete(v)}
                      className="text-secondary hover:text-error transition-colors"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 16 }}>delete</span>
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <BottomNav />
    </div>
  )
}
