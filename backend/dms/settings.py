from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# Cấu hình bảo mật và môi trường mặc định
SECRET_KEY = 'django-insecure-dental-clinic-system-key-change-me'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Định nghĩa các module gốc
ROOT_URLCONF = 'dms.urls'
WSGI_APPLICATION = 'dms.wsgi.application'

# SQLite is the portable default for local development. Set DMS_DB_ENGINE=mssql
# to use SQL Server, and configure its connection through environment variables.
if os.environ.get("DMS_DB_ENGINE") == "mssql":
    DATABASES = {
        "default": {
            "ENGINE": "mssql",
            "NAME": os.environ.get("DMS_DB_NAME", "dental_clinic_db"),
            "HOST": os.environ.get("DMS_DB_HOST", "localhost"),
            "PORT": os.environ.get("DMS_DB_PORT", "1433"),
            "OPTIONS": {
                "driver": os.environ.get("DMS_DB_DRIVER", "ODBC Driver 17 for SQL Server"),
                "trusted_connection": os.environ.get("DMS_DB_TRUSTED_CONNECTION", "yes"),
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.environ.get("DMS_DB_NAME", BASE_DIR / "db.sqlite3"),
        }
    }

VIETQR_BANK_ID = os.environ.get("DMS_VIETQR_BANK_ID", "").strip().upper()
VIETQR_ACCOUNT_NUMBER = os.environ.get("DMS_VIETQR_ACCOUNT_NUMBER", "").strip()
VIETQR_ACCOUNT_NAME = os.environ.get("DMS_VIETQR_ACCOUNT_NAME", "").strip()

# 2. Cấu hình các App được cài đặt trong Project
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Thêm các thư viện và app của nhóm mình vào:
    'rest_framework',
    'corsheaders',
    'authentication',
    'clinic',
    'appointments',
]

# 3. Khai báo Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# 4. Cấu hình Django REST Framework và JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'ai_chat': '30/hour',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'