# WEsolucions Backend API

Production-ready Node.js Express backend API connected to Supabase PostgreSQL, deployed on Contabo VPS.

## 🎉 Status: LIVE & CONNECTED

- ✅ **VPS:** Contabo (173.212.218.31) - Running
- ✅ **Database:** Supabase PostgreSQL - Connected via Connection Pooler
- ✅ **API:** Express Server - Deployed & Healthy
- ✅ **Docker:** Container Running

## 🌐 Live URLs

- **API Base:** http://173.212.218.31:3000
- **Health Check:** http://173.212.218.31:3000/health

## 📁 Project Structure

```
WEsolucions Backend/
├── src/
│   ├── config/
│   │   └── database.js          # Supabase PostgreSQL connection pool
│   ├── scripts/                 # Utility scripts
│   │   └── test-db-connection.js
│   └── server.js                # Express server entry point
├── .dockerignore                 # Docker build exclusions
├── .env                          # Environment variables (git-ignored)
├── .gitignore                    # Git exclusions
├── deploy.sh                     # VPS deployment script
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker container definition
├── package.json                  # Node.js dependencies
└── README.md                     # This file
```

## 🛠️ Technology Stack

- **Runtime:** Node.js 18 (Alpine Linux)
- **Framework:** Express.js 4.18
- **Database:** Supabase PostgreSQL (Connection Pooler)
- **Database Client:** node-postgres (pg)
- **Security:** Helmet, CORS
- **Logging:** Morgan
- **Containerization:** Docker & Docker Compose
- **VPS:** Contabo (Ubuntu 24.04 LTS)

## 🚀 API Endpoints

### GET `/`
Returns API information
```json
{
  "message": "WEsolucions Backend API",
  "version": "1.0.0",
  "status": "running"
}
```

### GET `/health`
Health check with database connection status
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-10T19:06:53.888Z"
}
```


## 💻 Local Development

### Prerequisites
- Node.js 18+
- npm or yarn
- Supabase account

### Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Configure Supabase credentials in `.env`:**
   ```env
   PORT=3000
   NODE_ENV=development
   DATABASE_URL=postgresql://postgres.PROJECT_ID:PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres
   SUPABASE_DB_HOST=aws-REGION.pooler.supabase.com
   SUPABASE_DB_PORT=6543
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres.PROJECT_ID
   SUPABASE_DB_PASSWORD=your_password
   SUPABASE_DB_SSL=true
   SUPABASE_DB_POOL_MIN=2
   SUPABASE_DB_POOL_MAX=10
   ```

4. **Run database migrations:**
   ```bash
   npm run migrate
   ```

5. **Test database connection:**
   ```bash
   npm run test:db
   ```

6. **Start development server:**
   ```bash
   npm run dev
   ```

## 🐳 Docker Deployment

### Build and Run Locally

```bash
# Build image
docker build -t wesolucions-backend .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🖥️ VPS Deployment (Contabo)

### Current Deployment
- **VPS IP:** 173.212.218.31
- **OS:** Ubuntu 24.04 LTS
- **Status:** ✅ Running
- **Location:** `/opt/wesolucions-backend`

### Deployment Commands

```bash
# SSH into VPS
ssh root@173.212.218.31

# Navigate to project
cd /opt/wesolucions-backend

# Deploy/Update
./deploy.sh

# Or manually
docker-compose up -d --build

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down
```

### Update Application

```bash
# On VPS
cd /opt/wesolucions-backend

# Pull latest changes (if using Git)
git pull

# Or transfer new files via SCP from Windows
# scp -r src root@173.212.218.31:/opt/wesolucions-backend/

# Redeploy
./deploy.sh
```

## 🔒 Database Connection

### Supabase Connection Pooler
- **Host:** `aws-1-ap-southeast-1.pooler.supabase.com`
- **Port:** `6543` (Transaction pooler)
- **Username Format:** `postgres.PROJECT_ID` (e.g., `postgres.hihygeuawvzzrundvzev`)
- **SSL:** Required (Enabled)
- **Connection Pool:** 2-10 connections

### Why Connection Pooler?
- ✅ IPv4 compatible (works on all networks)
- ✅ Better for serverless/stateless applications
- ✅ Handles connection management automatically
- ✅ More reliable than direct connection

### Getting Connection Details

1. Go to Supabase Dashboard → Project Settings → Database
2. Click "Connect" button
3. Select "Transaction pooler" method
4. Copy the connection string
5. Update `.env` file with the credentials

## 📝 Environment Variables

Required environment variables:

```env
# Server
PORT=3000
NODE_ENV=production

# Supabase Connection Pooler
DATABASE_URL=postgresql://postgres.PROJECT_ID:PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres
SUPABASE_DB_HOST=aws-REGION.pooler.supabase.com
SUPABASE_DB_PORT=6543
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.PROJECT_ID
SUPABASE_DB_PASSWORD=your_password
SUPABASE_DB_SSL=true

# Connection Pool Settings
SUPABASE_DB_POOL_MIN=2
SUPABASE_DB_POOL_MAX=10
```

