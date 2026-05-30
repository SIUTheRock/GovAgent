const express = require('express');
const router = express.Router();
const { getStats, getChatHistory, getSystemHealth } = require('../controllers/adminController');
const authMiddleware = require('../middleware/auth');

// All admin routes require a valid JWT
router.use(authMiddleware);

router.get('/stats', getStats);
router.get('/chat-history', getChatHistory);
router.get('/system-health', getSystemHealth);

module.exports = router;
