from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    db_path: Path
    seed_path: Path
    static_dir: Path
    host: str = "127.0.0.1"
    port: int = 8081
    reload: bool = False
    auto_seed: bool = True


def load_settings(options_path: Path | None = None) -> Settings:
    package_dir = Path(__file__).parent
    addon_dir = package_dir.parents[1]
    repo_root = addon_dir.parent
    options_path = options_path or Path("/data/options.json")
    addon_options = _load_options(options_path)
    has_addon_options = bool(addon_options)

    default_db = Path("/data/family-menu.sqlite") if has_addon_options else repo_root / "family-menu.db"
    default_seed = (
        Path("/app/data/generic-starter-meal-catalog.example.json")
        if has_addon_options
        else addon_dir / "data" / "generic-starter-meal-catalog.example.json"
    )
    default_static = Path("/app/src/family_menu/static") if has_addon_options else package_dir / "static"
    default_host = "0.0.0.0" if has_addon_options else "127.0.0.1"
    default_port = 8081
    default_auto_seed = True

    db_path = Path(_setting("FAMILY_MENU_DB", addon_options, ("database", "path"), default_db))
    seed_path = Path(_setting("FAMILY_MENU_SEED", addon_options, ("seed", "path"), default_seed))
    static_dir = Path(os.getenv("FAMILY_MENU_STATIC", default_static))
    host = str(_setting("FAMILY_MENU_HOST", addon_options, ("server", "host"), default_host))
    port = int(_setting("FAMILY_MENU_PORT", addon_options, ("server", "port"), default_port))
    auto_seed = _bool_setting("FAMILY_MENU_AUTO_SEED", addon_options, ("seed", "auto_seed"), default_auto_seed)
    return Settings(
        db_path=db_path,
        seed_path=seed_path,
        static_dir=static_dir,
        host=host,
        port=port,
        reload=os.getenv("FAMILY_MENU_RELOAD", "").lower() in {"1", "true", "yes"},
        auto_seed=auto_seed,
    )


def _load_options(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        return {}
    return loaded


def _setting(env_name: str, options: dict[str, Any], path: tuple[str, ...], default: Any) -> Any:
    env_value = os.getenv(env_name)
    if env_value not in {None, ""}:
        return env_value
    value: Any = options
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return default if value is None or value == "" else value


def _bool_setting(env_name: str, options: dict[str, Any], path: tuple[str, ...], default: bool) -> bool:
    value = _setting(env_name, options, path, default)
    if isinstance(value, bool):
        return value
    return str(value).lower() not in {"0", "false", "no", "off"}
