# Shared FastAPI dependencies for route handlers.

import threading

from backend.config import DB_PATH
from backend.data.store import init_db

_write_lock = threading.Lock()


def get_conn():
    """Yield a DuckDB connection, guaranteed to close on exit."""
    conn = init_db(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def get_write_conn():
    """Yield a DuckDB connection with a global write lock for thread safety."""
    conn = init_db(DB_PATH)
    _write_lock.acquire()
    try:
        yield conn
    finally:
        conn.close()
        _write_lock.release()
