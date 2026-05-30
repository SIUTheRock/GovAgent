import { useState, useEffect, useCallback } from 'react'
import { getAdminChatHistory } from '../../services/api'

function RatingBadge({ rating }) {
  if (rating === 1)  return <span className="text-green-600 font-bold">👍</span>
  if (rating === -1) return <span className="text-red-500 font-bold">👎</span>
  return <span className="text-gray-300">—</span>
}

export default function ChatHistory() {
  const [data, setData] = useState([])
  const [pagination, setPagination] = useState(null)
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const { data: res } = await getAdminChatHistory({ page, q: q || undefined })
      setData(res.data)
      setPagination(res.pagination)
    } catch {
      setData([])
    } finally {
      setLoading(false)
    }
  }, [page, q])

  useEffect(() => { fetch() }, [fetch])

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    setQ(searchInput.trim())
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">💬 Lịch sử cuộc hội thoại</h2>
        {pagination && (
          <span className="text-xs text-gray-500">
            {pagination.total.toLocaleString()} câu hỏi tổng cộng
          </span>
        )}
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Tìm theo nội dung câu hỏi..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
        >
          Tìm
        </button>
        {q && (
          <button
            type="button"
            onClick={() => { setSearchInput(''); setQ(''); setPage(1) }}
            className="text-sm text-gray-500 hover:text-red-600 px-3 py-2 rounded-lg border border-gray-300 hover:border-red-300"
          >
            ✕ Xóa
          </button>
        )}
      </form>

      {/* Table */}
      {loading ? (
        <div className="text-center py-8 text-gray-400">
          <div className="animate-spin text-3xl mb-2">⏳</div>
          <p className="text-sm">Đang tải...</p>
        </div>
      ) : data.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <div className="text-4xl mb-2">💬</div>
          <p>Chưa có cuộc hội thoại nào{q ? ` khớp với "${q}"` : ''}.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {data.map((log) => (
            <div
              key={log.id}
              className="bg-white border border-gray-100 rounded-xl overflow-hidden"
            >
              <div
                className="flex items-start gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setExpanded(expanded === log.id ? null : log.id)}
              >
                {/* Rating */}
                <div className="mt-0.5 w-5 text-center flex-shrink-0">
                  <RatingBadge rating={log.rating} />
                </div>
                {/* Question */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800 font-medium line-clamp-1">{log.question}</p>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                    <span>{new Date(log.created_at).toLocaleString('vi-VN')}</span>
                    {log.response_time_ms && (
                      <span>⚡ {log.response_time_ms.toLocaleString()}ms</span>
                    )}
                    <span className="font-mono text-gray-300">#{log.id}</span>
                  </div>
                </div>
                {/* Expand toggle */}
                <span className="text-gray-300 text-xs flex-shrink-0 mt-1">
                  {expanded === log.id ? '▲' : '▼'}
                </span>
              </div>

              {/* Expanded answer */}
              {expanded === log.id && (
                <div className="border-t border-gray-100 px-4 py-3 bg-blue-50">
                  <p className="text-xs font-medium text-gray-500 mb-1.5">Câu trả lời AI:</p>
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {log.answer || '(Không có câu trả lời)'}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pagination && pagination.pages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50"
          >
            ← Trước
          </button>
          <span className="text-sm text-gray-600">
            Trang {page} / {pagination.pages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(pagination.pages, p + 1))}
            disabled={page === pagination.pages}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50"
          >
            Tiếp →
          </button>
        </div>
      )}
    </div>
  )
}
