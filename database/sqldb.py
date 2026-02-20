import sqlite3
from pathlib import Path
from info import SQLDB


def sqldb_enabled() -> bool:
    return bool(SQLDB)


def get_sqldb_path() -> str:
    db_url = SQLDB.strip()
    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    if db_url.startswith("sqlite://"):
        return db_url.replace("sqlite://", "", 1)
    return db_url


def get_conn() -> sqlite3.Connection:
    db_path = get_sqldb_path() or "bot.db"
    path = Path(db_path)
    if path.parent and str(path.parent) != ".":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
