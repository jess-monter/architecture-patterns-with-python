from typing import Dict

import os


def get_postgres_uri() -> str:
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5433")
    password = os.environ.get("DB_PASSWORD", "postgres")
    user, db_name = "postgres", "made_db"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url() -> str:
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = os.environ.get("API_PORT", 5000)
    return f"http://{host}:{port}"


def get_redis_host_and_port() -> Dict[str, str]:
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 6379
    return {"host": host, "port": str(port)}
