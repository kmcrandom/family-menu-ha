from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from family_menu.app import create_app
from family_menu.config import Settings


def test_prefixed_api_routes_to_same_handlers(client):
    response = client.get("/api/hassio_ingress/example-token/api/v1/meals")

    assert response.status_code == 200
    assert response.json()


def test_prefixed_spa_route_returns_index(tmp_path: Path):
    client = static_client(tmp_path)

    response = client.get("/api/hassio_ingress/example-token/weekly-plan")

    assert response.status_code == 200
    assert "Family Menu Test Index" in response.text


def test_prefixed_static_file_request_returns_bundle(tmp_path: Path):
    client = static_client(tmp_path)

    response = client.get("/api/hassio_ingress/example-token/main-test.js")

    assert response.status_code == 200
    assert response.text == "console.log('family menu');"


def test_prefixed_asset_file_request_returns_asset(tmp_path: Path):
    client = static_client(tmp_path)

    response = client.get("/api/hassio_ingress/example-token/assets/icon.svg")

    assert response.status_code == 200
    assert response.text == "<svg></svg>"


def static_client(tmp_path: Path) -> TestClient:
    static_dir = tmp_path / "static"
    browser_dir = static_dir / "browser"
    assets_dir = browser_dir / "assets"
    assets_dir.mkdir(parents=True)
    (browser_dir / "index.html").write_text("<h1>Family Menu Test Index</h1>", encoding="utf-8")
    (browser_dir / "main-test.js").write_text("console.log('family menu');", encoding="utf-8")
    (assets_dir / "icon.svg").write_text("<svg></svg>", encoding="utf-8")

    settings = Settings(
        db_path=tmp_path / "family-menu.db",
        seed_path=Path(__file__).parents[1] / "family-menu" / "data" / "generic-starter-meal-catalog.example.json",
        static_dir=static_dir,
    )
    return TestClient(create_app(settings=settings))
