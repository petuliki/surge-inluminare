import { useNavigate } from 'react-router-dom'

export default function Header({ backLabel }) {
  const navigate = useNavigate()

  return (
    <header className="flex justify-between items-center w-full px-6 py-6 bg-surface z-10">
      {backLabel ? (
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-secondary hover:text-primary transition-colors"
        >
          <span className="material-symbols-outlined" style={{ fontSize: 20 }}>arrow_back</span>
          <span className="font-label text-xs uppercase tracking-widest font-semibold">{backLabel}</span>
        </button>
      ) : (
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary" style={{ fontSize: 24 }}>menu_book</span>
          <h1 className="font-headline tracking-tight text-3xl font-bold">secretum agentis</h1>
        </div>
      )}
      <div className="font-headline italic uppercase tracking-widest text-primary text-xs">
        surge inluminare
      </div>
    </header>
  )
}
