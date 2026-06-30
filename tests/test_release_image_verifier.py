from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_release_image.py"
spec = importlib.util.spec_from_file_location("verify_release_image", SCRIPT)
verify_release_image = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(verify_release_image)


def write_config(path: Path, version: str = "1.2.3") -> None:
    path.write_text(
        "\n".join(
            [
                "---",
                "name: Family Menu",
                f'version: "{version}"',
                "image: ghcr.io/kmcrandom/family-menu-ha",
            ]
        ),
        encoding="utf-8",
    )


def test_reads_image_and_version_from_config(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    write_config(config, "2.3.4")

    image, version = verify_release_image.read_addon_metadata(config)

    assert image == "ghcr.io/kmcrandom/family-menu-ha"
    assert version == "2.3.4"


def test_verify_uses_config_version_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config.yaml"
    write_config(config, "2.3.4")
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stderr="")

    monkeypatch.setattr(verify_release_image.subprocess, "run", fake_run)

    image_ref = verify_release_image.verify_release_image(config)

    assert image_ref == "ghcr.io/kmcrandom/family-menu-ha:2.3.4"
    assert calls[0][0] == [
        "docker",
        "manifest",
        "inspect",
        "ghcr.io/kmcrandom/family-menu-ha:2.3.4",
    ]


def test_verify_allows_version_and_image_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config.yaml"
    write_config(config, "2.3.4")

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stderr="")

    monkeypatch.setattr(verify_release_image.subprocess, "run", fake_run)

    image_ref = verify_release_image.verify_release_image(
        config,
        version_override="9.9.9",
        image_override="ghcr.io/example/family-menu-ha",
    )

    assert image_ref == "ghcr.io/example/family-menu-ha:9.9.9"


def test_missing_manifest_raises_clear_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config.yaml"
    write_config(config, "2.3.4")

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, stderr="manifest unknown")

    monkeypatch.setattr(verify_release_image.subprocess, "run", fake_run)

    with pytest.raises(verify_release_image.ReleaseImageError) as excinfo:
        verify_release_image.verify_release_image(config)

    assert "ghcr.io/kmcrandom/family-menu-ha:2.3.4 is not available yet" in str(
        excinfo.value
    )
    assert "manifest unknown" in str(excinfo.value)


def test_missing_docker_raises_clear_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config.yaml"
    write_config(config, "2.3.4")

    def fake_run(command, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(verify_release_image.subprocess, "run", fake_run)

    with pytest.raises(verify_release_image.ReleaseImageError) as excinfo:
        verify_release_image.verify_release_image(config)

    assert "docker is not installed or is not on PATH" in str(excinfo.value)
