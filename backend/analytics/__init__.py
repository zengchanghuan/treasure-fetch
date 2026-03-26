"""
Analytics 埋点模块。

用法::

    from backend.analytics import get_tracker

    tracker = get_tracker()
    await tracker.track("page_view", {"ip": "1.2.3.4", "path": "/"})
"""

from __future__ import annotations

from .tracker import EventTracker, SQLiteTracker

_instance: SQLiteTracker | None = None


def get_tracker() -> SQLiteTracker:
    """返回全局单例 Tracker（懒加载）。"""
    global _instance
    if _instance is None:
        from backend.config import settings

        _instance = SQLiteTracker(settings.db_abs_path)
    return _instance


__all__ = ["EventTracker", "SQLiteTracker", "get_tracker"]
