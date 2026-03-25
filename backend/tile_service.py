"""
高清书画瓦片图下载核心服务。

支持三种布局类型：
  PIC  — 单图（hdp.src = "PIC"）
  COLL — 横批/长卷多图拼接（hdp.src = "COLL"）
  PAGE — 多页独立图（hdp.src = "COLL", layoutMode = "PAGE"）

职责链：URL 解析 → 元数据获取 → CDN 签名 → 图块并发下载 → 拼接输出。
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
import time
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
from typing import Callable

import httpx
from PIL import Image

# ── 常量 ────────────────────────────────────────────────────
CDN_HOST = "https://cag-ac.ltfc.net"
API_HOST = "https://api.quanku.art"
_SECRET_KEY = "ltfcdotnet"
_TILE_SIZE = 512
_APP_KEY = "CAGWEB"
_APP_SEC = "ZETYK0B8KTQB41KYWA2"
_URL_RE = re.compile(
    r"g2\.ltfc\.net/view/(?P<type>[A-Za-z]+)/(?P<id>[a-f0-9]{24})"
)

# ── 游客令牌缓存 ─────────────────────────────────────────────
_tour_token: str = ""
_tour_token_expire: float = 0


async def _get_tour_token(client: httpx.AsyncClient) -> str:
    """获取或复用游客令牌。"""
    global _tour_token, _tour_token_expire
    if _tour_token and time.time() < _tour_token_expire:
        return _tour_token
    resp = await client.post(
        f"{API_HOST}/cag2.TouristService/getAccessToken",
        json={},
        headers={"Referer": "https://g2.ltfc.net/", "Origin": "https://g2.ltfc.net"},
    )
    resp.raise_for_status()
    data = resp.json()
    _tour_token = data.get("token", "")
    _tour_token_expire = time.time() + int(data.get("expireAfter", 3600)) - 60
    return _tour_token


def _build_context(token: str) -> dict:
    return {"tourToken": token, "appKey": _APP_KEY, "appSec": _APP_SEC}


# ── 数据模型 ──────────────────────────────────────────────────
@dataclass
class PieceMeta:
    """COLL 类型中单个分片的信息。"""
    resource_id: str
    tiles_dir: str
    tiles_source: str
    width: int        # 原始像素宽
    height: int       # 原始像素高
    min_level: int
    max_level: int
    canvas_x: int     # 在最终画布上的 x 偏移（原始像素）
    canvas_y: int     # 在最终画布上的 y 偏移（原始像素）


@dataclass
class ArtworkMeta:
    id: str
    layout_type: str          # "PIC" | "COLL" | "PAGE"
    name: str
    author: str
    age: str
    age_detail: str
    desc: str
    owner: str
    size_cm: str
    width: int                # 展示用宽（PIC/COLL=画布，PAGE=最大页宽）
    height: int               # 展示用高
    min_level: int
    max_level: int
    thumb_url: str
    tags: list[str] = field(default_factory=list)
    # PIC 专用
    resource_id: str = ""
    tiles_dir: str = "cagstore"
    tiles_source: str = "TILES_SOURCE_ALIYUN"
    # COLL / PAGE 专用（PAGE 中 canvas_x/y 无意义但复用同结构）
    pieces: list[PieceMeta] = field(default_factory=list)

    @property
    def available_levels(self) -> list[dict]:
        levels = []
        for lvl in range(self.min_level, self.max_level + 1):
            scale = 2 ** (self.max_level - lvl)
            w = math.ceil(self.width / scale)
            h = math.ceil(self.height / scale)
            if self.layout_type in ("COLL", "PAGE"):
                total_tiles = sum(
                    math.ceil(math.ceil(p.width / (2 ** (p.max_level - lvl))) / _TILE_SIZE) *
                    math.ceil(math.ceil(p.height / (2 ** (p.max_level - lvl))) / _TILE_SIZE)
                    for p in self.pieces
                    if lvl >= p.min_level
                )
            else:
                total_tiles = (
                    math.ceil(w / _TILE_SIZE) * math.ceil(h / _TILE_SIZE)
                )
            suffix = f"  ×{len(self.pieces)}页" if self.layout_type == "PAGE" else ""
            levels.append({
                "level": lvl,
                "width": w,
                "height": h,
                "tiles": total_tiles,
                "label": f"Level {lvl} ({w}×{h}){suffix}",
            })
        return levels


# ── URL 解析 ──────────────────────────────────────────────────
def parse_url(url: str) -> tuple[str, str]:
    """从 URL 提取 (src, id)。格式: g2.ltfc.net/view/SUHA/24位hex"""
    m = _URL_RE.search(url)
    if not m:
        raise ValueError(f"无法识别的 URL: {url}")
    return m.group("type").upper(), m.group("id")


# ── CDN 签名 ─────────────────────────────────────────────────
def _sign(path: str) -> str:
    ts = int(time.time())
    digest = hashlib.md5(f"{path}-{ts}-0-0-{_SECRET_KEY}".encode()).hexdigest()
    return f"{CDN_HOST}{path}?auth_key={ts}-0-0-{digest}"


def tile_url(tiles_dir: str, resource_id: str, level: int, col: int, row: int) -> str:
    path = f"/{tiles_dir}/{resource_id}/{level}/{col}_{row}.jpg"
    return _sign(path)


# ── 元数据获取 ─────────────────────────────────────────────────
async def fetch_metadata(artwork_type: str, artwork_id: str) -> ArtworkMeta:
    async with httpx.AsyncClient(timeout=15) as client:
        token = await _get_tour_token(client)
        resp = await client.post(
            f"{API_HOST}/cag2.ResourceService/getResource",
            json={
                "id": artwork_id,
                "src": artwork_type.upper(),
                "context": _build_context(token),
            },
            headers={"Referer": "https://g2.ltfc.net/", "Origin": "https://g2.ltfc.net"},
        )
        if resp.status_code >= 400:
            raise ValueError(f"上游 API 错误 {resp.status_code}，响应体: {resp.text[:500]}")
        resp.raise_for_status()
        body = resp.json()
        if "data" not in body:
            raise ValueError(body.get("message", "API 返回无数据"))
        data = body["data"]

    # 按类型取主数据对象，兜底遍历所有已知 key
    artwork_key = artwork_type.lower()
    suha = (
        data.get(artwork_key)
        or data.get("suha") or data.get("sufa") or data.get("shiy")
        or data.get("photo") or data.get("wenwu") or {}
    )
    hdp = suha.get("hdp", {})
    hdp_src = hdp.get("src", "PIC")

    common = dict(
        id=artwork_id,
        name=suha.get("name", "未知"),
        author=suha.get("author", "未知"),
        age=suha.get("age", ""),
        age_detail=suha.get("ageDetail", ""),
        desc=suha.get("desc", ""),
        owner=suha.get("owner", ""),
        size_cm=suha.get("size", ""),
        thumb_url=suha.get("thumbTileUrl", ""),
        tags=suha.get("tags", []),
    )

    if hdp_src == "COLL":
        return _parse_coll(hdp, common)
    else:
        return _parse_pic(hdp, common)


def _parse_pic(hdp: dict, common: dict) -> ArtworkMeta:
    hdpic = hdp.get("hdpic", {})
    size = hdpic.get("size", {})
    return ArtworkMeta(
        **common,
        layout_type="PIC",
        width=size.get("width", 0),
        height=size.get("height", 0),
        min_level=hdpic.get("minlevel", 12),
        max_level=hdpic.get("maxlevel", 18),
        resource_id=hdpic.get("resourceId", ""),
        tiles_dir=hdpic.get("tilesDir", "cagstore"),
        tiles_source=hdpic.get("tilesSource", "TILES_SOURCE_ALIYUN"),
    )


def _parse_coll(hdp: dict, common: dict) -> ArtworkMeta:
    coll = hdp.get("hdpcoll", {})
    layout_mode = coll.get("layoutMode", "TILE")   # "TILE" | "PAGE"
    tile_layout = coll.get("tileLayout", {}).get("tiles", [])
    hdps = coll.get("hdps", [])

    all_min = [h.get("minlevel", 12) for h in hdps]
    all_max = [h.get("maxlevel", 18) for h in hdps]
    # TILE：取公共 level（最大交集）；PAGE：取最宽范围
    min_level = max(all_min) if all_min else 12
    max_level = min(all_max) if all_max else 18

    if layout_mode == "PAGE":
        # 各页独立，不拼合；展示最大页的尺寸
        pieces = []
        for h in hdps:
            sz = h.get("size", {})
            pieces.append(PieceMeta(
                resource_id=h.get("resourceId", ""),
                tiles_dir=h.get("tilesDir", "cagstore"),
                tiles_source=h.get("tilesSource", "TILES_SOURCE_ALIYUN"),
                width=sz.get("width", 0),
                height=sz.get("height", 0),
                min_level=h.get("minlevel", 12),
                max_level=h.get("maxlevel", 18),
                canvas_x=0,
                canvas_y=0,
            ))
        # PAGE 整体级别范围取各页的并集（_stitch_page 会对每页 clamp 到自己的 max_level）
        page_min = min(p.min_level for p in pieces) if pieces else 12
        page_max = max(p.max_level for p in pieces) if pieces else 18
        # 展示用尺寸取最大页
        largest = max(pieces, key=lambda p: p.width * p.height, default=None)
        return ArtworkMeta(
            **common,
            layout_type="PAGE",
            width=largest.width if largest else 0,
            height=largest.height if largest else 0,
            min_level=page_min,
            max_level=page_max,
            pieces=pieces,
        )

    # TILE：水平/垂直拼合
    total_w = max((t["x"] + t["width"] for t in tile_layout), default=0)
    total_h = max((t["y"] + t["height"] for t in tile_layout), default=0)

    pieces = []
    for i, h in enumerate(hdps):
        pos = tile_layout[i] if i < len(tile_layout) else {"x": 0, "y": 0}
        sz = h.get("size", {})
        pieces.append(PieceMeta(
            resource_id=h.get("resourceId", ""),
            tiles_dir=h.get("tilesDir", "cagstore"),
            tiles_source=h.get("tilesSource", "TILES_SOURCE_ALIYUN"),
            width=sz.get("width", pos.get("width", 0)),
            height=sz.get("height", pos.get("height", 0)),
            min_level=h.get("minlevel", min_level),
            max_level=h.get("maxlevel", max_level),
            canvas_x=pos.get("x", 0),
            canvas_y=pos.get("y", 0),
        ))

    return ArtworkMeta(
        **common,
        layout_type="COLL",
        width=total_w,
        height=total_h,
        min_level=min_level,
        max_level=max_level,
        pieces=pieces,
    )


# ── 图块下载与拼接 ────────────────────────────────────────────
@dataclass
class DownloadProgress:
    total: int = 0
    done: int = 0
    status: str = "idle"
    message: str = ""


async def _download_tile(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> bytes:
    """返回 bytes；404 或网络错误返回 b'' 而不抛异常，避免单块失败中止整体下载。"""
    async with semaphore:
        try:
            resp = await client.get(url, headers={"Referer": "https://g2.ltfc.net/"})
            if resp.status_code == 404:
                return b""
            resp.raise_for_status()
            return resp.content
        except httpx.HTTPStatusError:
            return b""


async def download_and_stitch(
    meta: ArtworkMeta,
    level: int,
    progress: DownloadProgress,
    on_progress: Callable[[], None] | None = None,
) -> BytesIO:
    if meta.layout_type == "COLL":
        return await _stitch_coll(meta, level, progress, on_progress)
    if meta.layout_type == "PAGE":
        return await _stitch_page(meta, level, progress, on_progress)
    return await _stitch_pic(meta, level, progress, on_progress)


# ── PIC 拼接 ─────────────────────────────────────────────────
async def _stitch_pic(
    meta: ArtworkMeta,
    level: int,
    progress: DownloadProgress,
    on_progress: Callable[[], None] | None,
) -> BytesIO:
    scale = 2 ** (meta.max_level - level)
    img_w = math.ceil(meta.width / scale)
    img_h = math.ceil(meta.height / scale)
    cols = math.ceil(img_w / _TILE_SIZE)
    rows = math.ceil(img_h / _TILE_SIZE)

    progress.total = cols * rows
    progress.done = 0
    progress.status = "downloading"
    progress.message = f"正在下载 {progress.total} 个图块..."

    tile_data: dict[tuple[int, int], bytes] = {}
    sem = asyncio.Semaphore(12)

    async def _fetch(c: int, r: int, client: httpx.AsyncClient):
        url = tile_url(meta.tiles_dir, meta.resource_id, level, c, r)
        tile_data[(c, r)] = await _download_tile(client, url, sem)
        progress.done += 1
        if on_progress:
            on_progress()

    async with httpx.AsyncClient(timeout=30) as client:
        await asyncio.gather(*[_fetch(c, r, client) for r in range(rows) for c in range(cols)])

    return _build_canvas(tile_data, img_w, img_h, progress, on_progress)


# ── COLL 拼接 ────────────────────────────────────────────────
async def _stitch_coll(
    meta: ArtworkMeta,
    level: int,
    progress: DownloadProgress,
    on_progress: Callable[[], None] | None,
) -> BytesIO:
    # 计算各分片在目标 level 的尺寸
    piece_plans = []
    total_tiles = 0
    for piece in meta.pieces:
        scale = 2 ** (piece.max_level - level)
        pw = math.ceil(piece.width / scale)
        ph = math.ceil(piece.height / scale)
        cols = math.ceil(pw / _TILE_SIZE)
        rows = math.ceil(ph / _TILE_SIZE)
        cx = math.ceil(piece.canvas_x / scale)
        cy = math.ceil(piece.canvas_y / scale)
        piece_plans.append((piece, pw, ph, cols, rows, cx, cy))
        total_tiles += cols * rows

    # 总画布尺寸
    global_scale = 2 ** (meta.max_level - level)
    canvas_w = math.ceil(meta.width / global_scale)
    canvas_h = math.ceil(meta.height / global_scale)

    progress.total = total_tiles
    progress.done = 0
    progress.status = "downloading"
    progress.message = f"正在下载 {total_tiles} 个图块（{len(meta.pieces)} 个分片）..."

    # 并发下载所有分片的所有图块
    # 结构：piece_tiles[piece_idx][(col, row)] = bytes
    piece_tiles: list[dict[tuple[int, int], bytes]] = [{} for _ in meta.pieces]
    sem = asyncio.Semaphore(12)

    async def _fetch(pidx: int, piece: PieceMeta, c: int, r: int, client: httpx.AsyncClient):
        url = tile_url(piece.tiles_dir, piece.resource_id, level, c, r)
        piece_tiles[pidx][(c, r)] = await _download_tile(client, url, sem)
        progress.done += 1
        if on_progress:
            on_progress()

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = []
        for pidx, (piece, pw, ph, cols, rows, cx, cy) in enumerate(piece_plans):
            for r in range(rows):
                for c in range(cols):
                    tasks.append(_fetch(pidx, piece, c, r, client))
        await asyncio.gather(*tasks)

    progress.status = "stitching"
    progress.message = f"正在拼接 {len(meta.pieces)} 个分片..."
    if on_progress:
        on_progress()

    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    for pidx, (piece, pw, ph, cols, rows, cx, cy) in enumerate(piece_plans):
        piece_img = Image.new("RGB", (pw, ph), (255, 255, 255))
        for r in range(rows):
            for c in range(cols):
                data = piece_tiles[pidx].get((c, r))
                if data and len(data) > 100:
                    t = Image.open(BytesIO(data))
                    piece_img.paste(t, (c * _TILE_SIZE, r * _TILE_SIZE))
        canvas.paste(piece_img, (cx, cy))

    buf = BytesIO()
    canvas.save(buf, "JPEG", quality=95)
    buf.seek(0)

    progress.status = "done"
    progress.message = f"完成 ({canvas_w}×{canvas_h})"
    if on_progress:
        on_progress()

    return buf


# ── PAGE 下载（各页独立，打包 ZIP） ──────────────────────────
async def _stitch_page(
    meta: ArtworkMeta,
    level: int,
    progress: DownloadProgress,
    on_progress: Callable[[], None] | None,
) -> BytesIO:
    """每页独立拼接为 JPEG，所有页打包返回 ZIP BytesIO。"""
    # 计算每页在目标 level 的参数
    page_plans = []
    total_tiles = 0
    for piece in meta.pieces:
        effective_level = max(piece.min_level, min(level, piece.max_level))
        scale = 2 ** (piece.max_level - effective_level)
        pw = math.ceil(piece.width / scale)
        ph = math.ceil(piece.height / scale)
        cols = math.ceil(pw / _TILE_SIZE)
        rows = math.ceil(ph / _TILE_SIZE)
        page_plans.append((piece, effective_level, pw, ph, cols, rows))
        total_tiles += cols * rows

    progress.total = total_tiles
    progress.done = 0
    progress.status = "downloading"
    progress.message = f"正在下载 {total_tiles} 个图块（{len(meta.pieces)} 页）..."

    # 并发下载所有页的图块
    page_tiles: list[dict[tuple[int, int], bytes]] = [{} for _ in meta.pieces]
    sem = asyncio.Semaphore(12)

    async def _fetch(pidx: int, piece: PieceMeta, lvl: int, c: int, r: int, client: httpx.AsyncClient):
        url = tile_url(piece.tiles_dir, piece.resource_id, lvl, c, r)
        page_tiles[pidx][(c, r)] = await _download_tile(client, url, sem)
        progress.done += 1
        if on_progress:
            on_progress()

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = []
        for pidx, (piece, lvl, pw, ph, cols, rows) in enumerate(page_plans):
            for r in range(rows):
                for c in range(cols):
                    tasks.append(_fetch(pidx, piece, lvl, c, r, client))
        await asyncio.gather(*tasks)

    progress.status = "stitching"
    progress.message = f"正在拼接并打包 {len(meta.pieces)} 页..."
    if on_progress:
        on_progress()

    zip_buf = BytesIO()
    saved = 0
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for pidx, (piece, lvl, pw, ph, cols, rows) in enumerate(page_plans):
            tiles = page_tiles[pidx]
            valid = sum(1 for d in tiles.values() if len(d) > 100)
            if valid == 0:
                continue  # 该页 CDN 暂不可用，跳过
            page_img = Image.new("RGB", (pw, ph), (255, 255, 255))
            for r in range(rows):
                for c in range(cols):
                    data = tiles.get((c, r))
                    if data and len(data) > 100:
                        page_img.paste(Image.open(BytesIO(data)), (c * _TILE_SIZE, r * _TILE_SIZE))
            page_buf = BytesIO()
            page_img.save(page_buf, "JPEG", quality=95)
            saved += 1
            zf.writestr(f"{meta.author}_{meta.name}_{pidx + 1}.jpg", page_buf.getvalue())

    zip_buf.seek(0)
    progress.status = "done"
    progress.message = f"完成（{saved}/{len(meta.pieces)} 页已打包）"
    if on_progress:
        on_progress()

    return zip_buf


def _build_canvas(
    tile_data: dict,
    img_w: int,
    img_h: int,
    progress: DownloadProgress,
    on_progress: Callable[[], None] | None,
) -> BytesIO:
    progress.status = "stitching"
    progress.message = "正在拼接图片..."
    if on_progress:
        on_progress()

    canvas = Image.new("RGB", (img_w, img_h), (255, 255, 255))
    rows = math.ceil(img_h / _TILE_SIZE)
    cols = math.ceil(img_w / _TILE_SIZE)
    for r in range(rows):
        for c in range(cols):
            data = tile_data.get((c, r))
            if data and len(data) > 100:
                canvas.paste(Image.open(BytesIO(data)), (c * _TILE_SIZE, r * _TILE_SIZE))

    buf = BytesIO()
    canvas.save(buf, "JPEG", quality=95)
    buf.seek(0)

    progress.status = "done"
    progress.message = f"完成 ({img_w}×{img_h})"
    if on_progress:
        on_progress()

    return buf
