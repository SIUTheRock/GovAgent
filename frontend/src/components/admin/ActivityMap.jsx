import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

// 22 đơn vị hành chính TP.HCM với tọa độ trung tâm
const DISTRICTS = [
  { name: 'Quận 1',      coords: [10.7756, 106.7019], topProcs: ['Đăng ký kết hôn', 'Cấp CCCD', 'Đăng ký khai sinh'] },
  { name: 'Quận 3',      coords: [10.7795, 106.6861], topProcs: ['Xác nhận cư trú', 'Cấp hộ chiếu', 'Đăng ký kết hôn'] },
  { name: 'Quận 4',      coords: [10.7581, 106.7055], topProcs: ['Đăng ký khai sinh', 'Cấp CCCD', 'Xác nhận cư trú'] },
  { name: 'Quận 5',      coords: [10.7548, 106.6641], topProcs: ['Đăng ký kinh doanh', 'Cấp CCCD', 'Đăng ký kết hôn'] },
  { name: 'Quận 6',      coords: [10.7487, 106.6354], topProcs: ['Cấp CCCD', 'Xác nhận cư trú', 'Đăng ký khai sinh'] },
  { name: 'Quận 7',      coords: [10.7352, 106.7191], topProcs: ['Đăng ký kinh doanh', 'Cấp hộ chiếu', 'Cấp CCCD'] },
  { name: 'Quận 8',      coords: [10.7258, 106.6432], topProcs: ['Đăng ký khai sinh', 'Xác nhận cư trú', 'Cấp CCCD'] },
  { name: 'Quận 10',     coords: [10.7737, 106.6682], topProcs: ['Cấp CCCD', 'Đăng ký kết hôn', 'Cấp hộ chiếu'] },
  { name: 'Quận 11',     coords: [10.7666, 106.6541], topProcs: ['Xác nhận cư trú', 'Cấp CCCD', 'Đăng ký khai sinh'] },
  { name: 'Quận 12',     coords: [10.8636, 106.6627], topProcs: ['Đăng ký khai sinh', 'Đăng ký kết hôn', 'Cấp CCCD'] },
  { name: 'Bình Chánh',  coords: [10.6876, 106.5576], topProcs: ['Cấp CCCD', 'Xác nhận cư trú', 'Đăng ký khai sinh'] },
  { name: 'Bình Tân',    coords: [10.7683, 106.6098], topProcs: ['Xác nhận cư trú', 'Cấp CCCD', 'Đăng ký kinh doanh'] },
  { name: 'Bình Thạnh',  coords: [10.8079, 106.7139], topProcs: ['Đăng ký kết hôn', 'Cấp CCCD', 'Cấp hộ chiếu'] },
  { name: 'Cần Giờ',     coords: [10.4040, 106.9618], topProcs: ['Cấp CCCD', 'Đăng ký khai sinh', 'Xác nhận cư trú'] },
  { name: 'Củ Chi',      coords: [11.0008, 106.5062], topProcs: ['Cấp CCCD', 'Đăng ký khai sinh', 'Xác nhận cư trú'] },
  { name: 'Gò Vấp',      coords: [10.8375, 106.6654], topProcs: ['Xác nhận cư trú', 'Cấp CCCD', 'Đăng ký kinh doanh'] },
  { name: 'Hóc Môn',     coords: [10.8947, 106.5984], topProcs: ['Đăng ký khai sinh', 'Cấp CCCD', 'Xác nhận cư trú'] },
  { name: 'Nhà Bè',      coords: [10.6977, 106.7471], topProcs: ['Cấp CCCD', 'Xác nhận cư trú', 'Đăng ký khai sinh'] },
  { name: 'Phú Nhuận',   coords: [10.7973, 106.6797], topProcs: ['Đăng ký kết hôn', 'Cấp CCCD', 'Cấp hộ chiếu'] },
  { name: 'Tân Bình',    coords: [10.8010, 106.6527], topProcs: ['Cấp CCCD', 'Xác nhận cư trú', 'Đăng ký kết hôn'] },
  { name: 'Tân Phú',     coords: [10.7891, 106.6335], topProcs: ['Xác nhận cư trú', 'Cấp CCCD', 'Đăng ký khai sinh'] },
  { name: 'TP. Thủ Đức', coords: [10.8458, 106.7630], topProcs: ['Đăng ký kinh doanh', 'Cấp CCCD', 'Cấp hộ chiếu'] },
]

