from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StageSpec:
    index: int
    slug: str
    display_name: str
    goal: str
    output_heading: str
    preferred_capability: str
    uses_search: bool = False
