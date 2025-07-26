"""
config.py

Loads database connection settings from environment variables.

Required in your .env file:
- DB_USER:     PostgreSQL username
- DB_PASS:     PostgreSQL password

Optional (defaults used if not set):
- DB_NAME:     'supply_chain_sim'
- DB_HOST:     'localhost'
- DB_PORT:     5432
"""

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "supply_chain_sim"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
}
