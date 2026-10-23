"""No analytics destination token is committed anywhere.

Upstream VoiceStudio committed its publishable PostHog project token in
backend/core/analytics.py and electron/src/shared/utils/analytics.ts (#1193).
Arplio Voice must not report its users to the upstream project, so both
in-repo defaults are empty: analytics stays off, and its consent prompt hidden,
unless an operator supplies an Arplio token through VITE_POSTHOG_KEY /
POSTHOG_PROJECT_TOKEN at build or run time. This guard keeps any `phc_` literal
out of tracked files and keeps that override chain wired.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

# A PostHog project key. Deliberately matched by SHAPE, not by the specific value,
# so a key can't slip into a *different* file unnoticed.
_POSTHOG_KEY_RE = re.compile(r"phc_[A-Za-z0-9]{20,}")

# The files that hold the (empty) in-repo default destination.
_CANONICAL_TOKEN_FILES = (
    "backend/core/analytics.py",
    "electron/src/shared/utils/analytics.ts",
)
# Guards that must name the retired upstream token to pin its absence.
_EXEMPT_FILES = {
    "tests/test_no_committed_analytics_token.py",
    "tests/test_gitleaks_allowlist.py",
}

_SKIP_DIRS = {"node_modules", ".git", "target", "dist", "build", ".venv", "zig-out"}
_SCAN_EXT = {".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".json", ".yml", ".yaml", ".md", ".env"}


def _tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=_REPO, capture_output=True, text=True, check=True
    ).stdout
    for name in (n for n in out.split("\0") if n):
        p = Path(name)
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in _SCAN_EXT:
            yield name, _REPO / p


def test_no_posthog_token_literal_is_committed():
    offenders = []
    for name, path in _tracked_files():
        if name in _EXEMPT_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _POSTHOG_KEY_RE.search(text):
            offenders.append(name)

    assert not offenders, (
        "A PostHog token literal is committed: "
        + ", ".join(offenders)
        + ". Arplio Voice ships no analytics destination; supply one via "
        "VITE_POSTHOG_KEY / POSTHOG_PROJECT_TOKEN at build/run time."
    )


def test_both_in_repo_default_tokens_are_empty():
    """An empty default keeps analytics off and the consent prompt hidden."""
    backend = (_REPO / _CANONICAL_TOKEN_FILES[0]).read_text(encoding="utf-8")
    frontend = (_REPO / _CANONICAL_TOKEN_FILES[1]).read_text(encoding="utf-8")
    assert re.search(r'(?m)^_PUBLIC_PROJECT_TOKEN = ""$', backend)
    assert re.search(r"(?m)^const PUBLIC_PROJECT_TOKEN = '';$", frontend)


# ── the OVERRIDE chain must stay wired ───────────────────────────────────────
#
# The in-repo default is the fallback; release builds override it with the repo
# secret, and a developer's process env overrides everything:
#
#     repo secret -> release.yml -> tauri-action -> option_env! in backend.rs
#                 -> spawned backend process env -> analytics._resolved_token()
#
# Every link is invisible when it breaks (events just land in the default
# project instead of the release one). These pin the links that live in files a
# future change could quietly drop.


def test_the_frontend_reads_its_token_override_from_the_build_env():
    """The build-time override mechanism must stay in place."""
    src = (_REPO / "electron/src/shared/utils/analytics.ts").read_text(encoding="utf-8")
    assert "VITE_POSTHOG_KEY" in src


def test_release_workflow_still_passes_the_secret_to_the_build():
    wf = (_REPO / ".github/workflows/electron-release.yml").read_text(encoding="utf-8")
    assert "VITE_POSTHOG_KEY" in wf, "the build no longer receives the analytics token override"
    assert "secrets.POSTHOG_PROJECT_TOKEN" in wf, "the override must come from the repo secret"


def test_the_shell_hands_the_token_to_the_backend_it_spawns():
    """Without this a baked release token could never beat the in-repo default."""
    src = (_REPO / "electron/src/main/backend.ts").read_text(encoding="utf-8")
    assert "__POSTHOG_PROJECT_TOKEN__" in src, "the shell no longer bakes in the token"
    assert "POSTHOG_PROJECT_TOKEN" in src, "the backend process is no longer given the override"
    # #1193: the shell marks everything it spawns as the "installer" channel.

    # option_env! is resolved at COMPILE time, so cargo must rebuild when the
    # secret changes — otherwise a cached build keeps the token it first saw.
    config = (_REPO / "electron/electron.vite.config.ts").read_text(encoding="utf-8")
    assert "VITE_POSTHOG_KEY" in config
