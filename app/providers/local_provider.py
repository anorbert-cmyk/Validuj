from __future__ import annotations

import asyncio
import re
from app.config import Settings
from app.schemas import ProviderResponse


def _extract_idea(prompt: str) -> str:
    match = re.search(r"Business idea:\s*(.+)", prompt)
    return match.group(1).strip() if match else "the submitted idea"


def _extract_stage_name(prompt: str) -> str:
    match = re.search(r"You are the (.+?) in a six-agent business validation workflow", prompt)
    return match.group(1).strip() if match else "Specialist"


def _extract_evidence(prompt: str) -> list[str]:
    if "Research evidence:" not in prompt:
        return []
    evidence_block = prompt.split("Research evidence:", 1)[1].split("Required output structure:", 1)[0]
    items = []
    for line in evidence_block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
    return items[:6]


def _extract_handoff_text(prompt: str) -> str:
    if "Accumulated handoff context from earlier agents:" not in prompt:
        return ""
    return prompt.split("Accumulated handoff context from earlier agents:", 1)[1].split("Research evidence:", 1)[0].strip()


def _heuristic_markdown(prompt: str, capability: str) -> str:
    idea = _extract_idea(prompt)
    stage_name = _extract_stage_name(prompt)
    evidence = _extract_evidence(prompt)
    handoff = _extract_handoff_text(prompt)
    evidence_bullets = evidence[:3] or ["No live evidence was available, so this stage relies on domain heuristics and prior handoff."]

    if stage_name == "Market Scout":
        return "\n".join(
            [
                "## Market context and demand",
                "### Executive summary",
                f"{idea} addresses a workflow pain where practitioners lose time to documentation and follow-up coordination. The near-term opportunity is strongest with independent or small-clinic physiotherapists who feel the administrative burden personally and can trial niche software quickly.",
                "",
                "### Key findings",
                f"- Likely buyer: owner-operators and small rehabilitation clinics with limited admin support for {idea}.",
                "- Core pain points are after-hours note completion, reimbursement friction, and inconsistent patient follow-up quality.",
                *[f"- Evidence signal: {item}" for item in evidence_bullets],
                "",
                "### Recommendations",
                "- Focus the first offer on one measurable outcome: faster reimbursement-ready note completion.",
                "- Validate whether physiotherapists trust AI-generated follow-up plans enough to send them without heavy editing.",
                "- Narrow early messaging around burnout reduction plus revenue capture, not broad AI automation promises.",
                "",
                "### Handoff",
                "- Carry forward the buyer profile, documentation pain, and reimbursement angle into the competitor analysis.",
            ]
        )

    if stage_name == "Competitor Analyst":
        return "\n".join(
            [
                "## Competitive landscape",
                "### Executive summary",
                f"The market already contains AI documentation tools for rehab and clinical notes, so {idea} should not compete as a generic scribe. The strongest whitespace is a focused physiotherapy product that combines note generation, reimbursement formatting, and patient follow-up from one workflow.",
                "",
                "### Key findings",
                *[f"- Observable competitor signal: {item}" for item in evidence_bullets],
                "- Many visible alternatives lead with documentation speed, which means differentiation must extend into workflow, claims-readiness, or sport-recovery follow-up.",
                "- Physiotherapy-specific wording and integrations appear to matter more than generic healthcare AI positioning.",
                "",
                "### Recommendations",
                "- Position against manual admin overload, not against every EHR or note-taking platform.",
                "- Differentiate on structured reimbursement output and clinically appropriate follow-up planning.",
                "- Test whether clinics prefer a standalone specialist tool or an add-on inside existing practice software.",
                "",
                "### Handoff",
                "- Preserve competitor patterns: note automation is common, but bundled reimbursement + follow-up may still be under-served.",
            ]
        )

    if stage_name == "Strategy Architect":
        return "\n".join(
            [
                "## Strategy and roadmap",
                "### Executive summary",
                f"The best strategic path for {idea} is a narrow beachhead: independent physiotherapists and boutique clinics with high documentation load and limited administrative support. That segment is specific enough for differentiated messaging and practical enough for fast customer discovery interviews.",
                "",
                "### Key findings",
                "- Phase 1 should validate urgency, documentation time saved, and willingness to pay on a small cohort.",
                "- Phase 2 should deepen retention through template memory, payer-ready formatting, and patient communication history.",
                "- The go-to-market motion should start founder-led: interviews, pilot clinics, and targeted partnerships in physiotherapy communities and clinic software ecosystems.",
                f"- Prior handoff context used: {handoff[:320] or 'initial market and competitor synthesis'}",
                "",
                "### Recommendations",
                "- Ship one hero workflow: convert treatment notes into payer-friendly documentation plus follow-up recommendations.",
                "- Price around admin time recovered and reduced reimbursement friction, not token usage or generic AI value.",
                "- Define milestone metrics: pilot completion, weekly active clinicians, and average edit time per generated note.",
                "",
                "### Handoff",
                "- The product designer should translate the single-workflow strategy into a compact MVP experience with minimal UI complexity.",
            ]
        )

    if stage_name == "Product Designer":
        return "\n".join(
            [
                "## Product and UX concept",
                "### Executive summary",
                f"For {idea}, the MVP experience should feel like a focused clinical workbench: capture notes, review structured output, approve reimbursement-ready documentation, then send a patient follow-up plan. The UX should reward speed and clinician trust.",
                "",
                "### Key findings",
                "- Primary workflow: session note input -> AI draft -> clinician review -> reimbursement-ready export -> patient follow-up approval.",
                "- Information architecture should prioritize session context, generated note, payer formatting status, and patient communication side by side.",
                "- Trust features matter: editable drafts, visible source assumptions, and clear confidence / missing-information flags.",
                "- Small-clinic users will value low setup friction over deep customization in v1.",
                "",
                "### Recommendations",
                "- Keep the initial dashboard minimal: active cases, pending approvals, and recent generated notes.",
                "- Add structured guardrails such as required fields before follow-up plans can be sent.",
                "- Treat reimbursement export and patient plan generation as separate review steps to avoid over-automation anxiety.",
                "",
                "### Handoff",
                "- Preserve the main workflow and trust features so the edge-case review can stress-test failure paths.",
            ]
        )

    if stage_name == "Edge-Case Reviewer":
        return "\n".join(
            [
                "## Edge cases and operational safeguards",
                "### Executive summary",
                f"The main risks for {idea} are not only technical accuracy but workflow over-trust. The product must handle incomplete notes, medically ambiguous language, reimbursement edge cases, and patient-plan hallucination risks without pretending certainty.",
                "",
                "### Key findings",
                "- Incomplete or contradictory treatment notes can lead to unsafe follow-up recommendations.",
                "- Reimbursement formats vary, so unsupported payer logic must degrade gracefully rather than fabricate compliance.",
                "- Clinics need auditability: who edited what, what was AI-generated, and what assumptions were made.",
                "- Patient-facing plans should never imply clinician approval until explicitly reviewed.",
                "",
                "### Recommendations",
                "- Use mandatory review states before export or patient communication.",
                "- Flag missing clinical details instead of guessing across contraindications or recovery assumptions.",
                "- Maintain a visible audit trail for generated sections, edits, and final approvals.",
                "",
                "### Handoff",
                "- Pass forward the key operational risks, especially trust, compliance variance, and review gating.",
            ]
        )

    if stage_name == "Risk & Decision Analyst":
        return "\n".join(
            [
                "## Risk assessment and recommendation",
                "### Executive summary",
                f"{idea} looks promising as a focused niche workflow product, but only if the founder validates a narrow buyer segment and can prove measurable time savings without increasing clinical or reimbursement risk. The current recommendation is a cautious go for validation, not a blind build.",
                "",
                "### Key findings",
                "- Commercial risk: clinicians may like the concept but resist changing documentation habits without clear ROI.",
                "- Product risk: patient follow-up generation raises a higher trust bar than note drafting alone.",
                "- Market risk: several AI documentation tools already exist, so positioning must be sharper than generic automation.",
                "- Execution risk: integrations and payer-specific formatting can expand scope quickly.",
                "",
                "### Recommendations",
                "- Run 10-15 customer interviews with independent physiotherapists and quantify documentation pain in minutes per week.",
                "- Prototype only the note-to-reimbursement workflow before building broad patient communication features.",
                "- Define go/no-go gates: repeated problem urgency, willingness to pilot, and consistent edit-time reduction.",
                "",
                "### Handoff",
                "- Final recommendation: proceed with a narrow validation sprint and delay broader platform ambitions until ROI is proven.",
            ]
        )

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


class LocalProvider:
    provider_name = "local"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, *, prompt: str, capability: str) -> ProviderResponse:
        text = await asyncio.to_thread(_heuristic_markdown, prompt, capability)
        return ProviderResponse(
            provider_name=self.provider_name,
            model_name=self.settings.local_model_id,
            text=text,
        )
