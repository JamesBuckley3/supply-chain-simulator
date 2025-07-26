"""
database.py

This module provides a helper function to establish a connection to
the PostgreSQL database using configuration values defined in `config.py`.

Typical usage example:
    from database import get_connection

    conn = get_connection()
    cur = conn.cursor()
"""

import psycopg2
from config import DB_CONFIG


def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.

    Uses the connection parameters defined in the DB_CONFIG dictionary from `config.py`.

    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database.

    Raises:
        psycopg2.OperationalError: If the connection fails due to invalid credentials,
                                   unreachable host, or other DB-related errors.
    """
    return psycopg2.connect(**DB_CONFIG)
