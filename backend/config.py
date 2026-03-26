"""
统一配置模块。

所有可配置项从环境变量读取，支持 .env 文件。
其他模块通过 ``from backend.config import settings`` 获取配置。
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ── 管理后台 ─────────────────────────────────────────────
    admin_password: str = "changeme"

    # ── 数据库 ───────────────────────────────────────────────
    db_path: str = "data/analytics.db"

    # ── 限流 ─────────────────────────────────────────────────
    rate_limit_metadata_per_min: int = 20
    rate_limit_download_per_min: int = 5
    daily_download_standard: int = 10
    daily_download_hd: int = 3

    @property
    def db_abs_path(self) -> Path:
        p = Path(self.db_path)
        return p if p.is_absolute() else _PROJECT_ROOT / p

    model_config = {"env_file": str(_PROJECT_ROOT / ".env"), "env_file_encoding": "utf-8"}


settings = Settings()
