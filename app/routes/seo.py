from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response

from app.seo import build_url


router = APIRouter()


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots(request: Request):
    settings = request.app.state.settings
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /runs/",
            f"Sitemap: {build_url(settings, '/sitemap.xml')}",
            "",
        ]
    )


@router.get("/sitemap.xml")
async def sitemap(request: Request):
    settings = request.app.state.settings
    urls = [
        build_url(settings, "/"),
        build_url(settings, "/how-it-works"),
        build_url(settings, "/demo-report"),
    ]
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"  <url><loc>{url}</loc></url>" for url in urls)
        + "\n</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")
