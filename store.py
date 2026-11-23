"""ذخیره‌سازی داده‌ها در SQLite (شرکت‌ها، سوابق کار، نشست در جریان)."""

import datetime as dt
import os
import sqlite3
import sys


def _base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _base_dir()
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DB_PATH = os.path.join(STORAGE_DIR, "worklog.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cycle_start_day INTEGER NOT NULL DEFAULT 1,
    sort_order INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    company_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    start_ts TEXT NOT NULL,
    end_ts TEXT NOT NULL,
    seconds INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS active_session (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    company_id INTEGER,
    company_name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    started_ts TEXT NOT NULL,
    last_resume_ts TEXT NOT NULL,
    accumulated_seconds INTEGER NOT NULL DEFAULT 0,
    paused INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def _now():
    return dt.datetime.now().replace(microsecond=0)


def _iso(value):
    return value.isoformat(sep=" ")


def _parse(text):
    return dt.datetime.fromisoformat(text)


def _connect():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO companies (name, cycle_start_day, sort_order) VALUES (?, ?, ?)",
                [("پروژه ی A", 28, 0), ("پروژه ی B", 1, 1)],
            )


# ---------------------------------------------------------------- meta

def meta_get(key, default=None):
    with _connect() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def meta_set(key, value):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value)),
        )


# ------------------------------------------------------------ companies

def list_companies():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, name, cycle_start_day FROM companies "
            "ORDER BY sort_order, id"
        ).fetchall()
    return [dict(r) for r in rows]


def company_by_id(company_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, name, cycle_start_day FROM companies WHERE id = ?",
            (company_id,),
        ).fetchone()
    return dict(row) if row else None


def company_name_exists(name, exclude_id=None):
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM companies WHERE name = ? AND id IS NOT ?",
            (name.strip(), exclude_id),
        ).fetchone()
    return row is not None


def save_company(name, cycle_start_day, company_id=None):
    name = name.strip()
    cycle_start_day = max(1, min(31, int(cycle_start_day)))
    with _connect() as conn:
        if company_id:
            conn.execute(
                "UPDATE companies SET name = ?, cycle_start_day = ? WHERE id = ?",
                (name, cycle_start_day, company_id),
            )
        else:
            order = conn.execute("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM companies").fetchone()[0]
            conn.execute(
                "INSERT INTO companies (name, cycle_start_day, sort_order) VALUES (?, ?, ?)",
                (name, cycle_start_day, order),
            )


def delete_company(company_id):
    with _connect() as conn:
        conn.execute("DELETE FROM companies WHERE id = ?", (company_id,))


# ------------------------------------------------------- active session

def active_get():
    with _connect() as conn:
        row = conn.execute("SELECT * FROM active_session WHERE id = 1").fetchone()
    if not row:
        return None
    return {
        "company_id": row["company_id"],
        "company_name": row["company_name"],
        "description": row["description"],
        "started": _parse(row["started_ts"]),
        "last_resume": _parse(row["last_resume_ts"]),
        "accumulated": int(row["accumulated_seconds"]),
        "paused": bool(row["paused"]),
    }


def active_elapsed(session, now=None):
    now = now or _now()
    if session is None:
        return 0
    if session["paused"]:
        return session["accumulated"]
    return session["accumulated"] + max(0, int((now - session["last_resume"]).total_seconds()))


def active_start(company_id, company_name, description):
    now = _now()
    with _connect() as conn:
        conn.execute("DELETE FROM active_session")
        conn.execute(
            "INSERT INTO active_session "
            "(id, company_id, company_name, description, started_ts, last_resume_ts, accumulated_seconds, paused) "
            "VALUES (1, ?, ?, ?, ?, ?, 0, 0)",
            (company_id, company_name, description, _iso(now), _iso(now)),
        )


