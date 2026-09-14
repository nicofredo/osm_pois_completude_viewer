"""
config.py

Central place for environment variables, constants, and static URLs used
across the create / update / export modules. Nothing here has side effects
beyond reading the environment, so it's safe to import from anywhere.
"""

import os
import sys
from dotenv import load_dotenv

ENV = os.getenv("APP_ENV", "dev")
env_file = f".env.{ENV}"

if not os.path.exists(env_file):
    sys.exit(f"Env file not found : {env_file}")

load_dotenv(env_file)

REQUIRED_ENV_VARS = [
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_SCHEMA_LIMITES_ADMIN",
    "POSTGRES_SCHEMA_LIMITES_ADMIN_OSM",
    "POSTGRES_SCHEMA_POIS",
    "POSTGRES_SCHEMA_STATS",
    "POSTGRES_TAGINFO_TABLE",
    "PBF_PATH",
    "DATA_DIR",
    "CHANGE_FILE_SUBFOLDER",
    "OAUTH_COOKIE_CLIENT_PY_PATH",
    "COOKIE_FILENAME",
    "OSM_USERNAME",
    "OSM_PASSWORD",
    "CONSUMER_URL",
    "STORAGE_PROFILE_NAME",
    "STORAGE_ENDPOINT_URL",
    "STORAGE_BUCKET",
]

def validate_env_vars(required_vars):
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        sys.exit(f"Missing variables in {env_file} : {', '.join(missing)}")
    print(f"[OK] No missing variable ({env_file})")

validate_env_vars(REQUIRED_ENV_VARS)

# -----------------------------------------------------------------
# STATIC URLS
# -----------------------------------------------------------------

URL_REGIONS_INSEE_GEOJSON = 'https://www.data.gouv.fr/api/1/datasets/r/32d59ed1-542d-437a-b3f6-5004de23c660'
URL_DEPARTEMENTS_INSEE_GEOJSON = 'https://www.data.gouv.fr/api/1/datasets/r/e7f3fae7-9296-449d-bd7c-899fc55afcf1'
URL_EPCI_INSEE_GEOJSON = 'https://www.data.gouv.fr/api/1/datasets/r/15ee4938-82e9-4276-85bb-6a1d3d769961'
URL_COMMUNES_INSEE_GEOJSON = 'https://www.data.gouv.fr/api/1/datasets/r/7daa12dc-6fa4-44f6-9ccc-7bf2f6e2a594'

# -----------------------------------------------------------------
# POSTGRES / POSTGIS
# -----------------------------------------------------------------

POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

POSTGRES_SCHEMA_LIMITES_ADMIN = os.getenv('POSTGRES_SCHEMA_LIMITES_ADMIN')
POSTGRES_SCHEMA_LIMITES_ADMIN_OSM = os.getenv('POSTGRES_SCHEMA_LIMITES_ADMIN_OSM')
POSTGRES_SCHEMA_POIS = os.getenv('POSTGRES_SCHEMA_POIS')
POSTGRES_SCHEMA_STATS = os.getenv('POSTGRES_SCHEMA_STATS')

POSTGRES_TAGINFO_TABLE = os.getenv('POSTGRES_TAGINFO_TABLE')

# -----------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------

PBF_PATH = os.getenv('PBF_PATH')
DATA_DIR = os.getenv('DATA_DIR')
CHANGE_FILE_SUBFOLDER = os.path.join(DATA_DIR, os.getenv('CHANGE_FILE_SUBFOLDER'))

BOUNDARIES_LUA_FLEX = os.getenv('BOUNDARIES_LUA_FLEX')
POIS_LUA_FLEX = os.getenv('POIS_LUA_FLEX')

# -----------------------------------------------------------------
# GEOFABRIK / OSM REPLICATION AUTH
# -----------------------------------------------------------------

OAUTH_COOKIE_CLIENT_PY_PATH = os.getenv('OAUTH_COOKIE_CLIENT_PY_PATH')
COOKIE_FILENAME = os.getenv('COOKIE_FILENAME')
OSM_USERNAME = os.getenv('OSM_USERNAME')
OSM_PASSWORD = os.getenv('OSM_PASSWORD')
CONSUMER_URL = os.getenv('CONSUMER_URL')

# -----------------------------------------------------------------
# CLOUD STORAGE
# -----------------------------------------------------------------

STORAGE_PROFILE_NAME = os.getenv('STORAGE_PROFILE_NAME')
STORAGE_ENDPOINT_URL = os.getenv('STORAGE_ENDPOINT_URL')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')


def pg_connection_kwargs() -> dict:
    """Keyword args for psycopg.connect(), built from the settings above."""
    return dict(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
