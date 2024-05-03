import logging
import os
from datetime import timedelta
from typing import Optional
from flask_appbuilder.security.manager import AUTH_OAUTH
from superset.superset_typing import CacheConfig
from celery.schedules import crontab
from flask_caching.backends.rediscache import RedisCache
from superset.tasks.types import ExecutorType
from selenium.webdriver.remote.webdriver import WebDriver
from superset.utils.machine_auth import MachineAuthProvider
from debug_middleware import DebugMiddleware
from custom_sso_security_manager import CustomSsoSecurityManager
from superset.utils.urls import headless_url


def env(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


SUPERSET_ENV = env("SUPERSET_ENV")
print("[DEBUG] SUPERSET_ENV: " + SUPERSET_ENV)


def isProd():
    return SUPERSET_ENV == "prod"





def authDriver(driver: WebDriver, user) -> WebDriver:
    print(f"[DEBUG] ##### auth_driver BEGIN {driver} #####")
    driver.get(headless_url("/doesnotexist"))
    try:
        cookies = MachineAuthProvider.get_auth_cookies(user)
        for cookie_name, cookie_val in cookies.items():
            driver.add_cookie(dict(name=cookie_name, value=cookie_val))
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
    return driver


def buildSqlAlchemyUri():
    PATH_TO_CERT = env("PATH_TO_CERT")
    PATH_TO_KEY = env("PATH_TO_KEY")
    PATH_TO_CA = env("PATH_TO_CA")

    cert_exists = os.path.exists(PATH_TO_CERT)
    key_exists = os.path.exists(PATH_TO_KEY)
    ca_exists = os.path.exists(PATH_TO_CA)

    print(f"[DEBUG] PATH_TO_CERT: '{PATH_TO_CERT}' -- exists: {cert_exists}")
    print(f"[DEBUG] PATH_TO_KEY: '{PATH_TO_KEY}' -- exists: {key_exists}")
    print(f"[DEBUG] PATH_TO_CA: '{PATH_TO_CA}' -- exists: {ca_exists}")
    
    DATABASE_DIALECT = env("DATABASE_DIALECT")
    DATABASE_USER = env("DATABASE_USER")
    DATABASE_PASSWORD = env("DATABASE_PASSWORD")
    DATABASE_HOST = env("DATABASE_HOST")
    DATABASE_PORT = env("DATABASE_PORT")
    DATABASE_NAME = env("DATABASE_NAME")

    # The SQLAlchemy connection string.
    SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
        DATABASE_DIALECT,
        DATABASE_USER,
        DATABASE_PASSWORD,
        DATABASE_HOST,
        DATABASE_PORT,
        DATABASE_NAME,
    )
    if isProd():
        SQLALCHEMY_DATABASE_URI = "%s?ssl_cert=%s&ssl_key=%s&ssl_ca=%s" % (
            SQLALCHEMY_DATABASE_URI,
            PATH_TO_CERT,
            PATH_TO_KEY,
            PATH_TO_CA,
        )
    print("[DEBUG] SQLALCHEMY_DATABASE_URI: " + str(SQLALCHEMY_DATABASE_URI))
    return SQLALCHEMY_DATABASE_URI


print("[DEBUG] Initializing...")

SUPERSET_ENV = env("SUPERSET_ENV")
print("[DEBUG] SUPERSET_ENV: " + SUPERSET_ENV)

