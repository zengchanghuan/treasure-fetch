"""
SEO 路由：作品详情页、sitemap.xml、robots.txt。

- GET /artwork/{artwork_id}  → 服务端渲染的作品详情页（搜索引擎可索引）
- GET /sitemap.xml           → 动态生成 sitemap
- GET /robots.txt            → 爬虫规则
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response
from jinja2 import Environment, FileSystemLoader

from backend.tile_service import fetch_metadata

router = APIRouter(tags=["seo"])

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_SEED_FILE = Path(__file__).parent / "seed_artworks.json"
_jinja = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True)


def _load_seed_ids() -> list[dict]:
    if _SEED_FILE.exists():
        return json.loads(_SEED_FILE.read_text(encoding="utf-8"))
    return []


@router.get("/artwork/{artwork_id}", response_class=HTMLResponse)
async def artwork_detail(artwork_id: str, request: Request):
    """
    服务端渲染作品详情页。

    包含 JSON-LD 结构化数据和 Open Graph / Twitter Card meta，
    对搜索引擎和社交平台分享友好。响应带 24h 缓存。
    """
    try:
        meta = await fetch_metadata("SUHA", artwork_id)
    except Exception:
        return HTMLResponse("<h1>作品未找到</h1><p><a href='/'>返回首页</a></p>", status_code=404)

    canonical = str(request.url_for("artwork_detail", artwork_id=artwork_id))
    tmpl = _jinja.get_template("artwork.html")
    html = tmpl.render(meta=meta, canonical_url=canonical)
    return HTMLResponse(html, headers={"Cache-Control": "public, max-age=86400"})


@router.get("/sitemap.xml", response_class=Response)
async def sitemap(request: Request):
    """动态生成 sitemap。初期基于 seed_artworks.json，后续可接 API 抓取。"""
    base = str(request.base_url).rstrip("/")
    entries = [f"  <url><loc>{base}/</loc><priority>1.0</priority></url>"]

    for item in _load_seed_ids():
        aid = item.get("id", "")
        if aid:
            entries.append(
                f"  <url><loc>{base}/artwork/{aid}</loc>"
                f"<changefreq>monthly</changefreq><priority>0.8</priority></url>"
            )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/robots.txt", response_class=Response)
async def robots(request: Request):
    base = str(request.base_url).rstrip("/")
    txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /artwork/\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
    return Response(content=txt, media_type="text/plain")
