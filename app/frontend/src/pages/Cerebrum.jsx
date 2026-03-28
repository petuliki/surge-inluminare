import { useState, useEffect } from 'react'
import BottomNav from '../components/BottomNav'
import Header from '../components/Header'
import {
  useCharacters,
  useCharacterDetail,
  useSystemPrompt,
  createCharacter,
  updateCharacter,
  deleteCharacter,
} from '../hooks/useApi'

const EMPTY_CHAR = {
  name: '',
  type: 'Rollenspielcharakter',
  response_length: 3,
  traits: '',
  appearance: '',
  speech: '',
}

function CharacterForm({ initial, onSave, onCancel, saving }) {
  const [data, setData] = useState(initial || EMPTY_CHAR)
  const set = (field, value) => setData(prev => ({ ...prev, [field]: value }))

  return (
    <div className="space-y-5 bg-surface-container-low p-5">
      <div>
        <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">Name</label>
        <input
          value={data.name}
          onChange={e => set('name', e.target.value)}
          disabled={!!initial}
          className="w-full bg-transparent border-b border-outline-variant/40 focus:border-primary focus:border-b-2 py-2 font-headline text-lg italic outline-none transition-colors disabled:opacity-50"
        />
      </div>

      <div>
        <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">Typ</label>
        <select
          value={data.type}
          onChange={e => set('type', e.target.value)}
          className="w-full bg-transparent border-b border-outline-variant/40 focus:border-primary py-2 font-body text-sm outline-none"
        >
          <option value="Rollenspielcharakter">Rollenspielcharakter</option>
          <option value="AI Agent">AI Agent</option>
        </select>
      </div>

      <div>
        <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
          Antwortlaenge (Saetze)
        </label>
        <input
          type="number"
          min="1"
          max="20"
          value={data.response_length}
          onChange={e => set('response_length', parseInt(e.target.value) || 3)}
          className="w-24 bg-transparent border-b border-outline-variant/40 focus:border-primary focus:border-b-2 py-2 font-body text-sm outline-none transition-colors"
        />
      </div>

      <div>
        <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
          Charaktereigenschaften
        </label>
        <textarea
          value={data.traits}
          onChange={e => set('traits', e.target.value)}
          rows={3}
          className="w-full bg-transparent border-b border-outline-variant/40 focus:border-primary focus:border-b-2 p-2 font-body text-sm outline-none transition-colors resize-none"
        />
      </div>

      <div>
        <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">Aussehen</label>
        <textarea
          value={data.appearance}
          onChange={e => set('appearance', e.target.value)}
          rows={3}
          className="w-full bg-transparent border-b border-outline-variant/40 focus:border-primary focus:border-b-2 p-2 font-body text-sm outline-none transition-colors resize-none"
        />
      </div>

      <div>
        <label className="block font-label text-[10px] uppercase tracking-widest text-secondary mb-1">
          Besonderheiten in der Sprache
        </label>
        <textarea
          value={data.speech}
          onChange={e => set('speech', e.target.value)}
          rows={3}
          className="w-full bg-transparent border-b border-outline-variant/40 focus:border-primary focus:border-b-2 p-2 font-body text-sm outline-none transition-colors resize-none"
        />
      </div>

      <div className="flex gap-3 pt-2">
        <button
          onClick={() => onSave(data)}
          disabled={saving || !data.name.trim()}
          className="flex-1 py-3 bg-gradient-to-r from-primary to-primary-container text-on-primary font-label text-xs font-bold tracking-[0.15em] uppercase active:scale-95 transition-transform disabled:opacity-40"
        >
          {saving ? 'Salvare...' : 'Servare'}
        </button>
        {onCancel && (
          <button
            onClick={onCancel}
            className="py-3 px-6 bg-surface-container-high text-on-surface font-label text-xs font-bold tracking-[0.15em] uppercase active:scale-95 transition-transform"
          >
            Abire
          </button>
        )}
      </div>
    </div>
  )
}