**Note:** In `DATABASE_URL`, URL-encode special characters in password:
- `@` becomes `%40`
- Example: `NSP0122@150NAVO` → `NSP0122%40150NAVO`


## 🔍 Monitoring & Maintenance

### Check Application Status
```bash
# Container status
docker-compose ps

# View logs
docker-compose logs -f backend

# Check health endpoint
curl http://localhost:3000/health
```

### View Resource Usage
```bash
# Docker stats
docker stats wesolucions-backend

# System resources
htop
```

## 🛡️ Security

### Implemented
- ✅ Firewall (UFW) - Ports 22, 3000
- ✅ SSL/TLS for database connections
- ✅ Helmet security headers
- ✅ CORS configuration
- ✅ Non-root Docker user
- ✅ Environment variables for secrets
- ✅ Health checks and monitoring

### Recommended Next Steps
- Set up Nginx reverse proxy with SSL
- Implement rate limiting
- Add authentication/authorization
- Set up automated backups
- Configure log rotation

## 🐛 Troubleshooting

### Container Won't Start
```bash
docker-compose logs backend
docker-compose down
docker-compose up -d --build
```

### Database Connection Issues
```bash
# Test connection
docker-compose exec backend npm run test:db

# Check environment variables
docker-compose exec backend env | grep SUPABASE
```

### Port Already in Use
```bash
# Check what's using port 3000
netstat -tulpn | grep 3000

# Change PORT in .env if needed
```

## 📦 NPM Scripts

```json
{
  "start": "node src/server.js",                              // Production
  "dev": "nodemon src/server.js",                             // Development
  "test:db": "node src/scripts/test-db-connection.js"        // Test DB connection
}
```

## 📊 Connection Details

### Current Configuration
- **VPS:** Contabo (173.212.218.31)
- **Database:** Supabase PostgreSQL
- **Connection Method:** Transaction Pooler (IPv4)
- **Network Mode:** Host (for IPv6 compatibility)
- **Status:** ✅ Connected & Healthy

### Connection Flow
```
Client Request
    ↓
Contabo VPS (173.212.218.31:3000)
    ↓
Docker Container (wesolucions-backend)
    ↓
Express.js Application
    ↓
Connection Pool (2-10 connections)
    ↓
SSL/TLS Connection
    ↓
Supabase Connection Pooler (aws-1-ap-southeast-1.pooler.supabase.com:6543)
    ↓
Supabase PostgreSQL Database
    ↓
Response
```

## 🎯 What Was Built

### Backend API
- ✅ Express.js server with security middleware
- ✅ Health check endpoints
- ✅ Database connection pooling
- ✅ Error handling

### Database Integration
- ✅ Supabase PostgreSQL connection
- ✅ Connection pooler (IPv4 compatible)
- ✅ SSL/TLS encryption
- ✅ Automatic reconnection

### Deployment
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Automated deployment script
- ✅ Health checks

### Infrastructure
- ✅ Contabo VPS setup
- ✅ Firewall configuration
- ✅ Network configuration (host mode)
- ✅ Production-ready deployment

## 📈 Next Steps

### Short Term
- [ ] Add more API endpoints
- [ ] Implement authentication/authorization
- [ ] Add input validation
- [ ] Add API documentation (Swagger/OpenAPI)

### Medium Term
- [ ] Set up Nginx reverse proxy
- [ ] Configure SSL certificate (Let's Encrypt)
- [ ] Implement rate limiting
- [ ] Add monitoring (PM2, Grafana)
- [ ] Set up automated backups

### Long Term
- [ ] CI/CD pipeline
- [ ] Unit & integration tests
- [ ] Caching (Redis)
- [ ] Load balancing
- [ ] Logging aggregation

## 📞 Quick Reference

### URLs
- **API:** http://173.212.218.31:3000
- **Health:** http://173.212.218.31:3000/health

### VPS Access
```bash
ssh root@173.212.218.31
cd /opt/wesolucions-backend
```

### Common Commands
```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build

# Check status
docker-compose ps

# Test database
docker-compose exec backend npm run test:db
```

## 🎓 Key Learnings

### Issues Resolved
1. **IPv6 DNS Resolution** - Resolved by using Supabase Connection Pooler (IPv4)
2. **Username Format** - Pooler requires `postgres.PROJECT_ID` format
3. **Password Encoding** - Special characters must be URL-encoded in connection strings
4. **Docker Networking** - Used host network mode for better compatibility

### Best Practices Implemented
- Environment variable management
- Connection pooling for database
- Health check endpoints
- Docker security (non-root user)
- Proper error handling
- Logging and monitoring

## 📄 License

ISC

---

**Deployed:** December 10, 2025  
**Status:** ✅ Production Ready  
**Version:** 1.0.0

Built with ❤️ for WEsolucions
