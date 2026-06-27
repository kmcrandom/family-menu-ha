from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_addon_changelog_contains_config_version() -> None:
    config = (ROOT / "family-menu" / "config.yaml").read_text()
    match = re.search(r'^version:\s*"([^"]+)"\s*$', config, re.MULTILINE)
    assert match, "family-menu/config.yaml must declare a quoted add-on version"

    version = match.group(1)
    changelog = (ROOT / "family-menu" / "CHANGELOG.md").read_text()

    assert re.search(rf"^##\s+{re.escape(version)}\s*$", changelog, re.MULTILINE), (
        f"family-menu/CHANGELOG.md must contain a ## {version} entry"
    )
