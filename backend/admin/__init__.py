"""
Admin 管理后台模块。

用法::

    from backend.admin import admin_router
    app.include_router(admin_router, prefix="/admin")
"""

from .router import router as admin_router

__all__ = ["admin_router"]
