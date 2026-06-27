from __future__ import annotations

import json
from pathlib import Path

from family_menu.config import load_settings


def test_load_settings_uses_local_defaults_without_addon_options(monkeypatch, tmp_path: Path):
    clear_family_menu_env(monkeypatch)

    settings = load_settings(options_path=tmp_path / "missing-options.json")

    assert settings.db_path.name == "family-menu.db"
    assert settings.seed_path.name == "generic-starter-meal-catalog.example.json"
    assert settings.seed_path.parts[-3:] == ("family-menu", "data", "generic-starter-meal-catalog.example.json")
    assert settings.host == "127.0.0.1"
    assert settings.port == 8097
    assert settings.auto_seed is True


def test_load_settings_reads_home_assistant_options(monkeypatch, tmp_path: Path):
    clear_family_menu_env(monkeypatch)
    options_path = tmp_path / "options.json"
    options_path.write_text(
        json.dumps(
            {
                "database": {"path": "/data/custom.sqlite"},
                "seed": {"path": "/data/private-seed.json", "auto_seed": False},
                "server": {"host": "0.0.0.0", "port": 8098},
            }
        ),
        encoding="utf-8",
    )

    settings = load_settings(options_path=options_path)

    assert settings.db_path == Path("/data/custom.sqlite")
    assert settings.seed_path == Path("/data/private-seed.json")
    assert settings.host == "0.0.0.0"
    assert settings.port == 8098
    assert settings.auto_seed is False


def test_environment_overrides_home_assistant_options(monkeypatch, tmp_path: Path):
    clear_family_menu_env(monkeypatch)
    options_path = tmp_path / "options.json"
    options_path.write_text(
        json.dumps(
            {
                "database": {"path": "/data/options.sqlite"},
                "seed": {"path": "/data/options-seed.json", "auto_seed": True},
                "server": {"host": "0.0.0.0", "port": 8098},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("FAMILY_MENU_DB", str(tmp_path / "env.sqlite"))
    monkeypatch.setenv("FAMILY_MENU_SEED", str(tmp_path / "env-seed.json"))
    monkeypatch.setenv("FAMILY_MENU_HOST", "127.0.0.1")
    monkeypatch.setenv("FAMILY_MENU_PORT", "8100")
    monkeypatch.setenv("FAMILY_MENU_AUTO_SEED", "0")

    settings = load_settings(options_path=options_path)

    assert settings.db_path == tmp_path / "env.sqlite"
    assert settings.seed_path == tmp_path / "env-seed.json"
    assert settings.host == "127.0.0.1"
    assert settings.port == 8100
    assert settings.auto_seed is False


def clear_family_menu_env(monkeypatch):
    for key in (
        "FAMILY_MENU_DB",
        "FAMILY_MENU_SEED",
        "FAMILY_MENU_STATIC",
        "FAMILY_MENU_HOST",
        "FAMILY_MENU_PORT",
        "FAMILY_MENU_RELOAD",
        "FAMILY_MENU_AUTO_SEED",
    ):
        monkeypatch.delenv(key, raising=False)
