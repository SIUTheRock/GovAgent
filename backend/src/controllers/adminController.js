const pool = require('../db/postgres');

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

module.exports = { getStats };
