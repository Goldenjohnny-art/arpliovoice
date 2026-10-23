"""VoiceStudio release-brand and source-launch contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = json.loads((ROOT / "package.json").read_text())["version"]


def test_current_version_is_in_lockstep_everywhere() -> None:
    package = json.loads((ROOT / "package.json").read_text())
    assert package["version"] == CURRENT_VERSION

    mirrors = {
        "pyproject.toml": r'(?m)^version = "([^"]+)"',
        "backend/core/version.py": r'(?m)^_FALLBACK_VERSION = "([^"]+)"',
    }
    for path, pattern in mirrors.items():
        match = re.search(pattern, (ROOT / path).read_text())
        assert match and match.group(1) == CURRENT_VERSION, path

    lock_contracts = {"uv.lock": r'name = "omnivoice"\s+version = "([^"]+)"'}
    for path, pattern in lock_contracts.items():
        match = re.search(pattern, (ROOT / path).read_text())
        assert match and match.group(1) == CURRENT_VERSION, path


def test_visible_brand_surfaces_say_arplio_voice() -> None:
    visible_files = ("electron/build/Info.plist", "electron/src/renderer/index.html")
    product_name = json.loads((ROOT / "config/app.json").read_text())["productName"]
    assert product_name == "Arplio Voice"
    for path in visible_files:
        text = (ROOT / path).read_text()
        assert "__APP_PRODUCT_NAME__" in text, path
        assert "OmniVoice needs" not in text, path
        assert "OmniVoice may" not in text, path
        assert "OmniVoice Gallery" not in text, path

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "<h1>Arplio Voice</h1>" in readme
    # AGPL attribution to the upstream work stays visible.
    assert "VoiceStudio](https://github.com/debpalash/VoiceStudio) by\nPalash Debnath" in readme


def test_arplio_mark_is_the_app_icon_everywhere() -> None:
    """One source logo (branding/logo.png) feeds the in-app mark, the favicon
    and the packaged icons; none of them may fall back to the upstream mark."""
    assert (ROOT / "branding/logo.png").is_file()
    brand = (ROOT / "electron/src/renderer/src/lib/brand.ts").read_text()
    assert "public/brand-mark.png" in brand
    html = (ROOT / "electron/src/renderer/index.html").read_text()
    assert 'href="/favicon.png"' in html
    assert not (ROOT / "electron/public/favicon.svg").exists()
    for name in ("brand-mark.png", "favicon.png"):
        assert (ROOT / "electron/public" / name).is_file(), name
    for name in ("icon.png", "icon.ico", "icon.icns", "32x32.png"):
        assert (ROOT / "electron/build/icons" / name).is_file(), name


def test_python_package_metadata_points_to_voicestudio() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text()
    assert 'Homepage = "https://github.com/debpalash/VoiceStudio"' in pyproject
    assert 'Repository = "https://github.com/debpalash/VoiceStudio"' in pyproject
    assert '"Upstream TTS Model" = "https://github.com/k2-fsa/OmniVoice"' in pyproject


def test_engine_help_names_the_app_not_the_upstream_model() -> None:
    paths = (
        "backend/engines/confucius4/__init__.py",
        "backend/engines/confucius4/bootstrap.py",
        "backend/engines/dots_tts/__init__.py",
        "backend/engines/dots_tts/bootstrap.py",
        "backend/engines/indextts/__init__.py",
        "backend/engines/indextts/bootstrap.py",
        "backend/engines/moss_tts_v15/__init__.py",
        "backend/engines/moss_tts_v15/bootstrap.py",
    )
    stale_help = re.compile(r"(?:restart|reinstall|re-launch|Run) OmniVoice")
    for path in paths:
        text = (ROOT / path).read_text()
        assert not stale_help.search(text), path


def test_compatibility_identifiers_stay_stable() -> None:
    package = json.loads((ROOT / "package.json").read_text())
    assert package["name"] == "omnivoice-studio-monorepo"
    assert 'name = "omnivoice"' in (ROOT / "pyproject.toml").read_text()
    app_config = json.loads((ROOT / "config/app.json").read_text())
    assert app_config["appId"] == "com.voicestudio.desktop"


def test_active_source_launch_is_electron_and_web_ports_clean_quietly() -> None:
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    assert scripts["dev"] == "bun run --cwd electron dev"
    assert not any("tauri" in name for name in scripts)
    command = scripts["predev:web"]
    assert command.endswith("bun scripts/clear-dev-ports.mjs")
    assert "|| true" not in command


def test_icon_rail_has_no_static_section_captions_and_keeps_air_between_items() -> None:
    rail = (ROOT / "electron/src/shared/components/NavRail.jsx").read_text()
    for stale_caption in ("Start", "Create", "Workflows", "Reference"):
        assert stale_caption not in rail
    assert "pt-[18px]" in rail
    assert "gap-[9px]" in rail


def test_electron_launch_preserves_an_existing_backend():
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    for name in ("predev", "predesktop"):
        assert "clear-dev-ports" not in scripts[name]
        assert "desktop-runtime-preflight" not in scripts[name]
    assert scripts["dev"] == "bun run --cwd electron dev"
    assert scripts["desktop-prod:run"] == "bun run start"
    assert scripts["start"] == "bun run --cwd electron start"
