from __future__ import annotations

from app.agents.base import StageSpec
from app.schemas import SearchResultBundle


def build_stage_prompt(
    *,
    stage: StageSpec,
    idea_text: str,
    handoff_summary: str,
    search_bundle: SearchResultBundle | None,
) -> str:
    lines = [
        f"You are the {stage.display_name} in a six-agent business validation workflow.",
        f"Primary goal: {stage.goal}",
        "",
        "Return a professional and specific analysis using markdown.",
        "Use concise sections and bullets where helpful.",
        f"Business idea: {idea_text}",
    ]

    if handoff_summary:
        lines.extend(
            [
                "",
                "Accumulated handoff context from earlier agents:",
                handoff_summary,
            ]
        )

    if search_bundle and search_bundle.results:
        lines.extend(
            [
                "",
                f"Live research query used: {search_bundle.query}",
                "Research evidence:",
            ]
        )
        for result in search_bundle.results[:6]:
            lines.append(f"- {result.title}: {result.snippet or ''} ({result.url})")

    lines.extend(
        [
            "",
            "Required output structure:",
            f"## {stage.output_heading}",
            "### Executive summary",
            "### Key findings",
            "### Recommendations",
            "### Handoff",
        ]
    )
    return "\n".join(lines)
