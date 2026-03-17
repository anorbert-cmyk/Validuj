from __future__ import annotations

import asyncio
import re
from typing import Iterable

from app.agents import ALL_STAGES
from app.agents.base import StageSpec
from app.repository import (
    append_event,
    get_run,
    mark_run_completed,
    mark_run_failed,
    mark_run_started,
    mark_stage_failed,
    mark_stage_started,
    save_stage_output,
)
from app.schemas import Citation, SearchResultBundle, StageOutput
from app.services.event_bus import event_bus
from app.services.handoff import compact_handoff
from app.services.input_sanitizer import sanitize_idea_text
from app.services.model_router import ModelRouter
from app.services.prompt_builder import build_stage_prompt
from app.services.search_service import SearchService


class AnalysisRunner:
    def __init__(self, router: ModelRouter, search_service: SearchService) -> None:
        self.router = router
        self.search_service = search_service

    async def run(self, run_id: str) -> None:
        run = get_run(run_id)
        if run is None:
            return

        idea_text = sanitize_idea_text(run.idea_text)
        completed_outputs: list[StageOutput] = []
        mark_run_started(run_id)
        self._publish(run_id, "run_started", {"status": "running"})

        try:
            for stage in ALL_STAGES:
                mark_stage_started(run_id, stage.index, stage.display_name)
                self._publish(
                    run_id,
                    "stage_started",
                    {"stage_index": stage.index, "stage_name": stage.display_name},
                )

                search_bundle = None
                if stage.uses_search:
                    search_bundle = await self.search_service.search(
                        self._build_search_query(stage, idea_text),
                        limit=5,
                    )
                    self._publish(
                        run_id,
                        "stage_progress",
                        {
                            "stage_index": stage.index,
                            "message": f"Research results gathered: {len(search_bundle.results)} sources",
                        },
                    )

                prompt = build_stage_prompt(
                    stage=stage,
                    idea_text=idea_text,
                    handoff_summary=compact_handoff([item.handoff for item in completed_outputs]),
                    search_bundle=search_bundle,
                )
                provider_response = await self.router.generate(
                    prompt=prompt,
                    capability=stage.preferred_capability,
                )
                output = self._stage_output_from_text(
                    stage=stage,
                    text=provider_response.text,
                    citations=search_bundle.results if search_bundle else [],
                )
                save_stage_output(
                    run_public_id=run_id,
                    stage_index=stage.index,
                    output=output,
                    provider_name=provider_response.provider_name,
                    model_name=provider_response.model_name,
                )
                completed_outputs.append(output)
                self._publish(
                    run_id,
                    "stage_completed",
                    {
                        "stage_index": stage.index,
                        "stage_name": stage.display_name,
                        "summary": output.summary,
                        "provider_name": provider_response.provider_name,
                        "model_name": provider_response.model_name,
                    },
                )

            final_markdown = self._compile_report(run.idea_text, completed_outputs)
            mark_run_completed(run_id, final_markdown)
            self._publish(run_id, "run_completed", {"status": "completed"})
        except Exception as exc:
            stage_index = len(completed_outputs) + 1
            mark_stage_failed(run_id, stage_index, str(exc))
            mark_run_failed(run_id, str(exc))
            self._publish(
                run_id,
                "run_failed",
                {"status": "failed", "message": str(exc), "stage_index": stage_index},
            )

    def _publish(self, run_id: str, event_type: str, payload: dict) -> None:
        append_event(run_id, event_type, payload)
        event_bus.publish(run_id, {"event_type": event_type, "payload": payload})

    def _build_search_query(self, stage: StageSpec, idea_text: str) -> str:
        if stage.index == 1:
            return f"{idea_text} market demand trends target users startup"
        return f"{idea_text} competitors alternatives market landscape"

    def _stage_output_from_text(
        self,
        *,
        stage: StageSpec,
        text: str,
        citations: Iterable[Citation],
    ) -> StageOutput:
        normalized = text.strip() or f"## {stage.output_heading}\n\nNo content generated."
        summary = self._extract_summary(normalized)
        key_findings = self._extract_key_findings(normalized)
        markdown = normalized if normalized.startswith("#") else f"## {stage.output_heading}\n\n{normalized}"
        handoff = {
            "stage": stage.display_name,
            "summary": summary,
            "key_findings": key_findings[:5],
            "next_focus": self._extract_recommendation_lines(normalized)[:4],
        }
        return StageOutput(
            stage_name=stage.display_name,
            summary=summary,
            key_findings=key_findings,
            handoff=handoff,
            citations=list(citations),
            markdown=markdown,
            raw_text=text,
        )

    def _extract_summary(self, markdown: str) -> str:
        executive = re.search(
            r"###\s+Executive summary\s*(.+?)(?:\n###|\Z)",
            markdown,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if executive:
            return self._clean_block(executive.group(1))
        paragraphs = [chunk.strip() for chunk in markdown.split("\n\n") if chunk.strip()]
        return self._clean_block(paragraphs[0] if paragraphs else "Analysis completed.")

    def _extract_key_findings(self, markdown: str) -> list[str]:
        findings_block = re.search(
            r"###\s+Key findings\s*(.+?)(?:\n###|\Z)",
            markdown,
            flags=re.IGNORECASE | re.DOTALL,
        )
        source_text = findings_block.group(1) if findings_block else markdown
        findings = []
        for line in source_text.splitlines():
            line = line.strip()
            if line.startswith(("- ", "* ")):
                findings.append(line[2:].strip())
        if findings:
            return findings[:6]
        sentences = re.split(r"(?<=[.!?])\s+", self._clean_block(source_text))
        return [sentence.strip() for sentence in sentences[:4] if sentence.strip()]

    def _extract_recommendation_lines(self, markdown: str) -> list[str]:
        block = re.search(
            r"###\s+Recommendations\s*(.+?)(?:\n###|\Z)",
            markdown,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not block:
            return []
        recommendations = []
        for line in block.group(1).splitlines():
            line = line.strip()
            if line.startswith(("- ", "* ")):
                recommendations.append(line[2:].strip())
        return recommendations

    def _clean_block(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip(" -\n\t")

    def _compile_report(self, idea_text: str, outputs: list[StageOutput]) -> str:
        sections = [
            f"# Validuj analysis report",
            "",
            "## Submitted idea",
            idea_text.strip(),
            "",
            "## Executive overview",
            outputs[-1].summary if outputs else "No output generated.",
            "",
        ]
        for output in outputs:
            sections.extend([output.markdown, ""])
        return "\n".join(sections).strip() + "\n"


def spawn_analysis(run_id: str, runner: AnalysisRunner) -> None:
    asyncio.create_task(runner.run(run_id))
