const pool = require('../db/postgres');

// GET /api/categories
async function getCategories(req, res) {
  try {
    const result = await pool.query(
      'SELECT id, name, slug, description, icon FROM categories ORDER BY name ASC'
    );
    res.json({ data: result.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Lỗi khi lấy danh mục.' });
  }
}

module.exports = { getCategories };
