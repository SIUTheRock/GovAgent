import { useState, useEffect } from 'react'
import { getSystemHealth } from '../../services/api'

function StatusCard({ icon, label, status, latency, detail }) {
  const ok = status === 'ok'
  return (
    <div className={`rounded-xl border p-5 ${ok ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-2xl">{icon}</span>
        <span
          className={`text-xs font-bold px-2.5 py-1 rounded-full ${
            ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}
        >
          {ok ? '✅ Hoạt động' : '❌ Lỗi'}
        </span>
      </div>
      <p className="font-semibold text-gray-800">{label}</p>
      {latency != null && (
        <p className="text-sm text-gray-500 mt-1">
          Độ trễ: <span className={`font-medium ${latency < 50 ? 'text-green-600' : latency < 200 ? 'text-yellow-600' : 'text-red-600'}`}>
            {latency}ms
          </span>
        </p>
      )}
      {detail && <p className="text-xs text-gray-400 mt-1">{detail}</p>}
    </div>
  )
}

function formatUptime(seconds) {
  if (seconds < 60) return `${seconds}s`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  return `${h}h ${m}m`
}

export default function SystemHealth() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastCheck, setLastCheck] = useState(null)

  const fetchHealth = async () => {
    setLoading(true)
    try {
      const { data } = await getSystemHealth()
      setHealth(data)
      setLastCheck(new Date())
    } catch {
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
    const timer = setInterval(fetchHealth, 30_000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">🔧 Trạng thái hệ thống</h2>
        <div className="flex items-center gap-3">
          {lastCheck && (
            <span className="text-xs text-gray-400">
              Kiểm tra lúc {lastCheck.toLocaleTimeString('vi-VN')}
            </span>
          )}
          <button
            onClick={fetchHealth}
            disabled={loading}
            className="text-sm text-blue-600 hover:underline disabled:opacity-50"
          >
            {loading ? '⏳' : '🔄'} Làm mới
          </button>
        </div>
      </div>

      {loading && !health ? (
        <div className="text-center py-8 text-gray-400">
          <div className="animate-spin text-3xl mb-2">⏳</div>
          <p className="text-sm">Đang kiểm tra...</p>
        </div>
      ) : !health ? (
        <div className="text-center py-8 text-red-400">
          <p>Không thể lấy trạng thái hệ thống.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatusCard
            icon="🗄️"
            label="Cơ sở dữ liệu"
            status={health.database?.status}
            latency={health.database?.latency_ms}
            detail="PostgreSQL"
          />
          <StatusCard
            icon="🤖"
            label="Dịch vụ AI (RAG)"
            status={health.ai_service?.status}
            latency={health.ai_service?.latency_ms}
            detail="FastAPI + ChromaDB"
          />
          <StatusCard
            icon="⚙️"
            label="Backend API"
            status={health.backend?.status}
            detail={
              health.backend
                ? `Uptime: ${formatUptime(health.backend.uptime_seconds)} · Node ${health.backend.node_version}`
                : undefined
            }
          />
        </div>
      )}

      {health && (
        <div className="bg-gray-50 rounded-xl border border-gray-200 p-4 text-xs text-gray-500 space-y-1">
          <p className="font-medium text-gray-700 mb-2">📋 Thông tin chi tiết</p>
          <p>• Kiểm tra tự động mỗi 30 giây</p>
          <p>• Backend timeout AI check: 3 giây</p>
          {health.backend && (
            <p>• Node.js: {health.backend.node_version} · Uptime: {formatUptime(health.backend.uptime_seconds)}</p>
          )}
        </div>
      )}
    </div>
  )
}
