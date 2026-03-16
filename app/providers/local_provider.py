from __future__ import annotations

import asyncio
import re
from functools import lru_cache

from app.config import Settings
from app.schemas import ProviderResponse


def _extract_idea(prompt: str) -> str:
    match = re.search(r"Business idea:\s*(.+)", prompt)
    return match.group(1).strip() if match else "the submitted idea"


def _heuristic_markdown(prompt: str, capability: str) -> str:
    idea = _extract_idea(prompt)
    capability_label = {
        "research": "market evidence and demand signals",
        "design": "product and experience direction",
        "reasoning": "strategic and risk reasoning",
    }.get(capability, "analysis")
    return "\n".join(
        [
            "## Expert analysis",
            "### Executive summary",
            f"{idea} shows enough signal to justify a focused validation sprint, especially around {capability_label}.",
            "",
            "### Key findings",
            f"- The problem statement suggests a clear customer pain worth testing for {idea}.",
            "- The team should validate urgency, willingness to pay, and distribution feasibility early.",
            "- A differentiated offer will likely depend on sharper positioning than generic automation claims.",
            "",
            "### Recommendations",
            "- Interview a narrow early-adopter segment before broad product scope expansion.",
            "- Prototype one high-value workflow and measure completion, retention, and objection patterns.",
            "- Convert assumptions into explicit experiments with success thresholds.",
            "",
            "### Handoff",
            "- Preserve customer pains, likely buyer profile, and open questions for the next expert.",
        ]
    )


@lru_cache(maxsize=1)
def _load_pipeline(model_id: str):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    return pipeline("text2text-generation", model=model, tokenizer=tokenizer)


class LocalProvider:
    provider_name = "local"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, *, prompt: str, capability: str) -> ProviderResponse:
        try:
            text = await asyncio.to_thread(self._generate_with_model, prompt)
            model_name = self.settings.local_model_id
        except Exception:
            text = _heuristic_markdown(prompt, capability)
            model_name = "heuristic-fallback"
        return ProviderResponse(provider_name=self.provider_name, model_name=model_name, text=text)

    def _generate_with_model(self, prompt: str) -> str:
        generator = _load_pipeline(self.settings.local_model_id)
        shortened_prompt = (
            "Create a concise but specific startup analysis in markdown with sections for "
            "Executive summary, Key findings, Recommendations, and Handoff.\n\n"
            f"{prompt[:2800]}"
        )
        response = generator(
            shortened_prompt,
            max_new_tokens=320,
            do_sample=False,
            truncation=True,
        )
        if not response:
            return _heuristic_markdown(prompt, "reasoning")
        return response[0]["generated_text"].strip() or _heuristic_markdown(prompt, "reasoning")