ENVIRONMENT_TAG_CONFIG = {
    "variable": "SUPERSET_ENV",
    "values": {
        "": {
            "color": "error.base",
            "text": "Local",
        },
        "debug": {
            "color": "error.base",
            "text": "Debug",
        },
        "dev": {
            "color": "error.base",
            "text": "DevContainer",
        },
        "development": {
            "color": "error.base",
            "text": "Development",
        },
        "staging": {
            "color": "warning.base",
            "text": "Staging",
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
    "ALERT_REPORTS": True,  # Disabling in production
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": True,
}

######################### Middleware #########################

ADDITIONAL_MIDDLEWARE = [DebugMiddleware]

######################### CKMS/Athenz #########################


######################### Authentication/Authorization #########################
# AUTH_TYPE = AUTH_OAUTH

# OKTA_CLIENT_ID = loadOktaClientId()
# OKTA_CLIENT_SECRET = loadOktaClientSecret()
# OKTA_CLIENT_REDIRECT_URI = env("OKTA_CLIENT_REDIRECT_URI")
# print(f"[DEBUG] {str(OKTA_CLIENT_REDIRECT_URI)}")
# # https://<superset-webserver>/oauth-authorized/<provider-name>
# # http://localhost:8088/oauth-authorized/okta
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
#             "server_metadata_url": "https://ouryahoo.okta.com/oauth2/ausdqo06iBskQbfv0696/.well-known/openid-configuration",
#         },
#     }
# ]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Admin"
print("[DEBUG] AUTH_USER_REGISTRATION_ROLE: " + str(AUTH_USER_REGISTRATION_ROLE))

# Initialize custom SSO security manager to use Okta
CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

######################### Metastore (MySQL) #########################

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = buildSqlAlchemyUri()

SQLALCHEMY_ENGINE_OPTIONS = {
    # "echo": "debug",
    # "echo_pool": "debug",
    # "hide_parameters": False,
    "pool_recycle": 50,
    "pool_timeout": 50,
    "pool_size": 30,
    "max_overflow": 10,
}


def DB_CONNECTION_MUTATOR(uri, params, username, security_manager, source):
    print(f"[DEBUG] DB_CONNECTION_MUTATOR: {uri} {params} {username} {source}")
    return uri, params


# @event.listens_for(Session, "after_attach")
# def set_wait_timeout(session, transaction, connection):
#     print("[DEBUG] after_attach: SET wait_timeout=300;")
#     session.execute("SET wait_timeout=300;")


######################### Caching (Redis) #########################

REDIS_ENABLED = env("REDIS_ENABLED")
print("[DEBUG] REDIS_ENABLED: " + str(REDIS_ENABLED))


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
    print("[DEBUG] REDIS_DATABASE_URI: " + str(REDIS_DATABASE_URI))

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
    worker_prefetch_multiplier = 10
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
ALERT_REPORTS_EXECUTE_AS = [ExecutorType.SELENIUM]

WEBDRIVER_AUTH_FUNC = authDriver
WEBDRIVER_BASEURL = env("WEBDRIVER_BASEURL")
WEBDRIVER_BASEURL_USER_FRIENDLY = env("WEBDRIVER_BASEURL_USER_FRIENDLY")
WEBDRIVER_CONFIGURATION = {
    "service_log_path": "/app/geckodriver.log",
}
WEBDRIVER_TYPE = "firefox"
# WEBDRIVER_OPTION_ARGS = [
#     # "--log=trace"
#     # "--headless",
#     # "--marionette",
# ]

SCREENSHOT_LOCATE_WAIT = int(timedelta(seconds=50).total_seconds())
SCREENSHOT_LOAD_WAIT = int(timedelta(minutes=5).total_seconds())
SCREENSHOT_SELENIUM_HEADSTART = 10
WTF_CSRF_ENABLED = False
SESSION_COOKIE_HTTPONLY = False  # Prevent cookie from being read by frontend JS?
SESSION_COOKIE_SECURE = False  # Prevent cookie from being transmitted over non-tls?
SESSION_COOKIE_SAMESITE = "Lax"  # One of [None, 'None', 'Lax', 'Strict']


# print(f"[DEBUG] SLACK_API_TOKEN: {SLACK_API_TOKEN[:17]}**********")


### Misc. ###
COMPRESS_REGISTER = False

if isProd():
    SSL_KEY_FILE = env("SSL_KEY_FILE")
    SSL_CERT_FILE = env("SSL_CERT_FILE")
    SSL_CERT_PATH = env("SSL_CERT_PATH")

    print("[DEBUG] SSL_KEY_FILE: " + str(SSL_KEY_FILE))
    print("[DEBUG] SSL_CERT_FILE: " + str(SSL_CERT_FILE))
    print("[DEBUG] SSL_CERT_PATH: " + str(SSL_CERT_PATH))

SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_TIMEOUT = 300

SUPERSET_WEBSERVER_TIMEOUT = int(timedelta(minutes=5).total_seconds())

# PREVIOUS_SECRET_KEY = 'secret'
SUPERSET_SECRET_KEY = "secret"


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
