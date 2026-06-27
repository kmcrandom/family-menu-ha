from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from family_menu.app import create_app
from family_menu.config import Settings


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "family-menu.db"
    seed_path = Path(__file__).parents[1] / "family-menu" / "data" / "generic-starter-meal-catalog.example.json"
    static_dir = tmp_path / "static"
    settings = Settings(db_path=db_path, seed_path=seed_path, static_dir=static_dir)
    app = create_app(settings=settings)
    return TestClient(app)


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    db_path = tmp_path / "family-menu.db"
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()
