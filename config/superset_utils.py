import logging
import os
import pprint

from os.path import exists
from datetime import timedelta
from typing import Optional
from pathlib import Path

from flask_appbuilder.security.manager import AUTH_OAUTH
from superset.superset_typing import CacheConfig
from superset.utils.machine_auth import MachineAuthProvider
from werkzeug.wrappers import Request
from cachelib.file import FileSystemCache
from celery.schedules import crontab

from custom_sso_security_manager import CustomSsoSecurityManager

from selenium.webdriver.remote.webdriver import WebDriver

from flask_caching.backends.rediscache import RedisCache
from superset.tasks.types import ExecutorType

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


def isDev():
    return SUPERSET_ENV.startswith("dev") or SUPERSET_ENV.startswith("debug")


def isStaging():
    return SUPERSET_ENV.startswith("staging")


def isProd():
    return SUPERSET_ENV == "production"


def usingGunicorn():
    return isProd() or isStaging()


# PATH_TO_CERT = env("PATH_TO_CERT")
# PATH_TO_KEY = env("PATH_TO_KEY")
# PATH_TO_CA = env("PATH_TO_CA")

# cert_exists = exists(PATH_TO_CERT)
# key_exists = exists(PATH_TO_KEY)
# ca_exists = exists(PATH_TO_CA)

# print(f"[CONFIG] PATH_TO_CERT: '{PATH_TO_CERT}' -- exists: {cert_exists}")
# print(f"[CONFIG] PATH_TO_KEY: '{PATH_TO_KEY}' -- exists: {key_exists}")
# print(f"[CONFIG] PATH_TO_CA: '{PATH_TO_CA}' -- exists: {ca_exists}")


# authdriver used for headless auth (alerts/reports, thumbnails, etc)
def authDriver(driver: WebDriver, user) -> WebDriver:
    print(f"[CONFIG] ##### auth_driver BEGIN {driver} #####")
    driver.get(headless_url("/doesnotexist"))
    try:
        cookies = MachineAuthProvider.get_auth_cookies(user)
        for cookie_name, cookie_val in cookies.items():
            driver.add_cookie(dict(name=cookie_name, value=cookie_val))
    except Exception as e:
        print(f"[CONFIG] Error: {e}")
    return driver


def buildSqlAlchemyUri():
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
    # if isProd():
    #     # add ssl_cert, ssl_key, ssl_ca cert paths to the sqlalchemy database uri
    #     SQLALCHEMY_DATABASE_URI = "%s?ssl_cert=%s&ssl_key=%s&ssl_ca=%s" % (
    #         SQLALCHEMY_DATABASE_URI,
    #         PATH_TO_CERT,
    #         PATH_TO_KEY,
    #         PATH_TO_CA,
    #     )
    print("[CONFIG] SQLALCHEMY_DATABASE_URI: " + str(SQLALCHEMY_DATABASE_URI))
    return SQLALCHEMY_DATABASE_URI


# TODO: add secret fetching
def loadOktaClientId():
    return "okta.client_id"


def loadOktaClientSecret():
    return "okta.client_secret"
