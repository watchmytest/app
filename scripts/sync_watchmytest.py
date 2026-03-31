#!/usr/bin/env python3
"""Generate a local report of releases and documentation for mov2day/watchmytest."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWNER = "mov2day"
REPO = "watchmytest"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"
OUTPUT_FILE = Path("WATCHMYTEST_UPDATES.md")
MAX_RELEASES = 20
MAX_DOC_FILES = 60


def github_get(url: str, token: str | None = None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "watchmytest-sync-script",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def fetch_releases(token: str | None):
    url = f"{API_BASE}/releases?per_page={MAX_RELEASES}"
    return github_get(url, token)


def fetch_docs(token: str | None):
    tree_url = f"{API_BASE}/git/trees/HEAD?recursive=1"
    data = github_get(tree_url, token)
    tree = data.get("tree", [])

    docs = []
    for item in tree:
        if item.get("type") != "blob":
            continue

        path = item.get("path", "")
        lower = path.lower()
        if not lower.endswith((".md", ".mdx", ".rst", ".txt")):
            continue

        if (
            lower.startswith("docs/")
            or lower.startswith("doc/")
            or lower.endswith("readme.md")
            or lower.endswith("contributing.md")
            or lower.endswith("changelog.md")
        ):
            docs.append(path)

    docs.sort()
    return docs[:MAX_DOC_FILES]


def format_markdown(releases, docs):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# mov2day/watchmytest Updates",
        "",
        f"Last synced: **{now}**",
        "",
        "## Releases",
        "",
    ]

    if releases:
        for release in releases:
            name = release.get("name") or release.get("tag_name") or "Unnamed release"
            tag = release.get("tag_name", "")
            url = release.get("html_url", f"https://github.com/{OWNER}/{REPO}/releases")
            published = release.get("published_at") or release.get("created_at") or "unknown date"
            lines.append(f"- [{name} ({tag})]({url}) — published `{published}`")
    else:
        lines.append("- No releases found.")

    lines.extend([
        "",
        "## Documentation files",
        "",
    ])

    if docs:
        for path in docs:
            url = f"https://github.com/{OWNER}/{REPO}/blob/HEAD/{path}"
            lines.append(f"- [`{path}`]({url})")
    else:
        lines.append("- No documentation-like files found.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    try:
        releases = fetch_releases(token)
        docs = fetch_docs(token)
    except urllib.error.HTTPError as error:
        print(f"GitHub API request failed: {error.code} {error.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"Network error contacting GitHub API: {error.reason}", file=sys.stderr)
        return 1

    markdown = format_markdown(releases, docs)
    OUTPUT_FILE.write_text(markdown, encoding="utf-8")
    print(f"Updated {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
