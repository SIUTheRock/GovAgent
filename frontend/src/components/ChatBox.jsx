import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { sendChat, sendFeedback } from '../services/api'

const SESSION_KEY = 'chat_session_id'

function getSessionId() {
  let sid = sessionStorage.getItem(SESSION_KEY)
  if (!sid) {
    sid = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
    sessionStorage.setItem(SESSION_KEY, sid)
  }
  return sid
}

const WELCOME = {
  id: 0,
  role: 'assistant',
  text: 'Xin chào! Tôi là trợ lý ảo hỗ trợ tra cứu thủ tục hành chính tại TP.HCM. Bạn muốn hỏi về thủ tục gì?',
  suggestions: [
    'Đăng ký khai sinh cần giấy tờ gì?',
    'Cách đăng ký thường trú tại TP.HCM?',
    'Thủ tục xin cấp phép xây dựng nhà ở?',
    'Đăng ký kết hôn mất bao lâu?',
  ],
}

export default function ChatBox() {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState({}) // { [msg.id]: 1 | -1 }
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const question = (text || input).trim()
    if (!question || loading) return

    setInput('')
    const newUserMsg = { id: Date.now(), role: 'user', text: question }
    setMessages((prev) => [...prev, newUserMsg])
    setLoading(true)

    try {
      // Build history from previous real messages (exclude welcome + the new user msg)
      const currentMessages = [...messages, newUserMsg]
      const historyPayload = currentMessages
        .filter((m) => m.id !== 0)
        .slice(-8)
        .map((m) => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.text }))

      const { data } = await sendChat(question, getSessionId(), historyPayload)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          text: data.answer,
          procedures: data.suggested_procedures || [],
          responseTime: data.response_time_ms,
          logId: data.log_id || null,
        },
      ])
    } catch (err) {
      const errMsg =
        err.response?.data?.error || 'Đã xảy ra lỗi, vui lòng thử lại.'
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', text: errMsg, isError: true },
      ])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const handleFeedback = async (msgId, logId, rating) => {
    if (!logId || feedback[msgId]) return
    setFeedback((prev) => ({ ...prev, [msgId]: rating }))
    try {
      await sendFeedback(logId, rating)
    } catch {
      // silent fail
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-1' : 'order-2'}`}>
              {msg.role === 'assistant' && (
                <div className="flex items-center gap-1 mb-1">
                  <span className="text-lg">🤖</span>
                  <span className="text-xs text-gray-500">Trợ lý AI</span>
                </div>
              )}
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-none'
                    : msg.isError
                    ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-none'
                    : 'bg-white text-gray-800 border border-gray-200 shadow-sm rounded-tl-none'
                }`}
              >
                {msg.text}
              </div>

              {/* Gợi ý câu hỏi (chỉ ở tin nhắn đầu) */}
              {msg.suggestions && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {msg.suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => sendMessage(s)}
                      className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-3 py-1 hover:bg-blue-100 transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}

              {/* Thủ tục liên quan */}
              {msg.procedures?.length > 0 && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs text-gray-500">📎 Thủ tục liên quan:</p>
                  {msg.procedures.map((p) => (
                    <Link
                      key={p.id}
                      to={`/documents/${p.id}`}
                      className="block text-xs bg-blue-50 text-blue-700 border border-blue-100 rounded-lg px-3 py-2 hover:bg-blue-100 transition-colors"
                    >
                      🔗 {p.name}
                      {p.processing_time && (
                        <span className="text-gray-500 ml-1">· {p.processing_time}</span>
                      )}
                    </Link>
                  ))}
                </div>
              )}

              {msg.responseTime && (
                <p className="text-xs text-gray-400 mt-1 text-right">
                  ⚡ {(msg.responseTime / 1000).toFixed(1)}s
                </p>
              )}

              {/* Feedback buttons (chỉ cho tin nhắn AI có logId) */}
              {msg.role === 'assistant' && !msg.isError && msg.logId && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs text-gray-400">Câu trả lời này có hữu ích không?</span>
                  <button
                    onClick={() => handleFeedback(msg.id, msg.logId, 1)}
                    disabled={!!feedback[msg.id]}
                    className={`text-sm px-2 py-0.5 rounded-full border transition-colors ${
                      feedback[msg.id] === 1
                        ? 'bg-green-100 border-green-400 text-green-700'
                        : 'border-gray-300 text-gray-500 hover:border-green-400 hover:text-green-600'
                    } disabled:cursor-default`}
                    title="Hữu ích"
                  >
                    👍
                  </button>
                  <button
                    onClick={() => handleFeedback(msg.id, msg.logId, -1)}
                    disabled={!!feedback[msg.id]}
                    className={`text-sm px-2 py-0.5 rounded-full border transition-colors ${
                      feedback[msg.id] === -1
                        ? 'bg-red-100 border-red-400 text-red-700'
                        : 'border-gray-300 text-gray-500 hover:border-red-400 hover:text-red-600'
                    } disabled:cursor-default`}
                    title="Không hữu ích"
                  >
                    👎
                  </button>
                  {feedback[msg.id] && (
                    <span className="text-xs text-gray-400">Cảm ơn phản hồi!</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
              <div className="flex gap-1 items-center">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white px-4 py-3">
        <div className="flex gap-2 items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Nhập câu hỏi của bạn... (Enter để gửi)"
            rows={1}
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 max-h-32 overflow-y-auto"
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0"
          >
            Gửi
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1.5 text-center">
          Câu trả lời mang tính tham khảo, vui lòng xác nhận tại cơ quan có thẩm quyền.
        </p>
      </div>
    </div>
  )
}
