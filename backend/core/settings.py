import os
from pathlib import Path

# URL of the frontend application, used for redirects after OAuth
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
import environ
import dj_database_url # Still useful for parsing DATABASE_URL if not using env.db_url() directly for all cases

# Build base project directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Initialize django-environ
# Define schema for environment variables (casting and default values)
env = environ.Env(
    # General Site Info
    SITE_NAME=(str, "Reporter System"),
    SITE_URL=(str, "http://127.0.0.1:8000"),
    ENVIRONMENT=(str, "development"), # 'development' or 'production'
    # Security
    SECRET_KEY=(str, 'your-default-secret-key-for-dev-if-not-in-env'), # IMPORTANT: Override in .env
    DEBUG=(bool, False), # IMPORTANT: Set to True in .env for development
    ALLOWED_HOSTS=(list, ['127.0.0.1', '192.168.1.28', 'localhost']),
    CSRF_TRUSTED_ORIGINS=(list, []),
    # Database
    DATABASE_URL=(str, f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
    # Email
    EMAIL_BACKEND=(str, 'django.core.mail.backends.console.EmailBackend'), # Default to console for dev
    EMAIL_HOST=(str, 'localhost'),
    EMAIL_PORT=(int, 1025),
    EMAIL_USE_TLS=(bool, False),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    DEFAULT_FROM_EMAIL=(str, 'webmaster@localhost'),
    # Google Ads specific settings
    DEFAULT_ADMIN_EMAIL=(str, 'admin@localhost'),
    # Other services from your .env
    OPENAI_API_KEY=(str, ''),
    GOOGLE_CLIENT_ID=(str, ''),
    GOOGLE_CLIENT_SECRET=(str, ''),
    GOOGLE_ACCOUNT_EMAIL=(str, ''),
    STRIPE_SECRET_KEY=(str, ''),
    STRIPE_PUBLISHABLE_KEY=(str, ''),
    GOOGLE_DEVELOPER_TOKEN=(str, ''), # Added GOOGLE_DEVELOPER_TOKEN
    GOOGLE_LOGIN_CUSTOMER_ID=(str, ''), # Added GOOGLE_LOGIN_CUSTOMER_ID (optional for MCC)
    BINOM_API_KEY=(str, ''), # Define schema for Binom API Key
    BINOM_API_URL=(str, '')  # Define schema for Binom API URL
)

# Read .env file located at the project root (backend/.env)
environ.Env.read_env(BASE_DIR / '.env')



# ==== Site Information ====
SITE_NAME = env("SITE_NAME")
SITE_URL = env("SITE_URL")
ENVIRONMENT = env("ENVIRONMENT")

# Load service account json differently per environment
if ENVIRONMENT == 'production':
    GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # full JSON string in env var
else:
    GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'backend', 'reports', 'service_account.json')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG is read from .env; your .env currently has DEBUG=False.
# For development, you might want to set DEBUG=True in your .env file.
DEBUG = env('DEBUG')

# Allowed hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'reports',  # your reports app
    'django_extensions', # Added for running dev server with SSL
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # important for React frontend CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# CORS Settings
CORS_ALLOW_CREDENTIALS = True # Allow cookies to be sent with requests

if ENVIRONMENT == "production":
    # TODO: Replace with your actual frontend production domain
    CORS_ALLOWED_ORIGINS = [
        env('SITE_URL'), # Assumes SITE_URL is your frontend URL in production
        "http://192.168.1.28:3000", # Keep for local network access if needed
    ]
else: # Development settings
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# Database
# Load Google account email from environment
GOOGLE_ACCOUNT_EMAIL = env('GOOGLE_ACCOUNT_EMAIL')

# Session Cookie Settings for Cross-Origin Requests
# These are necessary for the frontend (e.g., localhost:3000) to send session cookies to the backend (e.g., localhost:8000)
SESSION_COOKIE_SAMESITE = 'Lax' if ENVIRONMENT == 'development' else 'None'
SESSION_COOKIE_SECURE = False if ENVIRONMENT == 'development' else True
CSRF_COOKIE_SAMESITE = 'Lax' if ENVIRONMENT == 'development' else 'None'
CSRF_COOKIE_SECURE = False if ENVIRONMENT == 'development' else True

# CSRF Trusted Origins, read from .env
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': env.db_url(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}
# Production-specific DB settings like SSL can be handled within the env.db_url call if needed
if ENVIRONMENT == "production":
    DATABASES['default']['CONN_MAX_AGE'] = 600
    DATABASES['default']['SSL_REQUIRE'] = True

# Email settings
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT') # Casting to int
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS') # Casting to bool
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
DEFAULT_ADMIN_EMAIL = env('DEFAULT_ADMIN_EMAIL')

# Other Service API Keys from .env
OPENAI_API_KEY = env('OPENAI_API_KEY')
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')
GOOGLE_DEVELOPER_TOKEN = env('GOOGLE_DEVELOPER_TOKEN')
GOOGLE_LOGIN_CUSTOMER_ID = env('GOOGLE_LOGIN_CUSTOMER_ID') # Optional, defaults to '' if not in .env
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# Binom API Settings
BINOM_API_KEY = env('BINOM_API_KEY')
BINOM_API_URL = env('BINOM_API_URL')

# Static files (CSS, JavaScript, Images)
# Ensure this is defined only once and correctly.
# The one at the end of the file was 'static/', this one is '/static/'
STATIC_URL = '/static/'



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==== OAuth Redirect URIs (Dual Callback Support) ====
BACKEND_OAUTH_REDIRECT_URI = env("BACKEND_OAUTH_REDIRECT_URI")
FRONTEND_OAUTH_REDIRECT_URI = env("FRONTEND_OAUTH_REDIRECT_URI")
