/**
 * Test script to verify Supabase PostgreSQL connection
 * Run with: node src/scripts/test-db-connection.js
 */

// Load environment variables (will use .env from container or process.env)
require('dotenv').config();

const { testConnection, pool } = require('../config/database');

async function runTest() {
  console.log('🔍 Testing Supabase PostgreSQL connection...\n');
  
  // Check if using connection string or individual parameters
  if (process.env.DATABASE_URL) {
    console.log('📝 Using connection string (DATABASE_URL)');
    // Mask password in connection string for display
    const maskedUrl = process.env.DATABASE_URL.replace(/:(.+?)@/, ':***@');
    console.log(`  Connection String: ${maskedUrl}\n`);
  } else {
    console.log('📝 Using individual parameters:');
    console.log(`  Host: ${process.env.SUPABASE_DB_HOST}`);
    console.log(`  Port: ${process.env.SUPABASE_DB_PORT}`);
    console.log(`  Database: ${process.env.SUPABASE_DB_NAME}`);
    console.log(`  User: ${process.env.SUPABASE_DB_USER}`);
    console.log(`  Password: ${process.env.SUPABASE_DB_PASSWORD ? '***set***' : '❌ NOT SET'}`);
    console.log(`  SSL: ${process.env.SUPABASE_DB_SSL}\n`);

    // Check if password is set
    if (!process.env.SUPABASE_DB_PASSWORD || process.env.SUPABASE_DB_PASSWORD.trim() === '') {
      console.log('❌ ERROR: SUPABASE_DB_PASSWORD is not set in .env file!');
      console.log('\n💡 Please add your Supabase database password to the .env file:');
      console.log('   SUPABASE_DB_PASSWORD=your_password_here');
      console.log('   OR use DATABASE_URL connection string instead');
      process.exit(1);
    }
  }

  const success = await testConnection();

  if (success) {
    // Try a simple query
    try {
      const result = await pool.query('SELECT version()');
      console.log('\n📊 PostgreSQL Version:', result.rows[0].version);
      
      // Test a simple query
      const tableResult = await pool.query(`
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        LIMIT 5
      `);
      console.log('\n📋 Sample tables:', tableResult.rows.map(r => r.table_name).join(', ') || 'No tables found');
      
      console.log('\n✅ Connection test completed successfully!');
      process.exit(0);
    } catch (error) {
      console.error('\n❌ Query test failed:', error.message);
      process.exit(1);
    }
  } else {
    console.log('\n❌ Connection test failed!');
    console.log('\n💡 Troubleshooting tips:');
    console.log('   1. Check your password in .env file');
    console.log('   2. Verify Supabase database is accessible');
    console.log('   3. Ensure SSL is enabled (SUPABASE_DB_SSL=true)');
    process.exit(1);
  }
}

runTest();

