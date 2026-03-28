import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import Curator from './pages/Curator'
import Cerebrum from './pages/Cerebrum'
import Vox from './pages/Vox'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Curator />} />
        <Route path="/cerebrum" element={<Cerebrum />} />
        <Route path="/vox" element={<Vox />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
