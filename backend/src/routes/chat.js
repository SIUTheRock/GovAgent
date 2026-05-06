const express = require('express');
const router = express.Router();
const { chat } = require('../controllers/chatController');
const { submitFeedback } = require('../controllers/feedbackController');

router.post('/', chat);
router.post('/feedback', submitFeedback);

module.exports = router;
