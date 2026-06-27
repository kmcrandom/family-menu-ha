from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    seed_path: Path
    static_dir: Path
    host: str = "127.0.0.1"
    port: int = 8097
    reload: bool = False
    auto_seed: bool = True


def load_settings() -> Settings:
    package_dir = Path(__file__).parent
    repo_root = package_dir.parents[2]
    db_path = Path(os.getenv("FAMILY_MENU_DB", repo_root / "family-menu.db"))
    seed_path = Path(os.getenv("FAMILY_MENU_SEED", repo_root / "data" / "generic-starter-meal-catalog.example.json"))
    static_dir = Path(os.getenv("FAMILY_MENU_STATIC", package_dir / "static"))
    return Settings(
        db_path=db_path,
        seed_path=seed_path,
        static_dir=static_dir,
        host=os.getenv("FAMILY_MENU_HOST", "127.0.0.1"),
        port=int(os.getenv("FAMILY_MENU_PORT", "8097")),
        reload=os.getenv("FAMILY_MENU_RELOAD", "").lower() in {"1", "true", "yes"},
        auto_seed=os.getenv("FAMILY_MENU_AUTO_SEED", "1").lower() not in {"0", "false", "no"},
    )
