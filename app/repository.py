from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.db import get_connection
from app.schemas import (
    AnalysisRunRecord,
    AnalysisRunSummary,
    CreateProjectRequest,
    Citation,
    ProjectSummary,
    RunEvent,
    SearchResultBundle,
    SessionRecord,
    StageOutput,
    StageRunRecord,
    SubscriptionRecord,
    UserSummary,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def create_project(payload: CreateProjectRequest, *, owner_email: str) -> str:
    public_id = uuid4().hex[:12]
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO projects (public_id, owner_email, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                public_id,
                owner_email.strip().lower(),
                payload.name.strip(),
                (payload.description or "").strip() or None,
                now,
                now,
            ),
        )
    return public_id


def create_user(email: str, password_hash: str, role: str = "user") -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email.strip().lower(), password_hash, role, now, now),
        )


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT email, password_hash, role, created_at, updated_at
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()
    if row is None:
        return None
    return {
        "email": row["email"],
        "password_hash": row["password_hash"],
        "role": row["role"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_users(limit: int = 50) -> list[UserSummary]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT email, role, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        UserSummary(
            email=row["email"],
            role=row["role"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]


def get_subscription(email: str) -> SubscriptionRecord | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT email, plan_name, status, created_at, updated_at
            FROM subscriptions
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()
    if row is None:
        return None
    return SubscriptionRecord(
        email=row["email"],
        plan_name=row["plan_name"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def upsert_subscription(email: str, plan_name: str, status: str = "active") -> SubscriptionRecord:
    now = utc_now()
    normalized_email = email.strip().lower()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO subscriptions (email, plan_name, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(email)
            DO UPDATE SET
              plan_name = excluded.plan_name,
              status = excluded.status,
              updated_at = excluded.updated_at
            """,
            (normalized_email, plan_name, status, now, now),
        )
    return get_subscription(normalized_email)  # type: ignore[return-value]


def create_session_record(session_id: str, email: str, role: str, expires_at: str) -> SessionRecord:
    now = utc_now()
    normalized_email = email.strip().lower()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sessions (session_id, email, role, expires_at, revoked_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, NULL, ?, ?)
            """,
            (session_id, normalized_email, role, expires_at, now, now),
        )
    return get_session_record(session_id)  # type: ignore[return-value]


def get_session_record(session_id: str) -> SessionRecord | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT session_id, email, role, expires_at, revoked_at, created_at, updated_at
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()
    if row is None:
        return None
    return SessionRecord(
        session_id=row["session_id"],
        email=row["email"],
        role=row["role"],
        expires_at=datetime.fromisoformat(row["expires_at"]),
        revoked_at=_parse_dt(row["revoked_at"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def revoke_session_record(session_id: str) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE sessions
            SET revoked_at = ?, updated_at = ?
            WHERE session_id = ? AND revoked_at IS NULL
            """,
            (now, now, session_id),
        )


def list_sessions_for_email(email: str, limit: int = 20) -> list[SessionRecord]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT session_id, email, role, expires_at, revoked_at, created_at, updated_at
            FROM sessions
            WHERE email = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (email.strip().lower(), limit),
        ).fetchall()
    return [
        SessionRecord(
            session_id=row["session_id"],
            email=row["email"],
            role=row["role"],
            expires_at=datetime.fromisoformat(row["expires_at"]),
            revoked_at=_parse_dt(row["revoked_at"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]


def create_run(
    idea_text: str,
    project_public_id: str | None = None,
    *,
    owner_email: str,
) -> str:
    public_id = uuid4().hex[:12]
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO analysis_runs (
                owner_email, project_public_id, public_id, idea_text, status, current_stage, current_stage_name,
                final_markdown, failure_message, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, 'queued', NULL, NULL, NULL, NULL, ?, ?)
            """,
            (owner_email.strip().lower(), project_public_id, public_id, idea_text.strip(), now, now),
        )
    append_event(public_id, "run_created", {"status": "queued"})
    return public_id


def append_event(run_public_id: str, event_type: str, payload: dict[str, Any]) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO run_events (run_public_id, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (run_public_id, event_type, json.dumps(payload), now),
        )


def mark_run_started(run_public_id: str) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET status = 'running', updated_at = ?
            WHERE public_id = ?
            """,
            (now, run_public_id),
        )


def mark_stage_started(run_public_id: str, stage_index: int, stage_name: str) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET current_stage = ?, current_stage_name = ?, status = 'running', updated_at = ?
            WHERE public_id = ?
            """,
            (stage_index, stage_name, now, run_public_id),
        )
        connection.execute(
            """
            INSERT INTO stage_runs (
                run_public_id, stage_index, stage_name, status, started_at
            )
            VALUES (?, ?, ?, 'running', ?)
            ON CONFLICT(run_public_id, stage_index)
            DO UPDATE SET
                stage_name = excluded.stage_name,
                status = 'running',
                started_at = excluded.started_at
            """,
            (run_public_id, stage_index, stage_name, now),
        )


def save_stage_output(
    run_public_id: str,
    stage_index: int,
    output: StageOutput,
    provider_name: str,
    model_name: str,
) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE stage_runs
            SET status = 'completed',
                provider_name = ?,
                model_name = ?,
                markdown = ?,
                summary = ?,
                handoff_json = ?,
                citations_json = ?,
                raw_text = ?,
                completed_at = ?
            WHERE run_public_id = ? AND stage_index = ?
            """,
            (
                provider_name,
                model_name,
                output.markdown,
                output.summary,
                json.dumps(output.handoff),
                json.dumps([citation.model_dump() for citation in output.citations]),
                output.raw_text,
                now,
                run_public_id,
                stage_index,
            ),
        )
        connection.execute(
            """
            UPDATE analysis_runs
            SET updated_at = ?
            WHERE public_id = ?
            """,
            (now, run_public_id),
        )


def mark_run_completed(run_public_id: str, final_markdown: str) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET status = 'completed',
                final_markdown = ?,
                updated_at = ?
            WHERE public_id = ?
            """,
            (final_markdown, now, run_public_id),
        )


def mark_stage_failed(run_public_id: str, stage_index: int, message: str) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE stage_runs
            SET status = 'failed',
                raw_text = ?,
                completed_at = ?
            WHERE run_public_id = ? AND stage_index = ?
            """,
            (message, now, run_public_id, stage_index),
        )


def mark_run_failed(run_public_id: str, message: str) -> None:
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE analysis_runs
            SET status = 'failed',
                failure_message = ?,
                updated_at = ?
            WHERE public_id = ?
            """,
            (message, now, run_public_id),
        )


def list_events(run_public_id: str) -> list[RunEvent]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT event_type, payload_json, created_at
            FROM run_events
            WHERE run_public_id = ?
            ORDER BY id ASC
            """,
            (run_public_id,),
        ).fetchall()
    return [
        RunEvent(
            event_type=row["event_type"],
            payload=json.loads(row["payload_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]


def get_run(run_public_id: str) -> AnalysisRunRecord | None:
    with get_connection() as connection:
        run_row = connection.execute(
            "SELECT * FROM analysis_runs WHERE public_id = ?",
            (run_public_id,),
        ).fetchone()
        if run_row is None:
            return None
        stage_rows = connection.execute(
            """
            SELECT * FROM stage_runs
            WHERE run_public_id = ?
            ORDER BY stage_index ASC
            """,
            (run_public_id,),
        ).fetchall()
    stages = [
        StageRunRecord(
            stage_index=row["stage_index"],
            stage_name=row["stage_name"],
            status=row["status"],
            provider_name=row["provider_name"],
            model_name=row["model_name"],
            summary=row["summary"],
            markdown=row["markdown"],
            handoff=json.loads(row["handoff_json"]) if row["handoff_json"] else {},
            citations=[Citation(**item) for item in json.loads(row["citations_json"] or "[]")],
            raw_text=row["raw_text"],
            started_at=_parse_dt(row["started_at"]),
            completed_at=_parse_dt(row["completed_at"]),
        )
        for row in stage_rows
    ]
    return AnalysisRunRecord(
        owner_email=run_row["owner_email"],
        project_public_id=run_row["project_public_id"],
        public_id=run_row["public_id"],
        idea_text=run_row["idea_text"],
        status=run_row["status"],
        current_stage=run_row["current_stage"],
        current_stage_name=run_row["current_stage_name"],
        final_markdown=run_row["final_markdown"],
        failure_message=run_row["failure_message"],
        created_at=datetime.fromisoformat(run_row["created_at"]),
        updated_at=datetime.fromisoformat(run_row["updated_at"]),
        stages=stages,
        events=list_events(run_public_id),
    )


def get_public_sitemap_runs() -> list[str]:
    return []


def list_runs(limit: int = 20, *, owner_email: str | None = None) -> list[AnalysisRunSummary]:
    with get_connection() as connection:
        if owner_email is None:
            rows = connection.execute(
                """
                SELECT public_id, idea_text, status, current_stage_name, created_at, updated_at,
                       project_public_id, owner_email
                FROM analysis_runs
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT public_id, idea_text, status, current_stage_name, created_at, updated_at,
                       project_public_id, owner_email
                FROM analysis_runs
                WHERE owner_email = ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (owner_email.strip().lower(), limit),
            ).fetchall()
    return [
        AnalysisRunSummary(
            owner_email=row["owner_email"],
            project_public_id=row["project_public_id"],
            public_id=row["public_id"],
            idea_text=row["idea_text"],
            status=row["status"],
            current_stage_name=row["current_stage_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]


def list_projects(limit: int = 20, *, owner_email: str | None = None) -> list[ProjectSummary]:
    with get_connection() as connection:
        if owner_email is None:
            rows = connection.execute(
                """
                SELECT
                  p.public_id,
                  p.owner_email,
                  p.name,
                  p.description,
                  p.created_at,
                  p.updated_at,
                  COUNT(ar.id) AS run_count
                FROM projects p
                LEFT JOIN analysis_runs ar
                  ON ar.project_public_id = p.public_id
                GROUP BY p.public_id, p.owner_email, p.name, p.description, p.created_at, p.updated_at
                ORDER BY p.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                  p.public_id,
                  p.owner_email,
                  p.name,
                  p.description,
                  p.created_at,
                  p.updated_at,
                  COUNT(ar.id) AS run_count
                FROM projects p
                LEFT JOIN analysis_runs ar
                  ON ar.project_public_id = p.public_id
                WHERE p.owner_email = ?
                GROUP BY p.public_id, p.owner_email, p.name, p.description, p.created_at, p.updated_at
                ORDER BY p.updated_at DESC
                LIMIT ?
                """,
                (owner_email.strip().lower(), limit),
            ).fetchall()
    return [
        ProjectSummary(
            owner_email=row["owner_email"],
            public_id=row["public_id"],
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            run_count=row["run_count"],
        )
        for row in rows
    ]


def get_admin_overview() -> dict[str, Any]:
    with get_connection() as connection:
        run_rows = connection.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM analysis_runs
            GROUP BY status
            """
        ).fetchall()
        provider_rows = connection.execute(
            """
            SELECT provider_name, COUNT(*) AS total
            FROM stage_runs
            WHERE provider_name IS NOT NULL
            GROUP BY provider_name
            ORDER BY total DESC
            """
        ).fetchall()
        failed_rows = connection.execute(
            """
            SELECT public_id, idea_text, failure_message, updated_at
            FROM analysis_runs
            WHERE status = 'failed'
            ORDER BY updated_at DESC
            LIMIT 10
            """
        ).fetchall()

    status_totals = {row["status"]: row["total"] for row in run_rows}
    provider_totals = {row["provider_name"]: row["total"] for row in provider_rows}
    recent_failures = [
        {
            "public_id": row["public_id"],
            "idea_text": row["idea_text"],
            "failure_message": row["failure_message"],
            "updated_at": row["updated_at"],
        }
        for row in failed_rows
    ]

    return {
        "status_totals": status_totals,
        "provider_totals": provider_totals,
        "recent_failures": recent_failures,
        "total_runs": sum(status_totals.values()),
    }


def user_owns_run(run_public_id: str, owner_email: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM analysis_runs
            WHERE public_id = ? AND owner_email = ?
            """,
            (run_public_id, owner_email.strip().lower()),
        ).fetchone()
    return row is not None


def user_owns_project(project_public_id: str, owner_email: str) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM projects
            WHERE public_id = ? AND owner_email = ?
            """,
            (project_public_id, owner_email.strip().lower()),
        ).fetchone()
    return row is not None


def count_runs_for_owner(owner_email: str) -> int:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM analysis_runs
            WHERE owner_email = ?
            """,
            (owner_email.strip().lower(),),
        ).fetchone()
    return int(row["total"]) if row is not None else 0
