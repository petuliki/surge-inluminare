import logoUrl from '../assets/logo.png'

const STATE_CONFIG = {
  dormit:     { ringClass: 'pulse-ring',      ringColor: 'border-primary/30' },
  auscultans: { ringClass: 'pulse-ring-fast', ringColor: 'border-primary' },
  cogitans:   { ringClass: 'pulse-ring-fast', ringColor: 'border-primary' },
  loquitur:   { ringClass: 'pulse-ring-glow', ringColor: 'border-primary' },
}

export default function TheSeal({ state = 'dormit' }) {
  const cfg = STATE_CONFIG[state] || STATE_CONFIG.dormit

  return (
    <div className="relative mb-12">
      <div className={`absolute inset-0 rounded-full border-2 ${cfg.ringColor} ${cfg.ringClass}`} />
      <div
        className={`absolute -inset-4 rounded-full border border-primary/20 ${cfg.ringClass}`}
        style={{ animationDelay: '1.5s' }}
      />
      <div className="relative w-48 h-48 bg-surface-container-lowest rounded-full flex items-center justify-center wax-seal-shadow overflow-hidden border-4 border-surface-container-high">
        <img src={logoUrl} alt="Secretum Agentis" className="w-32 h-32 object-contain" />
      </div>
    </div>
  )
}
