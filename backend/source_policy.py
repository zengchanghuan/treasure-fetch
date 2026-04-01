from __future__ import annotations

from typing import TYPE_CHECKING

from .config import settings

if TYPE_CHECKING:
    from .tile_service import ArtworkMeta


_OFFICIAL_VIEW_BASE = "https://g2.ltfc.net/view"
_BLOCKED_MESSAGE = "当前仅支持台北故宫博物院公开馆藏页面"


def build_official_url(artwork_type: str, artwork_id: str) -> str:
    return f"{_OFFICIAL_VIEW_BASE}/{artwork_type.upper()}/{artwork_id}"


def owner_matches_policy(owner: str) -> bool:
    owner_text = (owner or "").strip()
    if not owner_text:
        return False
    return any(keyword in owner_text for keyword in settings.allowed_owner_keyword_list)


def ensure_allowed_artwork(meta: ArtworkMeta) -> None:
    if owner_matches_policy(meta.owner):
        return
    raise ValueError(_BLOCKED_MESSAGE)


def blocked_message() -> str:
    return _BLOCKED_MESSAGE
