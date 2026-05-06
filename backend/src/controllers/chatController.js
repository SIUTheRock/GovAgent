const axios = require('axios');
const pool = require('../db/postgres');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// POST /api/chat
// Body: { question: string, session_id?: string, history?: array }
async function chat(req, res) {
  try {
    const { question, session_id, history = [] } = req.body;

    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: 'Thiếu câu hỏi.' });
    }

    const trimmedQ = question.trim().substring(0, 500);
    if (trimmedQ.length < 3) {
      return res.status(400).json({ error: 'Câu hỏi quá ngắn.' });
    }

    const startTime = Date.now();

    // Gọi AI service (kèm history)
    const aiResponse = await axios.post(
      `${AI_SERVICE_URL}/chat`,
      { question: trimmedQ, history: Array.isArray(history) ? history.slice(-8) : [] },
      { timeout: 30000 }
    );

    const { answer, procedure_ids = [], sources = [] } = aiResponse.data;
    const responseTimeMs = Date.now() - startTime;

    // Lấy thông tin thủ tục được đề xuất
    let suggestedProcedures = [];
    if (procedure_ids.length > 0) {
      const ids = procedure_ids.slice(0, 5).map(Number).filter(Boolean);
      if (ids.length > 0) {
        const result = await pool.query(
          `SELECT id, name, level, implementing_agency, processing_time
           FROM procedures
           WHERE id = ANY($1::int[]) AND is_active = TRUE`,
          [ids]
        );
        suggestedProcedures = result.rows;
      }
    }

    // Ghi log và lấy log_id để dùng cho feedback
    let logId = null;
    try {
      const logResult = await pool.query(
        `INSERT INTO chat_logs (session_id, question, answer, referenced_procedure_ids, response_time_ms)
         VALUES ($1, $2, $3, $4, $5) RETURNING id`,
        [session_id || null, trimmedQ, answer, procedure_ids, responseTimeMs]
      );
      logId = logResult.rows[0]?.id || null;
    } catch (logErr) {
      console.error('Log error:', logErr);
    }

    res.json({
      answer,
      suggested_procedures: suggestedProcedures,
      sources,
      response_time_ms: responseTimeMs,
      log_id: logId,
    });
  } catch (err) {
    if (err.code === 'ECONNREFUSED' || err.code === 'ECONNABORTED') {
      return res.status(503).json({ error: 'Dịch vụ AI tạm thời không khả dụng, vui lòng thử lại sau.' });
    }
    console.error(err);
    res.status(500).json({ error: 'Lỗi xử lý câu hỏi.' });
  }
}

module.exports = { chat };
