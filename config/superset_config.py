import logging
from datetime import timedelta
from flask_appbuilder.security.manager import AUTH_OAUTH, AUTH_DB
from superset.superset_typing import CacheConfig
from celery.schedules import crontab
from flask_caching.backends.rediscache import RedisCache
from superset.tasks.types import ExecutorType
from typing import Any, Callable, Literal, TYPE_CHECKING, TypedDict

from debug_middleware import DebugMiddleware
from custom_sso_security_manager import CustomSsoSecurityManager
from superset_utils import (
    authDriver,
    buildSqlAlchemyUri,
    env,
    usingGunicorn,
    isProd,
)

print("[CONFIG] Initializing...")

SUPERSET_ENV = env("SUPERSET_ENV")
SUPERSET_VERSION = env("SUPERSET_VERSION")

print(f"[CONFIG] SUPERSET_ENV: {SUPERSET_ENV}")
print(f"[CONFIG] SUPERSET_VERSION: {SUPERSET_VERSION}")

ENVIRONMENT_TAG_CONFIG = {
    "variable": "SUPERSET_ENV",
    "values": {
        "": {
            "color": "error.base",
            "text": "EnvNotFound",
        },
        "debug": {
            "color": "error.base",
            "text": f"Debug v{SUPERSET_VERSION}",
        },
        "dev": {
            "color": "error.base",
            "text": f"DevContainer v{SUPERSET_VERSION}",
        },
        "devcontainer": {
            "color": "error.base",
            "text": f"DevContainer v{SUPERSET_VERSION}",
        },
        "development": {
            "color": "error.base",
            "text": f"DevContainer v{SUPERSET_VERSION}",
        },
        "staging": {
            "color": "warning.base",
            "text": f"Staging v{SUPERSET_VERSION}",
        },
        "staging1": {
            "color": "warning.dark1",
            "text": f"Staging 1: v{SUPERSET_VERSION}",
        },
        "staging2": {
            "color": "warning.dark2",
            "text": f"Staging 2: v{SUPERSET_VERSION}",
        },
        "production": {
            "color": "",
            "text": "",
        },
    },
}

######################### Feature Flags #########################
FEATURE_FLAGS = {
    "DASHBOARD_FILTERS_EXPERIMENTAL": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
    "TAGGING_SYSTEM": True,
    "DASHBOARD_VIRTUALIZATION": True,
    "HORIZONTAL_FILTER_BAR": True,
    "ALERT_REPORTS": False,  # Disabling in production
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": True,
    # "PLAYWRIGHT_REPORTS_AND_THUMBNAILS": True,
    "ENABLE_DASHBOARD_SCREENSHOT_ENDPOINTS": True,
    # Generate screenshots (PDF or JPG) of dashboards using the web driver.
    # When disabled, screenshots are generated on the fly by the browser.
    # This feature flag is used by the download feature in the dashboard view.
    # It is dependent on ENABLE_DASHBOARD_SCREENSHOT_ENDPOINT being enabled.
    "ENABLE_DASHBOARD_DOWNLOAD_WEBDRIVER_SCREENSHOT": True,
    "SHARE_QUERIES_VIA_KV_STORE": True,
}

######################### Middleware #########################

ADDITIONAL_MIDDLEWARE = [DebugMiddleware]

######################### Authentication/Authorization #########################
# AUTH_TYPE = AUTH_OAUTH
AUTH_TYPE = AUTH_DB
# OKTA_CLIENT_ID = loadOktaClientId()
# OKTA_CLIENT_SECRET = loadOktaClientSecret()
# OKTA_CLIENT_REDIRECT_URI = env("OKTA_CLIENT_REDIRECT_URI")
# print(f"[CONFIG] {str(OKTA_CLIENT_REDIRECT_URI)}")
# https://<superset-webserver>/oauth-authorized/<provider-name>
# http://localhost:8088/oauth-authorized/okta
# OAUTH_PROVIDERS = [
#     {
#         "name": "okta",
#         "token_key": "access_token",
#         "icon": "fa-address-card",
#         "remote_app": {
#             "client_id": OKTA_CLIENT_ID,
#             "client_secret": OKTA_CLIENT_SECRET,
#             "redirect_uri": OKTA_CLIENT_REDIRECT_URI,
#             "client_kwargs": {"scope": "openid profile email groups"},
#             "access_token_method": "POST",  # HTTP Method to call access_token_url
#             "access_token_params": {},  # Additional parameters for calls to access_token_url},
#             "server_metadata_url": "<REPLACED>/.well-known/openid-configuration",
#         },
#     }
# ]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Admin"

