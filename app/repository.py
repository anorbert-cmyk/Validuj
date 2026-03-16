from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.db import get_connection
from app.schemas import AnalysisRunRecord, Citation, RunEvent, SearchResultBundle, StageOutput, StageRunRecord


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def create_run(idea_text: str) -> str:
    public_id = uuid4().hex[:12]
    now = utc_now()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO analysis_runs (
                public_id, idea_text, status, current_stage, current_stage_name,
                final_markdown, failure_message, created_at, updated_at
            )
            VALUES (?, ?, 'queued', NULL, NULL, NULL, NULL, ?, ?)
            """,
            (public_id, idea_text.strip(), now, now),
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
