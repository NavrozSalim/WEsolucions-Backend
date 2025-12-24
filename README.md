# WEsolucions Backend - Django

Django backend application with Supabase PostgreSQL database connection and VPS deployment setup.

## Project Structure

```
.
├── wesolucions/          # Django project directory
│   ├── settings.py      # Django settings with Supabase configuration
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── deploy.sh           # VPS deployment script
```

## Setup

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with your Supabase credentials:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgresql://user:password@host:port/database
   SUPABASE_DB_HOST=your-supabase-host
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your-password
   SUPABASE_DB_SSL=true
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Database Configuration

The project is configured to connect to Supabase PostgreSQL with support for:
- **Pooler connections** (port 6543)
- **Direct connections** (port 5432)
- **DATABASE_URL** connection string
- **Individual parameters** (fallback)

The database configuration is automatically selected based on your environment variables in `wesolucions/settings.py`.

## VPS Deployment

### Using Docker Compose

1. **Deploy to VPS:**
   ```bash
   ./deploy.sh
   ```

2. **Run migrations in container:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **Create superuser in container:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

### Manual Docker Commands

```bash
# Build image
docker build -t wesolucions-backend:latest .

# Run container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

## Environment Variables

Required environment variables:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `SUPABASE_DB_HOST` - Supabase database host
- `SUPABASE_DB_PORT` - Database port (5432 for direct, 6543 for pooler)
- `SUPABASE_DB_NAME` - Database name
- `SUPABASE_DB_USER` - Database user
- `SUPABASE_DB_PASSWORD` - Database password
- `SUPABASE_DB_SSL` - Set to `true` for SSL connections

Optional:
- `DATABASE_URL` - Full PostgreSQL connection URL

## Health Check

The application includes a health check endpoint:
- `GET /health` - Returns `{"status": "healthy"}`

## Admin Panel

Access the Django admin panel at:
- `http://localhost:8000/admin` (local)
- `http://your-vps-ip:8000/admin` (VPS)

