const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// POST /api/auth/login
async function login(req, res) {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Vui lòng nhập tên đăng nhập và mật khẩu.' });
  }

  const adminUsername = process.env.ADMIN_USERNAME;
  const adminPasswordHash = process.env.ADMIN_PASSWORD_HASH;

  // Always run bcrypt.compare even on wrong username to avoid timing attacks
  const passwordHash = username === adminUsername
    ? adminPasswordHash
    : '$2b$12$invalidhashpaddingtomakeconstanttimexxxxxxxxxxxxxxxxxxx'; // dummy hash

  let valid = false;
  try {
    valid = await bcrypt.compare(password, passwordHash);
  } catch {
    // ignore — valid stays false
  }

  if (!valid || username !== adminUsername) {
    return res.status(401).json({ error: 'Tên đăng nhập hoặc mật khẩu không đúng.' });
  }

  const token = jwt.sign(
    { username, role: 'admin' },
    process.env.JWT_SECRET,
    { expiresIn: '8h' }
  );

  res.json({ token, expiresIn: 8 * 60 * 60 });
}

// GET /api/auth/verify  (protected by authMiddleware)
function verify(req, res) {
  res.json({ valid: true, admin: req.admin });
}

module.exports = { login, verify };
