const pool = require('../db/postgres');

// POST /api/chat/feedback
// Body: { log_id: number, rating: 1 | -1 }
async function submitFeedback(req, res) {
  try {
    const { log_id, rating } = req.body;

    if (!log_id || typeof log_id !== 'number') {
      return res.status(400).json({ error: 'Thiếu log_id.' });
    }
    if (rating !== 1 && rating !== -1) {
      return res.status(400).json({ error: 'rating phải là 1 (hữu ích) hoặc -1 (không hữu ích).' });
    }

    await pool.query(
      `UPDATE chat_logs SET rating = $1 WHERE id = $2`,
      [rating, log_id]
    );

    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi ghi nhận đánh giá.' });
  }
}

module.exports = { submitFeedback };
