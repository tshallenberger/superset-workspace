import logging
import os
import pprint

from os.path import exists
from datetime import timedelta
from typing import Optional

from pathlib import Path

from flask_appbuilder.security.manager import AUTH_OAUTH
from werkzeug.wrappers import Request

from cachelib.file import FileSystemCache
from celery.schedules import crontab

logger = logging.getLogger()


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
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


class SampleMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # not Flask request - from werkzeug.wrappers import Request
        request = Request(environ)
        if request.path == "/login":
            print("[DEBUG] path: %s, url: %s" % (request.path, request.url))
            pprint.pprint(request)
            pprint.pprint(environ)
        return self.app(environ, start_response)


ADDITIONAL_MIDDLEWARE = [SampleMiddleware]

WTF_CSRF_ENABLED = False
SESSION_COOKIE_HTTPONLY = False  # Prevent cookie from being read by frontend JS?
SESSION_COOKIE_SECURE = False  # Prevent cookie from being transmitted over non-tls?
SESSION_COOKIE_SAMESITE = "Lax"  # One of [None, 'None', 'Lax', 'Strict']

# Load service credentials (auth Certs)

SUPERSET_ENV = get_env_variable("SUPERSET_ENV")
print("[DEBUG] SUPERSET_ENV: " + SUPERSET_ENV)

ENVIRONMENT_TAG_CONFIG = {
    "variable": "SUPERSET_ENV",
    "values": {
        "debug": {
            "color": "error.base",
            "text": "flask-debug",
        },
        "devcontainer": {
            "color": "error.base",
            "text": "DevContainer",
        },
        "staging": {
            "color": "warning.base",
            "text": "Staging",
        },
        "prod": {
            "color": "",
            "text": "",
        },
    },
}

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "General"

DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT")
DATABASE_DB = get_env_variable("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

print("[DEBUG] SQLALCHEMY_DATABASE_URI: " + str(SQLALCHEMY_DATABASE_URI))

# Initialize Redis config
REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")

REDIS_DATABASE_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}"

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

print("[DEBUG] REDIS_DATABASE_URI: " + str(REDIS_DATABASE_URI))


# Intialize Celery config
class CeleryConfig(object):
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    CELERY_IMPORTS = ("superset.sql_lab", "superset.tasks")
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    CELERYD_LOG_LEVEL = "DEBUG"
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ACKS_LATE = False
    CELERYBEAT_SCHEDULE = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {
    "DASHBOARD_FILTERS_EXPERIMENTAL": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# if SUPERSET_ENV == "prod":
FILTER_STATE_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_filter_cache",
    "CACHE_REDIS_URL": f"{REDIS_DATABASE_URI}/0",
}
DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_KEY_PREFIX": "superset_results",  # make sure this string is unique to avoid collisions
    "CACHE_DEFAULT_TIMEOUT": 86400,  # 60 seconds * 60 minutes * 24 hours
    "CACHE_REDIS_URL": f"{REDIS_DATABASE_URI}/0",
}

ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = "http://superset:8088/"
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL
SQLLAB_CTAS_NO_LIMIT = True
SUPERSET_WEBSERVER_TIMEOUT = int(timedelta(minutes=5).total_seconds())
SQLLAB_TIMEOUT = 300

# PREVIOUS_SECRET_KEY = 'secret'
SUPERSET_SECRET_KEY = "secret"
