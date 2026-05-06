import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getProcedureById } from '../services/api'

function Section({ title, content, icon }) {
  if (!content) return null
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
        <span>{icon}</span> {title}
      </h2>
      <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{content}</p>
    </div>
  )
}

export default function ProcedureDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [procedure, setProcedure] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getProcedureById(id)
      .then(({ data }) => setProcedure(data.data))
      .catch((err) => {
        if (err.response?.status === 404) setError('Không tìm thấy thủ tục.')
        else setError('Đã xảy ra lỗi khi tải dữ liệu.')
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin text-4xl mb-4">⏳</div>
        <p className="text-gray-500">Đang tải thông tin...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <div className="text-4xl mb-4">❌</div>
        <p className="text-red-600 font-medium">{error}</p>
        <button onClick={() => navigate(-1)} className="mt-4 text-blue-600 hover:underline text-sm">
          ← Quay lại
        </button>
      </div>
    )
  }

  const levelColor = {
    'Cấp tỉnh': 'bg-purple-100 text-purple-700',
    'Cấp huyện': 'bg-blue-100 text-blue-700',
    'Cấp xã': 'bg-green-100 text-green-700',
  }[procedure.level] || 'bg-gray-100 text-gray-600'

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-xs text-gray-500 mb-4 flex items-center gap-1">
        <Link to="/" className="hover:text-blue-600">Trang chủ</Link>
        <span>/</span>
        <Link to="/documents" className="hover:text-blue-600">Thủ tục</Link>
        {procedure.category_name && (
          <>
            <span>/</span>
            <Link to={`/documents?category=${procedure.category_id}`} className="hover:text-blue-600">
              {procedure.category_name}
            </Link>
          </>
        )}
      </nav>

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-700 to-blue-500 rounded-2xl text-white p-6 mb-6">
        <div className="flex items-start justify-between gap-3 mb-3">
          <h1 className="text-xl font-bold leading-tight">{procedure.name}</h1>
          {procedure.level && (
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium whitespace-nowrap ${levelColor}`}>
              {procedure.level}
            </span>
          )}
        </div>

        {procedure.code && (
          <p className="text-blue-200 text-xs mb-3">Mã thủ tục: {procedure.code}</p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {procedure.implementing_agency && (
            <div className="bg-white/15 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">🏢 Cơ quan</p>
              <p className="text-sm font-medium">{procedure.implementing_agency}</p>
            </div>
          )}
          {procedure.processing_time && (
            <div className="bg-white/15 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">⏱ Thời gian</p>
              <p className="text-sm font-medium">{procedure.processing_time}</p>
            </div>
          )}
          {procedure.fee && (
            <div className="bg-white/15 rounded-lg p-3">
              <p className="text-blue-200 text-xs mb-1">💰 Lệ phí</p>
              <p className="text-sm font-medium">{procedure.fee}</p>
            </div>
          )}
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-4">
        <Section title="Điều kiện thực hiện" content={procedure.requirements} icon="✅" />
        <Section title="Trình tự thực hiện" content={procedure.procedure_steps} icon="📋" />
        <Section title="Thành phần hồ sơ" content={procedure.required_documents} icon="📁" />

        {/* Mẫu đơn tải về */}
        {procedure.form_templates && procedure.form_templates.length > 0 && (
          <div className="bg-white rounded-xl border border-blue-200 p-5">
            <h2 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <span>📥</span> Mẫu đơn / Tờ khai
            </h2>
            <div className="space-y-2">
              {procedure.form_templates.map((form, idx) => {
                const isDvcPortal = form.code === 'dichvucong.gov.vn';
                return (
                  <a
                    key={idx}
                    href={form.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between gap-3 p-3 rounded-lg border border-blue-100 bg-blue-50 hover:bg-blue-100 transition-colors group"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-xl shrink-0">{isDvcPortal ? '🌐' : '📄'}</span>
                      <p className="text-sm font-medium text-gray-800 truncate">{form.name}</p>
                    </div>
                    <span className="text-xs text-blue-600 font-medium whitespace-nowrap shrink-0 group-hover:underline">
                      {isDvcPortal ? 'Mở trang ↗' : 'Tải xuống ↓'}
                    </span>
                  </a>
                );
              })}
            </div>
            <p className="text-xs text-gray-400 mt-3">
              {procedure.form_templates[0]?.code === 'dichvucong.gov.vn'
                ? '* Mở trang Cổng Dịch vụ công Quốc gia để xem và tải mẫu đơn.'
                : '* Bấm để tải trực tiếp file mẫu đơn (.doc/.docx).'}
            </p>
          </div>
        )}

        <Section title="Kết quả thực hiện" content={procedure.result} icon="🎯" />
        <Section title="Căn cứ pháp lý" content={procedure.legal_basis} icon="⚖️" />
      </div>

      {/* Actions */}
      <div className="mt-6 flex flex-wrap gap-3 print:hidden">
        <Link
          to="/chat"
          state={{ question: `Tôi muốn hỏi về thủ tục: ${procedure.name}` }}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          🤖 Hỏi thêm trợ lý AI
        </Link>
        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          🖨️ In / Xuất PDF
        </button>
        {procedure.source_url && (
          <a
            href={procedure.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-green-700 transition-colors"
          >
            🏛️ Xem trên Cổng Dịch vụ công Quốc gia
          </a>
        )}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors"
        >
          ← Quay lại
        </button>
      </div>

      {/* Disclaimer */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-xs text-yellow-800">
        ⚠️ Thông tin trên mang tính tham khảo. Vui lòng xác nhận thông tin tại cơ quan hành chính có thẩm quyền trước khi thực hiện.
      </div>
    </div>
  )
}
