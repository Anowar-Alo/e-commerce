import os
from pathlib import Path
import environ

# Initialize environ
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-development-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'accounts',
    'core',
    'products',
    'orders',
    'payments',
    'cart',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'core.context_processors.categories',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'
ASGI_APPLICATION = 'ecommerce.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
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
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Login/Logout URLs
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@example.com'

# Stripe Configuration
STRIPE_PUBLIC_KEY = 'your_stripe_public_key'
STRIPE_SECRET_KEY = 'your_stripe_secret_key'
STRIPE_WEBHOOK_SECRET = 'your_stripe_webhook_secret'

# Payment Settings
PAYMENT_METHODS = {
    'card': {
        'name': 'Credit/Debit Card',
        'icon': 'fa-credit-card',
    },
    'bank': {
        'name': 'Bank Account',
        'icon': 'fa-university',
    },
    'wallet': {
        'name': 'Digital Wallet',
        'icon': 'fa-wallet',
    },
    'upi': {
        'name': 'UPI',
        'icon': 'fa-mobile-alt',
    },
}

# Currency Settings
CURRENCY = 'USD'
CURRENCY_SYMBOL = '$'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Channel layers for real-time features
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF settings
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Session settings
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Remove Django-Axes settings since we're not using it
AXES_FAILURE_LIMIT = None
AXES_LOCK_OUT_AT_FAILURE = None
AXES_COOLOFF_TIME = None
AXES_ENABLED = None
AXES_VERBOSE = None
AXES_META_PRECEDENCE_ORDER = None

# Google reCAPTCHA settings
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default='')

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}

# AWS S3 settings (optional)
if 'AWS_ACCESS_KEY_ID' in env:
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Cart settings
CART_SESSION_ID = 'cart'

# Admin settings
ADMIN_URL = 'admin/'
ADMIN_SITE_HEADER = 'E-commerce Administration'
ADMIN_SITE_TITLE = 'E-commerce Admin Portal'
ADMIN_INDEX_TITLE = 'Welcome to E-commerce Admin Portal'

# Unfold settings
UNFOLD = {
    "SITE_TITLE": "E-commerce Admin",
    "SITE_HEADER": "E-commerce Administration",
    "SITE_SYMBOL": "shopping_cart",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "app": "core",
                "icon": "dashboard",
                "items": [
                    {
                        'title': 'Dashboard',
                        "name": "Overview",
                        "link": "/admin/dashboard/",
                        "icon": "dashboard",
                    },
                    {
                        'title': 'Analytics',
                        "name": "Analytics",
                        "link": "/admin/analytics/",
                        "icon": "analytics",
                    }
                ]
            },
            {
                "title": "Products",
                "app": "products",
                "icon": "inventory_2",
                "items": [
                    {
                        'title': 'Products',
                        "name": "Products",
                        "link": "/admin/products/product/",
                        "icon": "inventory_2",
                    },
                    {
                        'title': 'Categories',
                        "name": "Categories",
                        "link": "/admin/products/category/",
                        "icon": "category",
                    },
                    {
                        'title': 'Brands',
                        "name": "Brands",
                        "link": "/admin/products/brand/",
                        "icon": "branding_watermark",
                    }
                ]
            },
            {
                "title": "Orders",
                "app": "orders",
                "icon": "shopping_cart",
                "items": [
                    {
                        "name": "Orders",
                        "link": "/admin/orders/order/",
                        "icon": "shopping_cart",
                    },
                    {
                        "name": "Refunds",
                        "link": "/admin/orders/refund/",
                        "icon": "money_off",
                    }
                ]
            },
            {
                "title": "Customers",
                "app": "auth",
                "icon": "people",
                "items": [
                    {
                        "name": "Users",
                        "link": "/admin/auth/user/",
                        "icon": "person",
                    },
                    {
                        "name": "Groups",
                        "link": "/admin/auth/group/",
                        "icon": "group",
                    }
                ]
            },
            {
                "title": "Settings",
                "app": "core",
                "icon": "settings",
                "items": [
                    {
                        "name": "General",
                        "link": "/admin/core/settings/",
                        "icon": "settings",
                    },
                    {
                        "name": "Payment Methods",
                        "link": "/admin/core/paymentmethod/",
                        "icon": "payment",
                    }
                ]
            }
        ]
    },
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    }
}

# Remove django-allauth settings since we're not using it
SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = None
ACCOUNT_EMAIL_REQUIRED = None
ACCOUNT_EMAIL_VERIFICATION = None
ACCOUNT_USERNAME_REQUIRED = None
ACCOUNT_UNIQUE_EMAIL = None
ACCOUNT_RATE_LIMITS = None
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = None
ACCOUNT_SESSION_REMEMBER = None
ACCOUNT_USERNAME_MIN_LENGTH = None
ACCOUNT_PASSWORD_MIN_LENGTH = None
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = None
ACCOUNT_LOGOUT_ON_GET = None
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = None
ACCOUNT_LOGIN_ON_PASSWORD_RESET = None
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_SUBJECT_PREFIX = None
ACCOUNT_DEFAULT_HTTP_PROTOCOL = None
ACCOUNT_LOGOUT_REDIRECT_URL = None
ACCOUNT_LOGIN_REDIRECT_URL = None
ACCOUNT_EMAIL_CONFIRMATION_URL = None
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = None
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = None
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = None
ACCOUNT_EMAIL_CONFIRMATION_HMAC = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_CHANGE = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_ADD = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_REMOVE = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_PRIMARY = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_VERIFIED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_UNVERIFIED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_BLACKLIST = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_WHITELIST = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_REQUIRED_CUSTOM = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_REQUIRED_CUSTOM = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_REQUIRED = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_REQUIRED_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_REQUIRED_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_REQUIRED_OPTIONAL = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_OPTIONAL_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_OPTIONAL_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_OPTIONAL_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_REQUIRED_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_REQUIRED_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_REQUIRED_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_CUSTOM_REQUIRED_OPTIONAL_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_BLACKLIST_CUSTOM_REQUIRED_OPTIONAL_DEFAULT = None
ACCOUNT_EMAIL_CONFIRMATION_EMAIL_DOMAINS_WHITELIST_CUSTOM_REQUIRED_OPTIONAL_DEFAULT = None

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "E-commerce Admin",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "E-commerce",
    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "E-commerce",
    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": None,
    # Welcome text on the login screen
    "welcome_sign": "Welcome to E-commerce Admin",
    # Copyright on the footer
    "copyright": "E-commerce Ltd",
    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "auth.User",
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},
        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "core"},
    ],
    #############
    # User Menu #
    #############
    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "core", "products", "orders"],
    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "core": [{
            "name": "Dashboard",
            "url": "admin:core_dashboard_changelist",
            "icon": "fas fa-chart-line",
            "permissions": ["core.view_dashboard"]
        }]
    },
    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core": "fas fa-store",
        "products": "fas fa-box",
        "orders": "fas fa-shopping-cart",
        "payments": "fas fa-credit-card",
        "cart": "fas fa-shopping-bag",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,
    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,
    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
