import { Link } from 'react-router-dom'

export default function ProcedureCard({ procedure }) {
  const levelColor = {
    'Cấp tỉnh': 'bg-purple-100 text-purple-700',
    'Cấp huyện': 'bg-blue-100 text-blue-700',
    'Cấp xã': 'bg-green-100 text-green-700',
  }[procedure.level] || 'bg-gray-100 text-gray-600'

  return (
    <Link
      to={`/documents/${procedure.id}`}
      className="block bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md hover:border-blue-300 transition-all group"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h3 className="font-semibold text-gray-800 text-sm group-hover:text-blue-600 transition-colors line-clamp-2 flex-1">
          {procedure.name}
        </h3>
        {procedure.level && (
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap ${levelColor}`}>
            {procedure.level}
          </span>
        )}
      </div>

      {procedure.category_name && (
        <p className="text-xs text-blue-600 mb-2">📂 {procedure.category_name}</p>
      )}

      {procedure.implementing_agency && (
        <p className="text-xs text-gray-500 truncate">🏢 {procedure.implementing_agency}</p>
      )}

      {procedure.processing_time && (
        <p className="text-xs text-gray-500 mt-1">⏱ {procedure.processing_time}</p>
      )}
    </Link>
  )
}