// Seeded pseudo-random để ban đầu ra số ổn định (không nhảy khi re-render)
function seededRand(seed) {
  let s = seed
  return function () {
    s = (s * 1664525 + 1013904223) & 0xffffffff
    return (s >>> 0) / 0xffffffff
  }
}

function generateCounts(seed) {
  const rand = seededRand(seed)
  return DISTRICTS.map((d) => {
    // Nội thành đông hơn, ngoại thành thưa hơn
    const isUrban = !['Bình Chánh', 'Cần Giờ', 'Củ Chi', 'Hóc Môn', 'Nhà Bè'].includes(d.name)
    const base = isUrban ? 80 : 20
    const spread = isUrban ? 220 : 60
    return Math.floor(base + rand() * spread)
  })
}

function getDotStyle(count) {
  if (count < 50)  return { radius: 8,  color: '#fca5a5', fillColor: '#ef4444', fillOpacity: 0.65, weight: 1 }
  if (count < 150) return { radius: 14, color: '#f87171', fillColor: '#dc2626', fillOpacity: 0.72, weight: 1.5 }
  return               { radius: 22, color: '#dc2626', fillColor: '#991b1b', fillOpacity: 0.80, weight: 2 }
}

export default function ActivityMap() {
  const seedRef = useRef(Date.now())
  const [counts, setCounts] = useState(() => generateCounts(seedRef.current))
  const [lastUpdated, setLastUpdated] = useState(new Date())

  // Giả lập real-time: thay đổi nhỏ mỗi 30 giây
  useEffect(() => {
    const timer = setInterval(() => {
      setCounts((prev) =>
        prev.map((c) => {
          const delta = Math.floor((Math.random() - 0.45) * 15)
          return Math.max(1, c + delta)
        })
      )
      setLastUpdated(new Date())
    }, 30_000)
    return () => clearInterval(timer)
  }, [])

  const total = counts.reduce((s, c) => s + c, 0)

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">🗺️ Bản đồ hoạt động người dùng</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Giả lập phân bố người dùng đang sử dụng hệ thống — cập nhật lúc{' '}
            {lastUpdated.toLocaleTimeString('vi-VN')}
          </p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-blue-700">{total.toLocaleString()}</p>
          <p className="text-xs text-gray-500">Tổng người dùng</p>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-gray-600">
        <span className="font-medium">Mức độ:</span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded-full bg-red-300 border border-red-400"></span> Thấp (&lt;50)
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-4 h-4 rounded-full bg-red-500 border border-red-600"></span> Trung bình (50–149)
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-5 h-5 rounded-full bg-red-800 border border-red-900"></span> Cao (≥150)
        </span>
      </div>

      {/* Map */}
      <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm" style={{ height: 480 }}>
        <MapContainer
          center={[10.7769, 106.7009]}
          zoom={11}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {DISTRICTS.map((district, i) => {
            const count = counts[i]
            const style = getDotStyle(count)
            return (
              <CircleMarker
                key={district.name}
                center={district.coords}
                radius={style.radius}
                pathOptions={{
                  color: style.color,
                  fillColor: style.fillColor,
                  fillOpacity: style.fillOpacity,
                  weight: style.weight,
                }}
              >
                <Popup>
                  <div className="min-w-[160px]">
                    <p className="font-bold text-gray-800 mb-1">📍 {district.name}</p>
                    <p className="text-sm text-blue-700 font-semibold mb-2">
                      {count} người dùng
                    </p>
                    <p className="text-xs text-gray-500 font-medium mb-1">Top thủ tục hỏi:</p>
                    <ol className="text-xs text-gray-700 space-y-0.5 pl-3 list-decimal">
                      {district.topProcs.map((p) => (
                        <li key={p}>{p}</li>
                      ))}
                    </ol>
                  </div>
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>

      {/* District table */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {DISTRICTS.map((d, i) => (
          <div
            key={d.name}
            className="flex items-center justify-between bg-white rounded-lg border border-gray-100 px-3 py-2 text-xs"
          >
            <span className="text-gray-700 font-medium truncate">{d.name}</span>
            <span
              className={`ml-2 font-bold ${
                counts[i] >= 150
                  ? 'text-red-700'
                  : counts[i] >= 50
                  ? 'text-red-500'
                  : 'text-red-300'
              }`}
            >
              {counts[i]}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
