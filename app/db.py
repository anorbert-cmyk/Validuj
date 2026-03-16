from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import get_settings


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  public_id TEXT NOT NULL UNIQUE,
  owner_email TEXT,
  name TEXT NOT NULL,
  description TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  plan_name TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL,
  role TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_email TEXT,
  project_public_id TEXT,
  public_id TEXT NOT NULL UNIQUE,
  idea_text TEXT NOT NULL,
  status TEXT NOT NULL,
  current_stage INTEGER,
  current_stage_name TEXT,
  final_markdown TEXT,
  failure_message TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stage_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_public_id TEXT NOT NULL,
  stage_index INTEGER NOT NULL,
  stage_name TEXT NOT NULL,
  status TEXT NOT NULL,
  provider_name TEXT,
  model_name TEXT,
  markdown TEXT,
  summary TEXT,
  handoff_json TEXT,
  citations_json TEXT,
  raw_text TEXT,
  started_at TEXT,
  completed_at TEXT,
  UNIQUE(run_public_id, stage_index)
);

CREATE TABLE IF NOT EXISTS run_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_public_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def ensure_database() -> None:
    settings = get_settings()
    database_path = Path(settings.database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.executescript(SCHEMA_SQL)
        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(analysis_runs)").fetchall()
        }
        if "owner_email" not in existing_columns:
            connection.execute("ALTER TABLE analysis_runs ADD COLUMN owner_email TEXT")
        if "project_public_id" not in existing_columns:
            connection.execute("ALTER TABLE analysis_runs ADD COLUMN project_public_id TEXT")
        project_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(projects)").fetchall()
        }
        if "owner_email" not in project_columns:
            connection.execute("ALTER TABLE projects ADD COLUMN owner_email TEXT")
        connection.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    database_path = Path(settings.database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
