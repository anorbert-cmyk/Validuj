from app.agents.base import StageSpec


SPEC = StageSpec(
    index=5,
    slug="edge-case-reviewer",
    display_name="Edge-Case Reviewer",
    goal="Stress-test the product and operation with edge cases, failure paths, trust concerns, and operational exceptions.",
    output_heading="Edge cases and operational safeguards",
    preferred_capability="design",
)
