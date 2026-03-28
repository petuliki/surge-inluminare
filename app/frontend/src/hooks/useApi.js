import { useState, useEffect } from 'react'

export function useCharacters() {
  const [characters, setCharacters] = useState([])
  const [loading, setLoading] = useState(true)

  const reload = () => {
    setLoading(true)
    fetch('/api/characters')
      .then(r => r.json())
      .then(d => setCharacters(d.characters || []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])
  return { characters, loading, reload }
}

export function useCharacterDetail(name) {
  const [detail, setDetail] = useState(null)

  useEffect(() => {
    if (!name) { setDetail(null); return }
    fetch(`/api/characters/${name}`)
      .then(r => r.ok ? r.json() : null)
      .then(setDetail)
      .catch(console.error)
  }, [name])

  return detail
}

export async function createCharacter(data) {
  const res = await fetch('/api/characters', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Fehler beim Erstellen')
  }
  return res.json()
}

export async function updateCharacter(name, data) {
  const res = await fetch(`/api/characters/${name}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Fehler beim Aktualisieren')
  }
  return res.json()
}

export async function deleteCharacter(name) {
  const res = await fetch(`/api/characters/${name}`, { method: 'DELETE' })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Fehler beim Loeschen')
  }
  return res.json()
}

export function useVoices() {
  const [voices, setVoices] = useState([])
  const [loading, setLoading] = useState(true)

  const reload = () => {
    setLoading(true)
    fetch('/api/voices')
      .then(r => r.json())
      .then(d => setVoices(d.voices || []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(reload, [])
  return { voices, loading, reload }
}

export async function deleteVoice(name) {
  const res = await fetch(`/api/voices/${name}`, { method: 'DELETE' })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Fehler beim Loeschen')
  }
  return res.json()
}

export function useConfig() {
  const [config, setConfig] = useState({ character: null, voice: null })

  useEffect(() => {
    fetch('/api/config')
      .then(r => r.json())
      .then(setConfig)
      .catch(console.error)
  }, [])

  const update = (patch) => {
    fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    })
      .then(r => r.json())
      .then(setConfig)
      .catch(console.error)
  }

  return { config, update }
}

export function useSystemPrompt() {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/system-prompt')
      .then(r => r.json())
      .then(d => setContent(d.content || ''))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const save = async (text) => {
    const res = await fetch('/api/system-prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: text }),
    })
    return res.ok
  }

  return { content, setContent, save, loading }
}
