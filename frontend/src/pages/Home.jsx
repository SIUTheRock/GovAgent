import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getCategories, searchProcedures } from '../services/api'

const CATEGORY_ICONS = {
  'ho-tich': '📋',
  'cu-tru': '🏠',
  'dat-dai-nha-o': '🏡',
  'doanh-nghiep': '💼',
  'giao-duc': '🎓',
  'y-te': '🏥',
  'giao-thong-van-tai': '🚗',
  'xay-dung': '🏗️',
  'lao-dong-viec-lam': '👷',
  'tu-phap': '⚖️',
}

export default function Home() {
  const [categories, setCategories] = useState([])
  const [q, setQ] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    getCategories()
      .then(({ data }) => setCategories(data.data || []))
      .catch(() => {})
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    const query = q.trim()
    if (!query) return
    if (query.length < 2) return

    setSearching(true)
    try {
      const { data } = await searchProcedures({ q: query, limit: 5 })
      setSearchResults(data.data || [])
    } catch {
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }

  const goToSearch = () => {
    if (q.trim()) navigate(`/documents?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-700 to-blue-500 text-white py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="text-5xl mb-4">🏛️</div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3">
            Tra cứu Thủ tục Hành chính
          </h1>
          <p className="text-blue-100 text-lg mb-8">
            Hỗ trợ người dân TP. Hồ Chí Minh tìm kiếm thủ tục hành chính nhanh chóng, chính xác
          </p>

          {/* Search bar */}
          <form onSubmit={handleSearch} className="flex gap-2 max-w-xl mx-auto">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Ví dụ: đăng ký khai sinh, xin cấp phép xây dựng..."
              className="flex-1 px-4 py-3 rounded-xl text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              className="bg-white text-blue-700 px-5 py-3 rounded-xl font-semibold text-sm hover:bg-blue-50 transition-colors shrink-0"
            >
              {searching ? '...' : 'Tìm kiếm'}
            </button>
          </form>

          {/* Quick search results */}
          {searchResults.length > 0 && (
            <div className="mt-3 bg-white rounded-xl text-left max-w-xl mx-auto overflow-hidden shadow-lg">
              {searchResults.map((p) => (
                <Link
                  key={p.id}
                  to={`/documents/${p.id}`}
                  className="block px-4 py-3 text-gray-800 text-sm hover:bg-blue-50 border-b last:border-0 transition-colors"
                >
                  <span className="font-medium">{p.name}</span>
                  {p.category_name && (
                    <span className="text-xs text-gray-500 ml-2">· {p.category_name}</span>
                  )}
                </Link>
              ))}
              <button
                onClick={goToSearch}
                className="block w-full text-center text-blue-600 text-xs py-2 hover:bg-blue-50 transition-colors"
              >
                Xem tất cả kết quả →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="max-w-4xl mx-auto px-4 -mt-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <Link
            to="/chat"
            className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition-shadow border border-gray-100 group"
          >
            <div className="text-3xl mb-2">🤖</div>
            <h3 className="font-semibold text-gray-800 group-hover:text-blue-600">Hỏi Trợ lý AI</h3>
            <p className="text-xs text-gray-500 mt-1">Đặt câu hỏi trực tiếp</p>
          </Link>
          <Link
            to="/documents"
            className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition-shadow border border-gray-100 group"
          >
            <div className="text-3xl mb-2">📄</div>
            <h3 className="font-semibold text-gray-800 group-hover:text-blue-600">Danh sách Thủ tục</h3>
            <p className="text-xs text-gray-500 mt-1">Tra cứu theo lĩnh vực</p>
          </Link>
          <Link
            to="/documents?q=hồ sơ"
            className="bg-white rounded-xl shadow-md p-5 text-center hover:shadow-lg transition-shadow border border-gray-100 group col-span-2 md:col-span-1"
          >
            <div className="text-3xl mb-2">🔍</div>
            <h3 className="font-semibold text-gray-800 group-hover:text-blue-600">Tra cứu Hồ sơ</h3>
            <p className="text-xs text-gray-500 mt-1">Giấy tờ cần chuẩn bị</p>
          </Link>
        </div>
      </div>

      {/* Categories */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h2 className="text-xl font-bold text-gray-800 mb-6">Tra cứu theo lĩnh vực</h2>
        {categories.length === 0 ? (
          <div className="text-gray-400 text-sm text-center py-8">Đang tải danh mục...</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {categories.map((cat) => (
              <Link
                key={cat.id}
                to={`/documents?category=${cat.id}`}
                className="bg-white rounded-xl border border-gray-200 p-4 text-center hover:border-blue-400 hover:shadow-md transition-all group"
              >
                <div className="text-2xl mb-2">{CATEGORY_ICONS[cat.slug] || cat.icon || '📁'}</div>
                <p className="text-xs font-medium text-gray-700 group-hover:text-blue-600 leading-tight">
                  {cat.name}
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Info banner */}
      <div className="bg-blue-50 border-t border-blue-100 py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-sm text-blue-700 font-medium mb-1">
            ℹ️ Thông tin mang tính tham khảo
          </p>
          <p className="text-xs text-gray-500">
            Dữ liệu được tổng hợp từ Cổng Dịch vụ Công Quốc gia (dichvucong.gov.vn).
            Vui lòng xác nhận thông tin tại cơ quan hành chính có thẩm quyền.
          </p>
        </div>
      </div>
    </div>
  )
}
