import sqlite3
from pathlib import Path

from flask import g

config_db = Path("raw/config.db").resolve()
insert_config_table_fp = Path("sqls/insert_config_table.sql").resolve()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config_db)
    return db


def get_config(key):
    db = get_db()
    with db:
        row = db.execute(
            "SELECT value FROM config WHERE key = :key",
            {"key": key}
        ).fetchone()
    if row is None:
        return None
    else:
        return row[0]


def set_config(key, value):
    db = get_db()
    with db:
        db.execute(
            insert_config_table_fp.read_text(),
            {"key": key, "value": value}
        )


def unset_config(key):
    db = get_db()
    with db:
        db.execute(
            "DELETE FROM config WHERE key = :key",
            {"key": key}
        )
