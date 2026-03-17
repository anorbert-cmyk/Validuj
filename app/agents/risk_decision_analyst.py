from app.agents.base import StageSpec


SPEC = StageSpec(
    index=6,
    slug="risk-decision-analyst",
    display_name="Risk & Decision Analyst",
    goal="Summarize critical risks, assumptions, validation experiments, and produce a final recommendation.",
    output_heading="Risk assessment and recommendation",
    preferred_capability="reasoning",
)
