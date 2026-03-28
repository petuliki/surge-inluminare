import { useNavigate, useLocation } from 'react-router-dom'

const tabs = [
  { label: 'Curator',  icon: 'mic_none',          path: '/' },
  { label: 'Cerebrum', icon: 'psychology',         path: '/cerebrum' },
  { label: 'Vox',      icon: 'record_voice_over',  path: '/vox' },
]

export default function BottomNav() {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  return (
    <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-2 bg-surface shadow-[0px_-4px_20px_rgba(27,28,25,0.06)]">
      {tabs.map(tab => {
        const active = pathname === tab.path
        return (
          <button
            key={tab.path}
            onClick={() => navigate(tab.path)}
            className={`flex flex-col items-center justify-center pt-2 active:scale-95 duration-150 cursor-pointer transition-opacity ${
              active
                ? 'text-primary border-t-2 border-primary'
                : 'text-tertiary opacity-60 hover:opacity-100'
            }`}
          >
            <span className="material-symbols-outlined">{tab.icon}</span>
            <span className="font-label text-[11px] uppercase tracking-wider font-semibold">{tab.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
