import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getAdminStats } from '../services/api'

function StatCard({ icon, label, value, sub, color = 'blue' }) {
  const colors = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  }
  return (
    <div className={`rounded-xl border p-5 ${colors[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-3xl font-bold">{value}</p>
      <p className="font-medium mt-1">{label}</p>
      {sub && <p className="text-xs opacity-70 mt-0.5">{sub}</p>}
    </div>
  )
}

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getAdminStats()
      .then(({ data }) => setStats(data))
      .catch(() => setError('Không thể tải thống kê. Vui lòng thử lại.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin text-4xl mb-3">⏳</div>
        <p className="text-gray-500">Đang tải thống kê...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600">{error}</p>
        <button onClick={() => window.location.reload()} className="mt-3 text-blue-600 hover:underline text-sm">
          Thử lại
        </button>
      </div>
    )
  }

  const positiveRate =
    stats.rating.positive + stats.rating.negative > 0
      ? Math.round((stats.rating.positive / (stats.rating.positive + stats.rating.negative)) * 100)
      : null

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">📊 Bảng điều khiển quản trị</h1>
        <button
          onClick={() => window.location.reload()}
          className="text-sm text-blue-600 hover:underline flex items-center gap-1"
        >
          🔄 Làm mới
        </button>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon="💬"
          label="Tổng lượt hỏi"
          value={stats.total_chats.toLocaleString()}
          color="blue"
        />
        <StatCard
          icon="📅"
          label="Hôm nay"
          value={stats.today_chats.toLocaleString()}
          sub="lượt chat"
          color="green"
        />
        <StatCard
          icon="⚡"
          label="Thời gian p/hồi TB"
          value={`${(stats.avg_response_time_ms / 1000).toFixed(1)}s`}
          color="yellow"
        />
        <StatCard
          icon="👍"
          label="Độ hài lòng"
          value={positiveRate !== null ? `${positiveRate}%` : 'N/A'}
          sub={`${stats.rating.positive} hữu ích / ${stats.rating.negative} không hữu ích`}
          color="purple"
        />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Top procedures */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            🔥 Thủ tục được hỏi nhiều nhất
          </h2>
          {stats.top_procedures.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">Chưa có dữ liệu</p>
          ) : (
            <div className="space-y-3">
              {stats.top_procedures.map((p, idx) => (
                <div key={p.id} className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center shrink-0">
                    {idx + 1}
                  </span>
                  <Link
                    to={`/documents/${p.id}`}
                    className="flex-1 text-sm text-blue-700 hover:underline truncate"
                  >
                    {p.name}
                  </Link>
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full shrink-0">
                    {p.mention_count} lần
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent chat logs */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            🕐 Câu hỏi gần đây
          </h2>
          {stats.recent_logs.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">Chưa có dữ liệu</p>
          ) : (
            <div className="space-y-2">
              {stats.recent_logs.map((log) => (
                <div key={log.id} className="flex items-start gap-2 py-2 border-b border-gray-100 last:border-0">
                  <span className="text-xs mt-0.5">
                    {log.rating === 1 ? '👍' : log.rating === -1 ? '👎' : '💬'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-700 truncate">{log.question}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(log.created_at).toLocaleString('vi-VN')}
                      {log.response_time_ms && ` · ${(log.response_time_ms / 1000).toFixed(1)}s`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Rating breakdown */}
      <div className="mt-6 bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-semibold text-gray-800 mb-4">📈 Phân tích đánh giá người dùng</h2>
        <div className="flex gap-6 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-400" />
            <span className="text-sm text-gray-700">Hữu ích: <strong>{stats.rating.positive}</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-400" />
            <span className="text-sm text-gray-700">Không hữu ích: <strong>{stats.rating.negative}</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-300" />
            <span className="text-sm text-gray-700">Chưa đánh giá: <strong>{stats.rating.no_rating}</strong></span>
          </div>
        </div>
        {stats.total_chats > 0 && (
          <div className="mt-3 h-3 rounded-full bg-gray-100 overflow-hidden flex">
            <div
              className="bg-green-400 h-full"
              style={{ width: `${(stats.rating.positive / stats.total_chats) * 100}%` }}
            />
            <div
              className="bg-red-400 h-full"
              style={{ width: `${(stats.rating.negative / stats.total_chats) * 100}%` }}
            />
          </div>
        )}
      </div>
    </div>
  )
}
