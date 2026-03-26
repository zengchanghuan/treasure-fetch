"""
SEO 模块：作品详情页、sitemap、robots.txt。

用法::

    from backend.seo import seo_router
    app.include_router(seo_router)
"""

from .router import router as seo_router

__all__ = ["seo_router"]
