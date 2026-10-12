import sqlite3
from pathlib import Path

from flask import g

config_db = Path("raw/config.db").resolve()
insert_config_fp = Path("sqls/insert_config.sql").resolve()


def connect():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config_db)
    return db


def get_config(key):
    c = connect()
    with c:
        row = c.execute(
            "SELECT value FROM config WHERE key = :key",
            {"key": key}
        ).fetchone()
    if row is None:
        return None
    else:
        return row[0]


def set_config(key, value):
    c = connect()
    with c:
        c.execute(
            insert_config_fp.read_text(),
            {"key": key, "value": value}
        )


def unset_config(key):
    c = connect()
    with c:
        c.execute(
            "DELETE FROM config WHERE key = :key",
            {"key": key}
        )