print("[CONFIG] AUTH_USER_REGISTRATION_ROLE: " + str(AUTH_USER_REGISTRATION_ROLE))

# Initialize custom SSO security manager to use Okta
# CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

######################### Metastore (MySQL) #########################

SUPERSET_LOG_VIEW = False
# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = buildSqlAlchemyUri()
# SQLALCHEMY_ECHO = True
SQLALCHEMY_ENGINE_OPTIONS = {
    # "echo": "debug",
    # "echo_pool": "debug",
    "hide_parameters": False,
    "pool_recycle": 55,
    "pool_timeout": 55,
    "pool_size": 30,
    "max_overflow": 20,
    # "pool_pre_ping": True,
    # "pool_reset_on_return": None,
}

print(f"[CONFIG] SQLALCHEMY_ENGINE_OPTIONS: {SQLALCHEMY_ENGINE_OPTIONS}")
# Deny all data URLs
DATASET_IMPORT_ALLOWED_DATA_URLS = []


def isDruidUri(uri):
    return uri.drivername.__contains__("druid")


def containsConnectArgs(params):
    return params.__contains__("connect_args")


def containsSsl(connect_args):
    return connect_args.__contains__("ssl_client_cert")


def convertListToTuple(list):
    return tuple(list)


# Druid connection bugfix
def DB_CONNECTION_MUTATOR(uri, params, username, security_manager, source):
    print(f"[CONFIG] DB_CONNECTION_MUTATOR: {uri} {params} {username} {source}")
    if isDruidUri(uri):
        if containsConnectArgs(params):
            connect_args = params["connect_args"]
            if containsSsl(connect_args):
                certs = params["connect_args"]["ssl_client_cert"]
                params["connect_args"]["ssl_client_cert"] = convertListToTuple(certs)
    return uri, params


def SQL_QUERY_MUTATOR(  # pylint: disable=invalid-name,unused-argument
    sql, **kwargs: Any
) -> str:
    print(f"[CONFIG] kwargs: {kwargs}")
    return f"{sql}"


######################### Caching (Redis) #########################

REDIS_ENABLED = env("REDIS_ENABLED")
print("[CONFIG] REDIS_ENABLED: " + str(REDIS_ENABLED))


def redisEnabled():
    return REDIS_ENABLED == "true"


if redisEnabled():
    REDIS_HOST = env("REDIS_HOST")
    REDIS_PORT = env("REDIS_PORT")
    REDIS_CELERY_DB = env("REDIS_CELERY_DB", "0")
    REDIS_RESULTS_DB = env("REDIS_RESULTS_DB", "1")
    RESULTS_BACKEND = RedisCache(
        host=REDIS_HOST, port=REDIS_PORT, key_prefix="superset_result_"
    )

    REDIS_DATABASE_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    print("[CONFIG] REDIS_DATABASE_URI: " + str(REDIS_DATABASE_URI))

    CACHE_CONFIG = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_KEY_PREFIX": "superset_cache_",  # make sure this string is unique to avoid collisions
        "CACHE_DEFAULT_TIMEOUT": 86400,  # 60 seconds * 60 minutes * 24 hours
        "CACHE_REDIS_URL": f"{REDIS_DATABASE_URI}/{REDIS_RESULTS_DB}",
    }
    FILTER_STATE_CACHE_CONFIG = CACHE_CONFIG.copy()
    EXPLORE_FORM_DATA_CACHE_CONFIG = CACHE_CONFIG.copy()
    DATA_CACHE_CONFIG = CACHE_CONFIG.copy()
    THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG.copy()
    THUMBNAIL_CACHE_CONFIG["CACHE_KEY_PREFIX"] = "superset_thumbnail_"