function CharacterItem({ name, onEdit, onDelete }) {
  const detail = useCharacterDetail(name)
  const [showEdit, setShowEdit] = useState(false)
  const [saving, setSaving] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const handleSave = async (data) => {
    setSaving(true)
    try {
      await updateCharacter(name, data)
      setShowEdit(false)
      onEdit()
    } catch (e) {
      console.error(e)
    }
    setSaving(false)
  }

  const handleDelete = async () => {
    try {
      await deleteCharacter(name)
      onDelete()
    } catch (e) {
      console.error(e)
    }
  }

  if (showEdit && detail) {
    return (
      <CharacterForm
        initial={detail}
        onSave={handleSave}
        onCancel={() => setShowEdit(false)}
        saving={saving}
      />
    )
  }

  return (
    <div className="py-5 px-4 bg-surface-container-low">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <p className="font-headline italic text-lg leading-tight">
            {detail?.name || name.replace(/_/g, ' ')}
          </p>
          {detail?.type && (
            <p className="font-label text-[10px] uppercase tracking-widest text-secondary mt-0.5">
              {detail.type}
            </p>
          )}
          {detail?.traits && (
            <p className="font-body text-[11px] text-secondary mt-1 leading-relaxed line-clamp-2">
              {detail.traits}
            </p>
          )}
        </div>
        <div className="flex gap-3 flex-shrink-0 pt-1">
          <button
            onClick={() => setShowEdit(true)}
            className="font-label text-[10px] uppercase tracking-widest text-primary hover:underline"
          >
            Edere
          </button>
          {confirmDelete ? (
            <button
              onClick={handleDelete}
              className="font-label text-[10px] uppercase tracking-widest text-error hover:underline"
            >
              Confirmare?
            </button>
          ) : (
            <button
              onClick={() => setConfirmDelete(true)}
              className="font-label text-[10px] uppercase tracking-widest text-secondary hover:text-error hover:underline"
            >
              Delere
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Cerebrum() {
  const { characters, reload } = useCharacters()
  const { content: systemPrompt, setContent: setSystemPrompt, save: savePrompt } = useSystemPrompt()
  const [saveStatus, setSaveStatus] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [creating, setCreating] = useState(false)

  const handleSavePrompt = async () => {
    setSaveStatus('saving')
    const ok = await savePrompt(systemPrompt)
    setSaveStatus(ok ? 'saved' : 'error')
    setTimeout(() => setSaveStatus(null), 2500)
  }

  const handleCreate = async (data) => {
    setCreating(true)
    try {
      await createCharacter(data)
      setShowCreate(false)
      reload()
    } catch (e) {
      console.error(e)
    }
    setCreating(false)
  }

  return (
    <div className="bg-surface text-on-surface font-body min-h-screen flex flex-col">
      <div className="absolute inset-0 opacity-5 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/natural-paper.png')]" />

      <Header backLabel="Curator" />

      <main className="flex-grow px-8 pt-4 pb-32 max-w-sm mx-auto w-full space-y-12">
        <div>
          <h1 className="font-headline text-3xl font-bold mb-1">Cerebrum</h1>
          <p className="font-label text-xs uppercase tracking-[0.2em] text-secondary">
            Cognitio et Configuratio
          </p>
        </div>

        {/* System Prompt */}
        <section>
          <p className="font-label text-[10px] uppercase tracking-widest text-secondary mb-3">
            Promptum Systematis
          </p>
          <textarea
            value={systemPrompt}
            onChange={e => setSystemPrompt(e.target.value)}
            rows={10}
            className="w-full bg-surface-container-low border-b border-outline-variant/40 focus:border-primary focus:border-b-2 p-4 font-mono text-sm outline-none transition-colors resize-none"
          />
          <div className="flex items-center justify-between mt-3">
            <span className={`font-label text-[10px] uppercase tracking-widest transition-opacity ${
              saveStatus ? 'opacity-100' : 'opacity-0'
            } ${saveStatus === 'error' ? 'text-error' : 'text-secondary'}`}>
              {saveStatus === 'saving' ? 'Salvare...' : saveStatus === 'saved' ? 'Servatum est' : saveStatus === 'error' ? 'Error' : ''}
            </span>
            <button
              onClick={handleSavePrompt}
              disabled={saveStatus === 'saving'}
              className="py-3 px-8 bg-gradient-to-r from-primary to-primary-container text-on-primary font-label text-xs font-bold tracking-[0.15em] uppercase active:scale-95 transition-transform disabled:opacity-40"
            >
              Servare
            </button>
          </div>
        </section>

        {/* Characters */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <p className="font-label text-[10px] uppercase tracking-widest text-secondary">
              Agentes {'\u2014'} {characters.length} Charakter{characters.length !== 1 ? 'e' : ''}
            </p>
            <div className="flex gap-3">
              <button onClick={reload} className="text-tertiary hover:text-primary transition-colors">
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>refresh</span>
              </button>
              <button
                onClick={() => setShowCreate(!showCreate)}
                className="text-tertiary hover:text-primary transition-colors"
              >
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                  {showCreate ? 'close' : 'add'}
                </span>
              </button>
            </div>
          </div>

          {showCreate && (
            <div className="mb-4">
              <CharacterForm
                onSave={handleCreate}
                onCancel={() => setShowCreate(false)}
                saving={creating}
              />
            </div>
          )}

          <div className="space-y-0">
            {characters.map(name => (
              <CharacterItem
                key={name}
                name={name}
                onEdit={reload}
                onDelete={reload}
              />
            ))}
          </div>
        </section>
      </main>

      <BottomNav />
    </div>
  )
}
