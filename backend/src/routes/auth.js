const express = require('express');
const router = express.Router();
const { login, verify } = require('../controllers/authController');
const authMiddleware = require('../middleware/auth');

// POST /api/auth/login
router.post('/login', login);

// GET /api/auth/verify — requires valid token
router.get('/verify', authMiddleware, verify);

module.exports = router;
