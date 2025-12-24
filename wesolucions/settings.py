"""
Django settings for wesolucions project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'vendor',
    'marketplace',
    'products',
    'export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wesolucions.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wesolucions.wsgi.application'

# Database - Supabase PostgreSQL Configuration
def get_database_config():
    """
    Configure database connection for Supabase PostgreSQL.
    Supports both pooler and direct connections.
    """
    # Check if using pooler connection
    if os.getenv('SUPABASE_DB_HOST') and 'pooler' in os.getenv('SUPABASE_DB_HOST', ''):
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('SUPABASE_DB_NAME', 'postgres'),
            'USER': os.getenv('SUPABASE_DB_USER', 'postgres.hihygeuawvzzrundvzev'),
            'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD', ''),
            'HOST': os.getenv('SUPABASE_DB_HOST', ''),
            'PORT': os.getenv('SUPABASE_DB_PORT', '6543'),
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 15,
            },
            'CONN_MAX_AGE': 600,  # Connection pooling
        }
    
    # Use DATABASE_URL if available (for direct connections)
    if os.getenv('DATABASE_URL') and 'pooler' not in os.getenv('SUPABASE_DB_HOST', ''):
        from urllib.parse import urlparse
        url = os.getenv('DATABASE_URL')
        parsed = urlparse(url)
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or '5432',
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 15,
            },
            'CONN_MAX_AGE': 600,
        }
    
    # Fallback to individual parameters
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SUPABASE_DB_NAME', 'postgres'),
        'USER': os.getenv('SUPABASE_DB_USER', ''),
        'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD', ''),
        'HOST': os.getenv('SUPABASE_DB_HOST', ''),
        'PORT': os.getenv('SUPABASE_DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require' if os.getenv('SUPABASE_DB_SSL', 'true') == 'true' else 'disable',
            'connect_timeout': 15,
        },
        'CONN_MAX_AGE': 600,
    }

DATABASES = {
    'default': get_database_config()
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
# Get Vercel frontend URL from environment
VERCEL_FRONTEND_URL = os.getenv('VERCEL_FRONTEND_URL', '')

# Production CORS origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://w-esolucions-frontend.vercel.app",
]

# Add Vercel domain if provided
if VERCEL_FRONTEND_URL:
    if VERCEL_FRONTEND_URL not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(VERCEL_FRONTEND_URL)

# Allow all origins in development, specific origins in production
CORS_ALLOW_ALL_ORIGINS = DEBUG

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://w-esolucions-frontend.vercel.app",
]

# Add Vercel domain if provided
if VERCEL_FRONTEND_URL:
    if VERCEL_FRONTEND_URL not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(VERCEL_FRONTEND_URL)

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
