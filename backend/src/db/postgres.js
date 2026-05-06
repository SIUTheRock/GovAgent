const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

pool.on('error', (err) => {
  console.error('Unexpected PostgreSQL client error', err);
  process.exit(-1);
});

// Migration: thêm cột rating vào chat_logs nếu chưa có
pool.query(`
  ALTER TABLE chat_logs
  ADD COLUMN IF NOT EXISTS rating SMALLINT CHECK (rating IN (1, -1))
`).catch((err) => {
  if (!err.message.includes('already exists')) {
    console.error('Migration warning:', err.message);
  }
});

// Migration: thêm cột form_templates vào procedures nếu chưa có
pool.query(`
  ALTER TABLE procedures
  ADD COLUMN IF NOT EXISTS form_templates JSONB DEFAULT '[]'::jsonb
`).catch((err) => {
  if (!err.message.includes('already exists')) {
    console.error('Migration warning:', err.message);
  }
});

module.exports = pool;
