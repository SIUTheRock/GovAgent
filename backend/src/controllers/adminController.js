const pool = require('../db/postgres');
const axios = require('axios');

// GET /api/admin/stats
async function getStats(req, res) {
  try {
    const [
      totalChats,
      todayChats,
      avgResponseTime,
      ratingStats,
      topProcedures,
      recentLogs,
    ] = await Promise.all([
      // Tổng số chat
      pool.query(`SELECT COUNT(*) AS count FROM chat_logs`),

      // Chat hôm nay
      pool.query(
        `SELECT COUNT(*) AS count FROM chat_logs
         WHERE created_at >= CURRENT_DATE`
      ),

      // Thời gian phản hồi trung bình (ms)
      pool.query(
        `SELECT ROUND(AVG(response_time_ms)) AS avg_ms FROM chat_logs`
      ),

      // Thống kê đánh giá
      pool.query(
        `SELECT
           COUNT(CASE WHEN rating = 1 THEN 1 END) AS positive,
           COUNT(CASE WHEN rating = -1 THEN 1 END) AS negative,
           COUNT(CASE WHEN rating IS NULL THEN 1 END) AS no_rating
         FROM chat_logs`
      ),

      // Thủ tục được hỏi nhiều nhất
      pool.query(
        `SELECT p.id, p.name, COUNT(*) AS mention_count
         FROM chat_logs cl
         JOIN LATERAL unnest(cl.referenced_procedure_ids) AS pid ON TRUE
         JOIN procedures p ON p.id = pid
         WHERE p.is_active = TRUE
         GROUP BY p.id, p.name
         ORDER BY mention_count DESC
         LIMIT 5`
      ),

      // Câu hỏi gần đây
      pool.query(
        `SELECT id, question, rating, response_time_ms, created_at
         FROM chat_logs
         ORDER BY created_at DESC
         LIMIT 10`
      ),
    ]);

    res.json({
      total_chats: parseInt(totalChats.rows[0].count, 10),
      today_chats: parseInt(todayChats.rows[0].count, 10),
      avg_response_time_ms: parseInt(avgResponseTime.rows[0].avg_ms, 10) || 0,
      rating: {
        positive: parseInt(ratingStats.rows[0].positive, 10),
        negative: parseInt(ratingStats.rows[0].negative, 10),
        no_rating: parseInt(ratingStats.rows[0].no_rating, 10),
      },
      top_procedures: topProcedures.rows,
      recent_logs: recentLogs.rows,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi lấy thống kê.' });
  }
}

// GET /api/admin/chat-history?page=1&q=keyword
async function getChatHistory(req, res) {
  try {
    const page = Math.max(1, parseInt(req.query.page, 10) || 1);
    const limit = 20;
    const offset = (page - 1) * limit;
    const q = (req.query.q || '').trim();

    let countQuery, dataQuery;

    if (q) {
      const searchParam = `%${q}%`;
      countQuery = pool.query(
        `SELECT COUNT(*) AS count FROM chat_logs WHERE question ILIKE $1`,
        [searchParam]
      );
      dataQuery = pool.query(
        `SELECT id, session_id, question, answer, rating, response_time_ms, created_at
         FROM chat_logs
         WHERE question ILIKE $1
         ORDER BY created_at DESC
         LIMIT $2 OFFSET $3`,
        [searchParam, limit, offset]
      );
    } else {
      countQuery = pool.query(`SELECT COUNT(*) AS count FROM chat_logs`);
      dataQuery = pool.query(
        `SELECT id, session_id, question, answer, rating, response_time_ms, created_at
         FROM chat_logs
         ORDER BY created_at DESC
         LIMIT $1 OFFSET $2`,
        [limit, offset]
      );
    }

    const [countResult, dataResult] = await Promise.all([countQuery, dataQuery]);
    const total = parseInt(countResult.rows[0].count, 10);

    res.json({
      data: dataResult.rows,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit),
      },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi lấy lịch sử chat.' });
  }
}

// GET /api/admin/system-health
async function getSystemHealth(req, res) {
  const results = {};

  // Check DB
  const dbStart = Date.now();
  try {
    await pool.query('SELECT 1');
    results.database = { status: 'ok', latency_ms: Date.now() - dbStart };
  } catch {
    results.database = { status: 'error', latency_ms: null };
  }

  // Check AI service
  const aiStart = Date.now();
  try {
    const aiUrl = process.env.AI_SERVICE_URL || 'http://localhost:8001';
    await axios.get(`${aiUrl}/health`, { timeout: 3000 });
    results.ai_service = { status: 'ok', latency_ms: Date.now() - aiStart };
  } catch {
    results.ai_service = { status: 'error', latency_ms: null };
  }

  results.backend = {
    status: 'ok',
    uptime_seconds: Math.floor(process.uptime()),
    node_version: process.version,
  };

  res.json(results);
}

module.exports = { getStats, getChatHistory, getSystemHealth };
