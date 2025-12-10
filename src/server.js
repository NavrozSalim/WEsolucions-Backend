const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config({ path: '.env' });

const { testConnection } = require('./config/database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', async (req, res) => {
  const dbStatus = await testConnection();
  res.status(dbStatus ? 200 : 503).json({
    status: dbStatus ? 'healthy' : 'unhealthy',
    database: dbStatus ? 'connected' : 'disconnected',
    timestamp: new Date().toISOString()
  });
});

// API routes
app.get('/', (req, res) => {
  res.json({
    message: 'WEsolucions Backend API',
    version: '1.0.0',
    status: 'running'
  });
});

// Start server
const startServer = async () => {
  try {
    // Test database connection on startup
    await testConnection();
    
    app.listen(PORT, () => {
      console.log(`🚀 Server running on port ${PORT}`);
      console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
      console.log(`🌐 Health check: http://localhost:${PORT}/health`);
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
};

startServer();

module.exports = app;