def active_pause():
    session = active_get()
    if not session or session["paused"]:
        return
    now = _now()
    accumulated = session["accumulated"] + max(0, int((now - session["last_resume"]).total_seconds()))
    with _connect() as conn:
        conn.execute(
            "UPDATE active_session SET accumulated_seconds = ?, last_resume_ts = ?, paused = 1 WHERE id = 1",
            (accumulated, _iso(now)),
        )


def active_resume():
    session = active_get()
    if not session or not session["paused"]:
        return
    with _connect() as conn:
        conn.execute(
            "UPDATE active_session SET last_resume_ts = ?, paused = 0 WHERE id = 1",
            (_iso(_now()),),
        )


def active_stop():
    """پایان کار: ثبت سابقه و حذف نشست. ثانیه‌ها به دقیقه گرد می‌شوند."""
    session = active_get()
    if not session:
        return None
    now = _now()
    seconds = active_elapsed(session, now)
    seconds = int(round(seconds / 60.0)) * 60
    entry = {
        "company_id": session["company_id"],
        "company_name": session["company_name"],
        "description": session["description"],
        "start": session["started"],
        "end": now,
        "seconds": seconds,
    }
    with _connect() as conn:
        conn.execute(
            "INSERT INTO entries (company_id, company_name, description, start_ts, end_ts, seconds, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                entry["company_id"],
                entry["company_name"],
                entry["description"],
                _iso(entry["start"]),
                _iso(entry["end"]),
                entry["seconds"],
                _iso(now),
            ),
        )
        conn.execute("DELETE FROM active_session")
    return entry


def active_discard():
    with _connect() as conn:
        conn.execute("DELETE FROM active_session")


# --------------------------------------------------------------- entries

def entries_list(company_id=None, limit=None):
    query = "SELECT * FROM entries"
    params = []
    if company_id is not None:
        query += " WHERE company_id = ?"
        params.append(company_id)
    query += " ORDER BY start_ts DESC, id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    result = []
    for r in rows:
        item = dict(r)
        item["start"] = _parse(item["start_ts"])
        item["end"] = _parse(item["end_ts"])
        result.append(item)
    return result


def entries_grouped():
    """همه سوابق به تفکیک شرکت (برای خروجی اکسل)، شامل شرکت‌های حذف‌شده."""
    companies = {c["id"]: c for c in list_companies()}
    groups = {}
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM entries ORDER BY start_ts, id").fetchall()
    for r in rows:
        item = dict(r)
        item["start"] = _parse(item["start_ts"])
        item["end"] = _parse(item["end_ts"])
        key = item["company_id"] if item["company_id"] in companies else ("name", item["company_name"])
        company = companies.get(item["company_id"], {})
        group = groups.setdefault(
            key,
            {
                "company_id": item["company_id"],
                "name": company.get("name", item["company_name"]),
                "cycle_start_day": company.get("cycle_start_day", 1),
                "entries": [],
            },
        )
        group["entries"].append(item)
    return list(groups.values())


def entry_delete(entry_id):
    with _connect() as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))


def entry_description(entry_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT description FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()
    return row["description"] if row else ""


def entry_set_description(entry_id, description):
    with _connect() as conn:
        conn.execute(
            "UPDATE entries SET description = ? WHERE id = ?",
            (description, entry_id),
        )


def recent_descriptions(company_id=None, limit=8):
    """شرح‌های قبلی (برای همان شرکت)، تازه‌ترین اول و بدون تکرار."""
    query = "SELECT description FROM entries WHERE TRIM(description) <> ''"
    params = []
    if company_id is not None:
        query += " AND company_id = ?"
        params.append(company_id)
    query += (" GROUP BY description ORDER BY MAX(start_ts) DESC, MAX(id) DESC"
              " LIMIT ?")
    params.append(int(limit))
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [r["description"] for r in rows]


def seconds_for_day(day, company_id=None):
    total = 0
    for e in entries_list(company_id):
        if e["start"].date() == day:
            total += e["seconds"]
        elif e["end"].date() == day and e["start"].date() != day:
            total += e["seconds"]
    return total


init_db()
