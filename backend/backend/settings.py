"""
Django settings for backend project.
兼容本地开发 (HTTP) 与 服务器生产 (HTTPS)
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 1. 环境切换开关 (关键)
# ==========================================
# 本地 .env 设置 DEBUG=True, 服务器 .env 设置 DEBUG=False
DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-dev')



# 允许的 Host
ALLOWED_HOSTS = [
    '82.156.32.183',
    '127.0.0.1',
    'localhost',
    'www.soragen.cloud',
    'soragen.cloud',
    '.soragen.cloud',
]

# APP 定义
INSTALLED_APPS = [
    "simpleui",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "captcha",
    "users",
    "videos",
    "SoraApp",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "SoraApp.middleware.RequestLogMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# 数据库
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 语言时区
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root') # Required for collectstatic in production

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'users.User'

# ==========================================
# 2. 动态 CORS / CSRF 配置 (核心)
# ==========================================

CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    # --------------------------------------
    # 本地开发配置 (HTTP)
    # --------------------------------------
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
    
    # 本地不强制要求 HTTPS
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    
else:
    # --------------------------------------
    # 服务器生产配置 (HTTPS)
    # --------------------------------------
    CORS_ALLOWED_ORIGINS = [
        "https://www.soragen.cloud",
        "https://soragen.cloud",
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
    
    # 强制安全传输
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SAMESITE = 'Lax'

# ==========================================
# 3. 业务插件
# ==========================================
SESSION_COOKIE_AGE = 48 * 3600 # 48 hours in seconds

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.authentication.ExpiringTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

# ... (其他的 Captcha、OpenAI 等配置保持不变) ...

# OpenAI 助手
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', "https://api.jiekou.ai/openai")
OPENAI_MODEL = os.getenv('OPENAI_MODEL', "gpt-5.1")
PROMPT_GENERATION_COST = 20

# Sora API
SORA_API_KEY = os.getenv('SORA_API_KEY')

WUYIN_API_KEY=os.getenv('WUYIN_API_KEY')
APIMART_API_KEY =os.getenv('APIMART_API_KEY')

# 验证码设置
CAPTCHA_IMAGE_SIZE = (120, 40)
CAPTCHA_FONT_SIZE = 28
CAPTCHA_LETTER_ROTATION = (-5, 5)
CAPTCHA_BACKGROUND_COLOR = '#ffffff'
CAPTCHA_FOREGROUND_COLOR = '#0011ff'
CAPTCHA_NOISE_FUNCTIONS = []
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_LETTER_SAMPLES = '0123456789'

# 阿里云短信
ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')

# SimpleUI
SIMPLEUI_HOME_PAGE = '/admin/dashboard/'
SIMPLEUI_HOME_TITLE = '管理后台'