const jwt = require('jsonwebtoken');

/**
 * JWT authentication middleware — protects admin routes.
 * Expects: Authorization: Bearer <token>
 */
module.exports = function authMiddleware(req, res, next) {
  const authHeader = req.headers['authorization'];

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Không có quyền truy cập. Vui lòng đăng nhập.' });
  }

  const token = authHeader.slice(7); // Remove "Bearer "

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.admin = payload;
    next();
  } catch {
    return res.status(401).json({ error: 'Token không hợp lệ hoặc đã hết hạn.' });
  }
};
