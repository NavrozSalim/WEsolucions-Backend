const { Pool } = require('pg');
require('dotenv').config();

// Create connection config
const getConnectionConfig = () => {
  // For pooler, ALWAYS use individual parameters and IGNORE DATABASE_URL completely
  if (process.env.SUPABASE_DB_HOST && process.env.SUPABASE_DB_HOST.includes('pooler')) {
    const config = {
      host: process.env.SUPABASE_DB_HOST,
      port: parseInt(process.env.SUPABASE_DB_PORT) || 6543,
      database: process.env.SUPABASE_DB_NAME || 'postgres',
      user: process.env.SUPABASE_DB_USER || 'postgres.hihygeuawvzzrundvzev',
      password: process.env.SUPABASE_DB_PASSWORD,
      ssl: { rejectUnauthorized: false },
      max: parseInt(process.env.SUPABASE_DB_POOL_MAX) || 10,
      min: parseInt(process.env.SUPABASE_DB_POOL_MIN) || 2,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 15000,
    };
    console.log('🔍 Using pooler connection with individual parameters');
    console.log('   Host:', config.host);
    console.log('   Port:', config.port);
    console.log('   User:', config.user);
    console.log('   Database:', config.database);
    console.log('   Password set:', !!config.password);
    // Explicitly do NOT use connectionString
    return config;
  }

  // Use connection string if available (for direct connections only)
  if (process.env.DATABASE_URL && !process.env.SUPABASE_DB_HOST?.includes('pooler')) {
    console.log('🔍 Using connection string (DATABASE_URL)');
    return {
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false },
      max: parseInt(process.env.SUPABASE_DB_POOL_MAX) || 10,
      min: parseInt(process.env.SUPABASE_DB_POOL_MIN) || 2,
    };
  }

  // Fallback to individual config
  console.log('🔍 Using individual parameters (fallback)');
  return {
    host: process.env.SUPABASE_DB_HOST,
    port: parseInt(process.env.SUPABASE_DB_PORT) || 5432,
    database: process.env.SUPABASE_DB_NAME || 'postgres',
    user: process.env.SUPABASE_DB_USER,
    password: process.env.SUPABASE_DB_PASSWORD,
    ssl: process.env.SUPABASE_DB_SSL === 'true' ? {
      rejectUnauthorized: false
    } : false,
    max: parseInt(process.env.SUPABASE_DB_POOL_MAX) || 10,
    min: parseInt(process.env.SUPABASE_DB_POOL_MIN) || 2,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 15000,
  };
};

// Create PostgreSQL connection pool for Supabase
const pool = new Pool(getConnectionConfig());

pool.on('connect', () => {
  console.log('✅ Connected to Supabase PostgreSQL database');
});

pool.on('error', (err) => {
  console.error('❌ Unexpected error on idle client', err);
  process.exit(-1);
});

// Test connection function
const testConnection = async () => {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT NOW()');
    console.log('✅ Database connection test successful:', result.rows[0].now);
    client.release();
    return true;
  } catch (error) {
    console.error('❌ Database connection test failed:', error.message);
    console.error('   Error code:', error.code);
    if (error.detail) {
      console.error('   Error detail:', error.detail);
    }
    return false;
  }
};

module.exports = {
  pool,
  testConnection
};
