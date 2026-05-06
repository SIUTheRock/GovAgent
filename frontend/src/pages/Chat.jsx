import ChatBox from '../components/ChatBox'

export default function Chat() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-6 h-[calc(100vh-4rem)]">
      <div className="bg-white rounded-2xl shadow-md border border-gray-200 h-full flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-700 to-blue-500 text-white px-5 py-4 flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-xl">
            🤖
          </div>
          <div>
            <h1 className="font-semibold text-base">Trợ lý Hành chính AI</h1>
            <p className="text-blue-100 text-xs">Hỗ trợ tra cứu thủ tục hành chính TP.HCM</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-blue-100">Trực tuyến</span>
          </div>
        </div>

        {/* ChatBox */}
        <div className="flex-1 overflow-hidden">
          <ChatBox />
        </div>
      </div>
    </div>
  )
}
