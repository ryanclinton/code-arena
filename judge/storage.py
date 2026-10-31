"""Persistent user progress: saved code, custom test cases and submission history.

Everything lives in a single SQLite file (data/codearena.db by default, override
with the CODEARENA_DB environment variable). Back it up by copying the file.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.environ.get("CODEARENA_DB", ROOT / "data" / "codearena.db"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS code (
    problem_id TEXT NOT NULL,
    language   TEXT NOT NULL,
    code       TEXT NOT NULL,
    updated_at REAL NOT NULL,
    PRIMARY KEY (problem_id, language)
);
CREATE TABLE IF NOT EXISTS cases (
    problem_id TEXT PRIMARY KEY,
    cases_json TEXT NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS submissions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id TEXT NOT NULL,
    language   TEXT NOT NULL,
    code       TEXT NOT NULL,
    verdict    TEXT NOT NULL,
    runtime_ms REAL,
    memory_kb  INTEGER,
    passed     INTEGER,
    total      INTEGER,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS submissions_problem ON submissions (problem_id, created_at DESC);
"""

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def _db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript(_SCHEMA)
    return _conn


def _write(sql: str, params=()) -> sqlite3.Cursor:
    with _lock:
        db = _db()
        cur = db.execute(sql, params)
        db.commit()
        return cur


def _read(sql: str, params=()) -> list[sqlite3.Row]:
    with _lock:
        return _db().execute(sql, params).fetchall()


# ---- code ---------------------------------------------------------------
def save_code(problem_id: str, language: str, code: str | None) -> None:
    """Save the editor contents; None deletes it (back to starter code)."""
    if code is None:
        _write("DELETE FROM code WHERE problem_id = ? AND language = ?", (problem_id, language))
    else:
        _write("INSERT INTO code VALUES (?, ?, ?, ?) ON CONFLICT (problem_id, language) "
               "DO UPDATE SET code = excluded.code, updated_at = excluded.updated_at",
               (problem_id, language, code, time.time()))


# ---- custom test cases --------------------------------------------------
def save_cases(problem_id: str, cases: list | None) -> None:
    if cases is None:
        _write("DELETE FROM cases WHERE problem_id = ?", (problem_id,))
    else:
        _write("INSERT INTO cases VALUES (?, ?, ?) ON CONFLICT (problem_id) "
               "DO UPDATE SET cases_json = excluded.cases_json, updated_at = excluded.updated_at",
               (problem_id, json.dumps(cases), time.time()))


# ---- submissions --------------------------------------------------------
def add_submission(problem_id: str, language: str, code: str, result: dict, created_at: float | None = None) -> int:
    cur = _write(
        "INSERT INTO submissions (problem_id, language, code, verdict, runtime_ms, memory_kb, passed, total, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (problem_id, language, code, result["verdict"], result.get("runtime_ms"), result.get("memory_kb"),
         result.get("passed"), result.get("total"), created_at or time.time()))
    return cur.lastrowid


def _submission_dict(r: sqlite3.Row) -> dict:
    return {"id": r["id"], "lang": r["language"], "code": r["code"], "verdict": r["verdict"],
            "runtime_ms": r["runtime_ms"], "memory_kb": r["memory_kb"], "passed": r["passed"],
            "total": r["total"], "ts": int(r["created_at"] * 1000)}


# ---- aggregate views ----------------------------------------------------
def workspace(problem_id: str) -> dict:
    """Everything the problem page needs to restore where you left off."""
    code = {r["language"]: r["code"] for r in _read("SELECT language, code FROM code WHERE problem_id = ?", (problem_id,))}
    rows = _read("SELECT cases_json FROM cases WHERE problem_id = ?", (problem_id,))
    subs = _read("SELECT * FROM submissions WHERE problem_id = ? ORDER BY created_at DESC LIMIT 100", (problem_id,))
    return {
        "code": code,
        "cases": json.loads(rows[0]["cases_json"]) if rows else None,
        "submissions": [_submission_dict(r) for r in subs],
    }


def progress() -> dict[str, str]:
    """problem_id -> 'solved' | 'attempted' (attempted = submitted but never accepted)."""
    rows = _read("SELECT problem_id, MAX(verdict = 'Accepted') AS solved FROM submissions GROUP BY problem_id")
    return {r["problem_id"]: "solved" if r["solved"] else "attempted" for r in rows}


def import_browser_data(data: dict) -> dict:
    """One-time import of progress that older versions kept in browser localStorage.
    Never overwrites anything already saved on the server."""
    counts = {"code": 0, "cases": 0, "submissions": 0}
    for item in data.get("code", []):
        if not _read("SELECT 1 FROM code WHERE problem_id = ? AND language = ?", (item["problem_id"], item["language"])):
            save_code(item["problem_id"], item["language"], item["code"])
            counts["code"] += 1
    for item in data.get("cases", []):
        if not _read("SELECT 1 FROM cases WHERE problem_id = ?", (item["problem_id"],)):
            save_cases(item["problem_id"], item["cases"])
            counts["cases"] += 1
    for s in data.get("submissions", []):
        created = s["ts"] / 1000
        if not _read("SELECT 1 FROM submissions WHERE problem_id = ? AND created_at = ?", (s["problem_id"], created)):
            add_submission(s["problem_id"], s["lang"], s.get("code", ""), s, created_at=created)
            counts["submissions"] += 1
    return counts
