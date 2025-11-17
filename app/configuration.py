from os import environ, path
from dotenv import load_dotenv

# Load .env file from parent directory
env_path = path.join(path.dirname(path.dirname(__file__)), '.env')
load_dotenv(env_path)

ROOT = path.dirname(path.abspath(__file__))
ENVIRONMENT = environ.get("ENVIRONMENT", "dev")
ENV_NAME = environ.get("ENVNAME", "dev1")
APPLICATION_NAME = f"sql-agent {ENV_NAME}"

DB_CONFIG = {
    "user": environ.get("POSTGRES_USER", "avivekanandan"),
    "password": environ.get("POSTGRES_PASSWORD", "HotForex!"),
    "host": environ.get("POSTGRES_HOST", "localhost"),
    "database": environ.get("POSTGRES_DATABASE", "hfm_assistant"),
}

GOOGLE_API_KEY = environ.get("GOOGLE_API_KEY")
PGVECTOR_CONNECTION = environ.get("PGVECTOR_CONNECTION", 
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

def is_production() -> bool:
    return ENVIRONMENT in ["live", "prod"]

def is_staging() -> bool:
    return ENVIRONMENT == "staging"

config = {}