######################### Celery Workers #########################
# Intialize Celery config
class CeleryConfig(object):
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.cache",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    log_level = "DEBUG"
    worker_prefetch_multiplier = 1
    task_acks_late = True
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
    }
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
        # "cache-warmup-hourly": {
        #     "task": "cache-warmup",
        #     "schedule": crontab(minute="*/30", hour="*"),
        #     "kwargs": {
        #         "strategy_name": "top_n_dashboards",
        #         "top_n": 10,
        #         "since": "14 days ago",
        #     },
        # },
    }


CELERY_CONFIG = CeleryConfig

######################### Webdriver #########################
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False

THUMBNAIL_SELENIUM_USER = "admin"
# ALERT_REPORTS_EXECUTE_AS = [ExecutorType.SELENIUM]

WEBDRIVER_AUTH_FUNC = authDriver
BROWSER_CONTEXT_AUTH_FUNC = None
WEBDRIVER_BASEURL = env("WEBDRIVER_BASEURL")
WEBDRIVER_BASEURL_USER_FRIENDLY = env("WEBDRIVER_BASEURL_USER_FRIENDLY")

print(f"[CONFIG] WEBDRIVER_BASEURL: {WEBDRIVER_BASEURL}")
print(f"[CONFIG] WEBDRIVER_BASEURL_USER_FRIENDLY: {WEBDRIVER_BASEURL_USER_FRIENDLY}")

WEBDRIVER_CONFIGURATION = {
    "service_log_path": "/app/logs/geckodriver.log",
}
WEBDRIVER_TYPE = "firefox"
# WEBDRIVER_TYPE = "chrome"
# WEBDRIVER_OPTION_ARGS = [
#     "--headless",
#     "--single-process",
#     "--marionette",
#     "--log=trace",
# ]

SCREENSHOT_SELENIUM_RETRIES = 5
SCREENSHOT_LOCATE_WAIT = int(timedelta(seconds=60).total_seconds())
SCREENSHOT_LOAD_WAIT = int(timedelta(seconds=60).total_seconds())
SCREENSHOT_SELENIUM_HEADSTART = 5
SCREENSHOT_SELENIUM_ANIMATION_WAIT = 2

# CSRF
# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = False
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []
# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365
TALISMAN_ENABLED = False

SESSION_COOKIE_HTTPONLY = False  # Prevent cookie from being read by frontend JS?
SESSION_COOKIE_SECURE = True  # Prevent cookie from being transmitted over non-tls?
SESSION_COOKIE_SAMESITE = "Lax"  # One of [None, 'None', 'Lax', 'Strict']

# SLACK_API_TOKEN = "slack_api_token"
# print(f"[CONFIG] SLACK_API_TOKEN: {SLACK_API_TOKEN[:5]}**********")


### Misc. ###

# If you're NOT using Gunicorn, you may want to disable the use of
# flask-compress by setting COMPRESS_REGISTER = False
COMPRESS_REGISTER = True
if not usingGunicorn():
    COMPRESS_REGISTER = False

print(f"[CONFIG] COMPRESS_REGISTER: {COMPRESS_REGISTER}")

if isProd():
    SSL_KEY_FILE = env("SSL_KEY_FILE")
    SSL_CERT_FILE = env("SSL_CERT_FILE")
    SSL_CERT_PATH = env("SSL_CERT_PATH")

    print("[CONFIG] SSL_KEY_FILE: " + str(SSL_KEY_FILE))
    print("[CONFIG] SSL_CERT_FILE: " + str(SSL_CERT_FILE))
    print("[CONFIG] SSL_CERT_PATH: " + str(SSL_CERT_PATH))

SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_TIMEOUT = 300

SUPERSET_WEBSERVER_TIMEOUT = int(timedelta(minutes=5).total_seconds())

SUPERSET_SECRET_KEY = env("SUPERSET_SECRET_KEY")
print(f"[CONFIG] SUPERSET_SECRET_KEY: {SUPERSET_SECRET_KEY[:4]}**********")

# Uncomment to setup Your App name
APP_NAME = "Superset"

# Specify the App icon
APP_ICON = "/static/assets/images/superset-logo-horiz.png"

# Specify where clicking the logo would take the user
# e.g. setting it to '/' would take the user to '/superset/welcome/'
LOGO_TARGET_PATH = None

# Specify tooltip that should appear when hovering over the App Icon/Logo
LOGO_TOOLTIP = ""

# Specify any text that should appear to the right of the logo
LOGO_RIGHT_TEXT = ""
