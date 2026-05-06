import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import ProcedureCard from '../components/ProcedureCard'
import { getCategories, getProcedures, searchProcedures } from '../services/api'

const LEVELS = ['Cấp tỉnh', 'Cấp huyện', 'Cấp xã']

export default function Documents() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [categories, setCategories] = useState([])
  const [procedures, setProcedures] = useState([])
  const [pagination, setPagination] = useState({})
  const [loading, setLoading] = useState(false)

  const q = searchParams.get('q') || ''
  const categoryId = searchParams.get('category') || ''
  const level = searchParams.get('level') || ''
  const page = parseInt(searchParams.get('page') || '1')

  const [inputQ, setInputQ] = useState(q)

  useEffect(() => {
    getCategories().then(({ data }) => setCategories(data.data || [])).catch(() => {})
  }, [])

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      if (q) {
        const { data } = await searchProcedures({ q, category: categoryId || undefined, page, limit: 12 })
        setProcedures(data.data || [])
        setPagination(data.pagination || {})
      } else {
        const { data } = await getProcedures({ page, limit: 12, category: categoryId || undefined, level: level || undefined })
        setProcedures(data.data || [])
        setPagination(data.pagination || {})
      }
    } catch {
      setProcedures([])
    } finally {
      setLoading(false)
    }
  }, [q, categoryId, level, page])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const setParam = (key, value) => {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    next.delete('page')
    setSearchParams(next)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setParam('q', inputQ.trim())
  }

  const goPage = (p) => {
    const next = new URLSearchParams(searchParams)
    next.set('page', p)
    setSearchParams(next)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const selectedCategory = categories.find((c) => String(c.id) === categoryId)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          {q ? `Kết quả tìm kiếm: "${q}"` : selectedCategory ? `${selectedCategory.name}` : 'Tất cả Thủ tục Hành chính'}
        </h1>
        {pagination.total !== undefined && (
          <p className="text-sm text-gray-500 mt-1">
            Tìm thấy <strong>{pagination.total}</strong> thủ tục
          </p>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar filters */}
        <aside className="lg:w-56 shrink-0">
          {/* Search */}
          <form onSubmit={handleSearch} className="mb-5">
            <div className="flex gap-2">
              <input
                value={inputQ}
                onChange={(e) => setInputQ(e.target.value)}
                placeholder="Tìm kiếm..."
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <button type="submit" className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700">
                🔍
              </button>
            </div>
          </form>

          {/* Category filter */}
          <div className="mb-5">
            <h3 className="font-semibold text-gray-700 text-sm mb-2">Lĩnh vực</h3>
            <div className="space-y-1">
              <button
                onClick={() => setParam('category', '')}
                className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${!categoryId ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
              >
                Tất cả lĩnh vực
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setParam('category', cat.id)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${String(cat.id) === categoryId ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>

          {/* Level filter */}
          <div>
            <h3 className="font-semibold text-gray-700 text-sm mb-2">Cấp thực hiện</h3>
            <div className="space-y-1">
              <button
                onClick={() => setParam('level', '')}
                className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${!level ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
              >
                Tất cả cấp
              </button>
              {LEVELS.map((l) => (
                <button
                  key={l}
                  onClick={() => setParam('level', l)}
                  className={`w-full text-left px-3 py-1.5 rounded-lg text-sm transition-colors ${level === l ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>

          {/* Chat link */}
          <div className="mt-6 bg-blue-50 rounded-xl p-4 text-center">
            <p className="text-xs text-gray-600 mb-2">Không tìm được? Hỏi trợ lý AI</p>
            <Link
              to="/chat"
              className="inline-block bg-blue-600 text-white text-xs px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              🤖 Hỏi ngay
            </Link>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="bg-gray-100 rounded-xl h-36 animate-pulse" />
              ))}
            </div>
          ) : procedures.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <div className="text-4xl mb-3">🔍</div>
              <p className="font-medium">Không tìm thấy thủ tục phù hợp.</p>
              <p className="text-sm mt-1">Hãy thử từ khóa khác hoặc hỏi trợ lý AI.</p>
              <Link to="/chat" className="inline-block mt-4 bg-blue-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-blue-700">
                🤖 Hỏi trợ lý AI
              </Link>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                {procedures.map((p) => (
                  <ProcedureCard key={p.id} procedure={p} />
                ))}
              </div>

              {/* Pagination */}
              {pagination.totalPages > 1 && (
                <div className="flex justify-center gap-2 mt-8">
                  <button
                    onClick={() => goPage(page - 1)}
                    disabled={page <= 1}
                    className="px-3 py-2 rounded-lg border text-sm disabled:opacity-40 hover:bg-gray-50 transition-colors"
                  >
                    ← Trước
                  </button>
                  {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                    const p = Math.max(1, Math.min(pagination.totalPages - 4, page - 2)) + i
                    return (
                      <button
                        key={p}
                        onClick={() => goPage(p)}
                        className={`px-3 py-2 rounded-lg border text-sm transition-colors ${page === p ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'}`}
                      >
                        {p}
                      </button>
                    )
                  })}
                  <button
                    onClick={() => goPage(page + 1)}
                    disabled={page >= pagination.totalPages}
                    className="px-3 py-2 rounded-lg border text-sm disabled:opacity-40 hover:bg-gray-50 transition-colors"
                  >
                    Sau →
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  )
}
