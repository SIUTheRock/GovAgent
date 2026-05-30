import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [q, setQ] = useState('')
  const navigate = useNavigate()
  const { isAuthenticated, logout } = useAuth()

  const handleSearch = (e) => {
    e.preventDefault()
    if (q.trim()) {
      navigate(`/documents?q=${encodeURIComponent(q.trim())}`)
      setQ('')
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
    setMenuOpen(false)
  }

  const navClass = ({ isActive }) =>
    isActive
      ? 'text-blue-600 font-semibold border-b-2 border-blue-600 pb-0.5'
      : 'text-gray-700 hover:text-blue-600 transition-colors'

  return (
    <nav className="bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold text-blue-700 text-lg">
          <span className="text-2xl">🏛️</span>
          <span className="hidden sm:block">TTHC TP.HCM</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-6">
          <NavLink to="/" end className={navClass}>Trang chủ</NavLink>
          <NavLink to="/chat" className={navClass}>Trợ lý AI</NavLink>
          <NavLink to="/documents" className={navClass}>Thủ tục</NavLink>
          {isAuthenticated && (
            <NavLink to="/admin" className={navClass}>Quản trị</NavLink>
          )}
        </div>

        {/* Right side: Search + Auth */}
        <div className="hidden md:flex items-center gap-3">
          <form onSubmit={handleSearch} className="flex items-center gap-2">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Tìm thủ tục..."
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700 transition-colors"
            >
              Tìm
            </button>
          </form>

          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <span className="text-xs bg-green-100 text-green-700 font-medium px-2 py-1 rounded-full">
                ✅ Admin
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-red-600 transition-colors px-2 py-1 rounded hover:bg-red-50"
              >
                Đăng xuất
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="text-sm text-gray-500 hover:text-blue-600 transition-colors flex items-center gap-1 px-2 py-1 rounded hover:bg-blue-50"
            >
              🔐 <span>Admin</span>
            </Link>
          )}
        </div>

        {/* Mobile burger */}
        <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
          <span className="text-xl">{menuOpen ? '✕' : '☰'}</span>
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden bg-white border-t px-4 py-3 flex flex-col gap-3">
          <NavLink to="/" end className={navClass} onClick={() => setMenuOpen(false)}>Trang chủ</NavLink>
          <NavLink to="/chat" className={navClass} onClick={() => setMenuOpen(false)}>Trợ lý AI</NavLink>
          <NavLink to="/documents" className={navClass} onClick={() => setMenuOpen(false)}>Thủ tục</NavLink>
          {isAuthenticated && (
            <NavLink to="/admin" className={navClass} onClick={() => setMenuOpen(false)}>Quản trị</NavLink>
          )}
          <form onSubmit={(e) => { handleSearch(e); setMenuOpen(false) }} className="flex gap-2">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Tìm thủ tục..."
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button type="submit" className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm">Tìm</button>
          </form>
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:underline text-left"
            >
              🚪 Đăng xuất
            </button>
          ) : (
            <Link to="/login" onClick={() => setMenuOpen(false)} className="text-sm text-blue-600 hover:underline">
              🔐 Đăng nhập quản trị
            </Link>
          )}
        </div>
      )}
    </nav>
  )
}
