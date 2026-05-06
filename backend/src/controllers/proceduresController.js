const pool = require('../db/postgres');

// GET /api/procedures?page=1&limit=12&category=&level=
async function getProcedures(req, res) {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(50, Math.max(1, parseInt(req.query.limit) || 12));
    const offset = (page - 1) * limit;
    const categoryId = req.query.category ? parseInt(req.query.category) : null;
    const level = req.query.level || null;

    const conditions = ['p.is_active = TRUE'];
    const params = [];

    if (categoryId) {
      params.push(categoryId);
      conditions.push(`p.category_id = $${params.length}`);
    }
    if (level) {
      params.push(level);
      conditions.push(`p.level = $${params.length}`);
    }

    const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';

    const countResult = await pool.query(
      `SELECT COUNT(*) FROM procedures p ${where}`,
      params
    );
    const total = parseInt(countResult.rows[0].count);

    params.push(limit);
    params.push(offset);
    const dataResult = await pool.query(
      `SELECT p.id, p.code, p.name, p.level, p.implementing_agency,
              p.processing_time, p.fee, c.name AS category_name, c.slug AS category_slug
       FROM procedures p
       LEFT JOIN categories c ON p.category_id = c.id
       ${where}
       ORDER BY p.name ASC
       LIMIT $${params.length - 1} OFFSET $${params.length}`,
      params
    );

    res.json({
      data: dataResult.rows,
      pagination: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi lấy danh sách thủ tục.' });
  }
}

// GET /api/procedures/:id
async function getProcedureById(req, res) {
  try {
    const id = parseInt(req.params.id);
    if (!id || id < 1) return res.status(400).json({ error: 'ID không hợp lệ.' });

    const result = await pool.query(
      `SELECT p.*, c.name AS category_name, c.slug AS category_slug
       FROM procedures p
       LEFT JOIN categories c ON p.category_id = c.id
       WHERE p.id = $1 AND p.is_active = TRUE`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Không tìm thấy thủ tục.' });
    }

    // Tăng view count
    pool.query('UPDATE procedures SET view_count = view_count + 1 WHERE id = $1', [id]);

    res.json({ data: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi lấy chi tiết thủ tục.' });
  }
}

module.exports = { getProcedures, getProcedureById };
