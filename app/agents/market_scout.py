from app.agents.base import StageSpec


SPEC = StageSpec(
    index=1,
    slug="market-scout",
    display_name="Market Scout",
    goal="Frame the problem, identify target audiences, pain points, and realistic market demand signals.",
    output_heading="Market context and demand",
    preferred_capability="research",
    uses_search=True,
)
