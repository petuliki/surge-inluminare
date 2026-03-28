import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import BottomNav from '../components/BottomNav'
import Header from '../components/Header'
import TheSeal from '../components/TheSeal'
import { useCharacters, useVoices, useConfig, useCharacterDetail } from '../hooks/useApi'
import { usePipecat } from '../hooks/usePipecat'

const STATE_LABELS = {
  dormit: 'status: dormit',
  auscultans: 'status: auscultans',
  cogitans: 'status: cogitans',
  loquitur: 'status: loquitur',
}

export default function Curator() {
  const navigate = useNavigate()
  const [agentState, setAgentState] = useState('dormit')
  const [transcript, setTranscript] = useState([])

  const { characters } = useCharacters()
  const { voices } = useVoices()
  const { config, update: updateConfig } = useConfig()
  const charDetail = useCharacterDetail(config.character)

  const onTranscript = useCallback((text, role) => {
    setTranscript(prev => [...prev.slice(-20), { role, text }])
  }, [])
  const onState = useCallback((state) => setAgentState(state), [])
  const onError = useCallback((msg) => console.error('Agent error:', msg), [])

  const { connect, disconnect, connected } = usePipecat({ onTranscript, onState, onError })

  const displayName = charDetail?.name || (config.character || '').replace(/_/g, ' ') || '\u2014'

  const handleConnect = () => {
    connect(config.character, config.voice)
  }

  return (
    <div className="bg-surface text-on-surface font-body selection:bg-primary-fixed min-h-screen flex flex-col">
      <div className="absolute inset-0 opacity-5 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/natural-paper.png')]" />

      <Header />

      <main className="flex-grow flex flex-col items-center justify-center px-8 relative overflow-hidden pb-32">
        <TheSeal state={agentState} />

        {/* Status & Identity */}
        <div className="text-center mb-10">
          <span className="font-label text-xs uppercase tracking-[0.2em] text-secondary mb-2 block">
            {STATE_LABELS[agentState] || STATE_LABELS.dormit}
          </span>
          <h2 className="font-headline text-4xl italic text-on-surface">{displayName}</h2>
        </div>

        {/* Transcript */}
        {transcript.length > 0 && (
          <div className="w-full max-w-xs mb-8 space-y-2">
            {transcript.slice(-3).map((t, i) => (
              <div key={i} className={`text-xs font-body leading-relaxed ${
                t.role === 'user' ? 'text-secondary text-right' : 'text-on-surface'
              }`}>
                {t.text}
              </div>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="w-full space-y-4 max-w-xs mb-12">
          <button
            onClick={handleConnect}
            disabled={connected}
            className="w-full py-5 bg-gradient-to-r from-primary to-primary-container text-on-primary font-label text-sm font-bold tracking-[0.15em] uppercase shadow-lg active:scale-95 transition-transform disabled:opacity-40"
          >
            inchoate
          </button>
          <button
            onClick={disconnect}
            disabled={!connected}
            className="w-full py-5 bg-surface-container-high text-on-surface font-label text-sm font-bold tracking-[0.15em] uppercase active:scale-95 transition-transform disabled:opacity-40"
          >
            finisci
          </button>
        </div>

        {/* Selectors */}
        <div className="w-full max-w-xs space-y-6">
          {/* AGENTIS */}
          <div className="relative group">
            <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
              agentis
            </label>
            <div className="flex items-center justify-between border-b border-outline-variant/30 py-2">
              <select
                value={config.character || ''}
                onChange={e => updateConfig({ character: e.target.value })}
                className="bg-transparent font-headline text-lg italic w-full appearance-none outline-none cursor-pointer"
              >
                <option value="">{'\u2014'}</option>
                {characters.map(c => (
                  <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>
                ))}
              </select>
              <span className="material-symbols-outlined text-tertiary pointer-events-none">expand_more</span>
            </div>
          </div>

          {/* VOX */}
          <div className="relative group">
            <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
              vox
            </label>
            <div className="flex items-center justify-between border-b border-outline-variant/30 py-2">
              <select
                value={config.voice || ''}
                onChange={e => updateConfig({ voice: e.target.value || null })}
                className="bg-transparent font-headline text-lg italic w-full appearance-none outline-none cursor-pointer"
              >
                <option value="">{'\u2014 keine Stimme \u2014'}</option>
                {voices.map(v => (
                  <option key={v} value={v}>{v.replace(/_/g, ' ')}</option>
                ))}
              </select>
              <span className="material-symbols-outlined text-tertiary pointer-events-none">expand_more</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-surface-container-low px-8 pt-8 pb-20">
        <div className="flex flex-col gap-6 max-w-xs mx-auto">
          <button
            onClick={() => navigate('/vox')}
            className="w-full py-4 border-2 border-primary text-primary font-label text-xs font-bold tracking-[0.2em] uppercase hover:bg-primary hover:text-on-primary transition-all flex items-center justify-center gap-3"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>record_voice_over</span>
            VOX FURANTUR
          </button>
        </div>
      </footer>

      <BottomNav />
    </div>
  )
}
