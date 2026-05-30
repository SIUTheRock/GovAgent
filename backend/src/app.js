require('dotenv').config();
/* ---------------------------------------------------------
 * Copyright (c) 2025 PPNCKH Contributors
 * Licensed under the MIT License.
 * --------------------------------------------------------- */
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');

const proceduresRouter = require('./routes/procedures');
const searchRouter = require('./routes/search');
const chatRouter = require('./routes/chat');
const categoriesRouter = require('./routes/categories');
const adminRouter = require('./routes/admin');
const authRouter = require('./routes/auth');

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 phút
  max: 200,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

const chatLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 phút
  max: 20,
  message: { error: 'Quá nhiều yêu cầu chat, vui lòng thử lại sau 1 phút.' },
});

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 phút
  max: 5,
  message: { error: 'Quá nhiều lần đăng nhập thất bại, vui lòng thử lại sau 15 phút.' },
  skipSuccessfulRequests: true,
});

app.use(morgan('dev'));
app.use(express.json({ limit: '10kb' }));

// Tách route theo đúng ba trục demo chính: dữ liệu thủ tục, chat AI và quản trị.
app.use('/api/auth', loginLimiter, authRouter);
app.use('/api/procedures', proceduresRouter);
app.use('/api/search', searchRouter);
app.use('/api/chat', chatLimiter, chatRouter);
app.use('/api/categories', categoriesRouter);
app.use('/api/admin', adminRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint không tồn tại.' });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Lỗi máy chủ nội bộ.' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Backend API đang chạy tại http://localhost:${PORT}`);
});

module.exports = app;
