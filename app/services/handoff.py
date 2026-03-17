from __future__ import annotations

from typing import Any


def compact_handoff(previous_handoffs: list[dict[str, Any]], *, max_chars: int = 4000) -> str:
    serialized_chunks: list[str] = []
    total = 0
    for handoff in previous_handoffs:
        if not handoff:
            continue
        chunk = _serialize_handoff(handoff)
        if not chunk:
            continue
        if total + len(chunk) > max_chars:
            break
        serialized_chunks.append(chunk)
        total += len(chunk)
    return "\n\n".join(serialized_chunks)


def _serialize_handoff(handoff: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in handoff.items():
        if isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                lines.extend(f"- {item}" for item in value[:6])
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for nested_key, nested_value in list(value.items())[:6]:
                lines.append(f"- {nested_key}: {nested_value}")
        elif value:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
