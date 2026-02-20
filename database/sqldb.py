import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from info import SQLDB, TURSO_AUTH_TOKEN


def sqldb_enabled() -> bool:
    return bool(SQLDB)


def _is_remote_libsql(db_url: str) -> bool:
    return db_url.startswith("libsql://") or db_url.startswith("ws://") or db_url.startswith("wss://")


def _validate_remote_libsql(db_url: str) -> None:
    if not _is_remote_libsql(db_url):
        return

    # We currently use sqlite engine for SQL mode in this codebase.
    # A raw libsql:// URL is not a local sqlite file and would fail with unclear sqlite errors,
    # so we fail early with a precise actionable message.
    if not TURSO_AUTH_TOKEN:
        raise RuntimeError(
            "Turso URL detected in SQLDB/TURSO_DATABASE_URL but TURSO_AUTH_TOKEN is missing. "
            "Add TURSO_AUTH_TOKEN in your environment variables."
        )

    raise RuntimeError(
        "Remote Turso URL detected (libsql://...). This bot's SQL backend currently expects a sqlite file path. "
        "Use a sqlite path like 'sqlite:///data/bot.db' for now, or extend database/sqldb.py to use libsql-client."
    )


def get_sqldb_path() -> str:
    db_url = SQLDB.strip()
    if not db_url:
        return ""

    _validate_remote_libsql(db_url)

    if db_url.startswith("sqlite:///"):
        return db_url.replace("sqlite:///", "", 1)
    if db_url.startswith("sqlite://"):
        return db_url.replace("sqlite://", "", 1)

    parsed = urlparse(db_url)
    if parsed.scheme and parsed.scheme != "file":
        raise RuntimeError(
            f"Unsupported SQLDB scheme '{parsed.scheme}'. Use sqlite file path (e.g. sqlite:///data/bot.db)."
        )

    return db_url


def get_conn() -> sqlite3.Connection:
    db_path = get_sqldb_path() or "bot.db"
    path = Path(db_path)
    if path.parent and str(path.parent) != ".":
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
