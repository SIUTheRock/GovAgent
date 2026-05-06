const pool = require('../db/postgres');

// GET /api/search?q=&category=&page=1
async function search(req, res) {
  try {
    const q = (req.query.q || '').trim().substring(0, 200);
    if (!q) return res.status(400).json({ error: 'Thiếu từ khóa tìm kiếm.' });

    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(20, Math.max(1, parseInt(req.query.limit) || 10));
    const offset = (page - 1) * limit;
    const categoryId = req.query.category ? parseInt(req.query.category) : null;

    const conditions = ["p.is_active = TRUE", "to_tsvector('simple', coalesce(p.name,'') || ' ' || coalesce(p.raw_content,'')) @@ plainto_tsquery('simple', $1)"];
    const params = [q];

    if (categoryId) {
      params.push(categoryId);
      conditions.push(`p.category_id = $${params.length}`);
    }

    const where = `WHERE ${conditions.join(' AND ')}`;

    const countResult = await pool.query(
      `SELECT COUNT(*) FROM procedures p ${where}`, params
    );
    const total = parseInt(countResult.rows[0].count);

    params.push(limit);
    params.push(offset);
    const dataResult = await pool.query(
      `SELECT p.id, p.code, p.name, p.level, p.implementing_agency,
              p.processing_time, c.name AS category_name,
              ts_rank(to_tsvector('simple', coalesce(p.name,'') || ' ' || coalesce(p.raw_content,'')),
                      plainto_tsquery('simple', $1)) AS rank
       FROM procedures p
       LEFT JOIN categories c ON p.category_id = c.id
       ${where}
       ORDER BY rank DESC, p.name ASC
       LIMIT $${params.length - 1} OFFSET $${params.length}`,
      params
    );

    res.json({
      data: dataResult.rows,
      query: q,
      pagination: { total, page, limit, totalPages: Math.ceil(total / limit) },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi tìm kiếm.' });
  }
}

module.exports = { search };
