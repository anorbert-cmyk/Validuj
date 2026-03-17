from __future__ import annotations

from urllib.parse import urljoin

from app.config import Settings
from app.schemas import PageMeta


def build_url(settings: Settings, path: str) -> str:
    return urljoin(f"{settings.app_base_url.rstrip('/')}/", path.lstrip("/"))


def make_meta(
    settings: Settings,
    *,
    path: str,
    title: str,
    description: str,
    robots: str = "index,follow",
    og_type: str = "website",
    structured_data: list[dict] | None = None,
) -> PageMeta:
    return PageMeta(
        title=title,
        description=description,
        canonical_url=build_url(settings, path),
        robots=robots,
        og_type=og_type,
        structured_data=structured_data or [],
    )


def homepage_structured_data(settings: Settings) -> list[dict]:
    homepage_url = build_url(settings, "/")
    return [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": settings.app_name,
            "url": homepage_url,
        },
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": settings.app_name,
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "url": homepage_url,
            "description": "Multi-agent business idea validation with research, strategy, product and risk analysis.",
        },
    ]


def methodology_structured_data(settings: Settings) -> list[dict]:
    return [
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": f"{settings.app_name} methodology",
            "url": build_url(settings, "/how-it-works"),
            "description": "How the six-agent handoff workflow validates business ideas.",
        }
    ]


def demo_structured_data(settings: Settings) -> list[dict]:
    return [
        {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": f"{settings.app_name} demo report",
            "url": build_url(settings, "/demo-report"),
            "description": "Public demonstration of the analysis report structure and outputs.",
        }
    ]
