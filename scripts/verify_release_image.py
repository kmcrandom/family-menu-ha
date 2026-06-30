#!/usr/bin/env python3
"""Verify that the Home Assistant add-on image exists in GHCR."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "family-menu" / "config.yaml"


class ReleaseImageError(RuntimeError):
    """Raised when release image verification cannot pass."""


def read_addon_metadata(config_path: Path) -> tuple[str, str]:
    text = config_path.read_text(encoding="utf-8")
    version_match = re.search(r'^version:\s*"([^"]+)"\s*$', text, re.MULTILINE)
    image_match = re.search(r"^image:\s*(\S+)\s*$", text, re.MULTILINE)
    if not version_match:
        raise ReleaseImageError(f"{config_path} does not declare a quoted version")
    if not image_match:
        raise ReleaseImageError(f"{config_path} does not declare an image")
    return image_match.group(1), version_match.group(1)


def inspect_manifest(image_ref: str) -> None:
    try:
        result = subprocess.run(
            ["docker", "manifest", "inspect", image_ref],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ReleaseImageError("docker is not installed or is not on PATH") from exc

    if result.returncode != 0:
        detail = result.stderr.strip() or "manifest inspect failed"
        raise ReleaseImageError(f"{image_ref} is not available yet: {detail}")


def verify_release_image(
    config_path: Path = DEFAULT_CONFIG,
    version_override: str | None = None,
    image_override: str | None = None,
) -> str:
    image, config_version = read_addon_metadata(config_path)
    version = version_override or config_version
    image_ref = f"{image_override or image}:{version}"
    inspect_manifest(image_ref)
    return image_ref


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the Family Menu Home Assistant add-on image tag exists."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to the add-on config.yaml file.",
    )
    parser.add_argument(
        "--version",
        help="Version tag to check. Defaults to family-menu/config.yaml version.",
    )
    parser.add_argument(
        "--image",
        help="Image repository to check. Defaults to family-menu/config.yaml image.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        image_ref = verify_release_image(args.config, args.version, args.image)
    except ReleaseImageError as exc:
        print(f"Release image verification failed: {exc}", file=sys.stderr)
        return 1

    print(f"Release image is available: {image_ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
