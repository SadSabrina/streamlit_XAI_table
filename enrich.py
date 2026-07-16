"""
Refresh script: updates stars, last_updated, and description_en
for all libraries in data/xai_libraries.csv using the GitHub API.

Existing rows are preserved as-is; only metadata fields are overwritten.
Libraries without a GitHub URL are skipped silently.

GitHub public API: 60 req/hour unauthenticated.
Set GITHUB_TOKEN env var for 5000 req/hour:
  export GITHUB_TOKEN=ghp_...
"""

from __future__ import annotations

import os
import re
import time
import requests
import pandas as pd
from datetime import datetime, timezone

DATA_PATH = "data/xai_libraries.csv"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}


def extract_github_repo(url: str) -> str | None:
    if not isinstance(url, str):
        return None
    m = re.search(r"github\.com/([^/]+/[^/?#\s]+)", url)
    return m.group(1).rstrip("/") if m else None


def fetch_github(repo: str) -> dict:
    try:
        r = requests.get(
            f"https://api.github.com/repos/{repo}",
            headers=HEADERS,
            timeout=10,
        )
        if r.status_code == 404:
            print(f"  404: {repo}")
            return {}
        if r.status_code == 403:
            print("  Rate limit hit — set GITHUB_TOKEN for more requests")
            return {}
        r.raise_for_status()
        data = r.json()
        pushed = (data.get("pushed_at") or "")[:10]
        return {
            "description_en": data.get("description") or "",
            "stars": int(data.get("stargazers_count") or 0),
            "last_updated": pushed,
        }
    except Exception as e:
        print(f"  Error: {e}")
        return {}


def refresh():
    df = pd.read_csv(DATA_PATH)
    total = len(df)
    updated = 0

    for i, row in df.iterrows():
        repo = extract_github_repo(row.get("url", ""))
        print(f"[{i+1}/{total}] {row['library']}", end="")

        if not repo:
            print(" — no GitHub URL, skipping")
            continue

        print(f" ({repo})", end=" ")
        meta = fetch_github(repo)

        if meta:
            for field in ("description_en", "stars", "last_updated"):
                if field in meta:
                    df.at[i, field] = meta[field]
            updated += 1
            print(f"✓ {meta.get('stars', '?')} ⭐  {meta.get('last_updated', '?')}")
        else:
            print("— skipped")

        time.sleep(0.5)

    df.to_csv(DATA_PATH, index=False)
    print(f"\nDone. Updated {updated}/{total} libraries → {DATA_PATH}")


if __name__ == "__main__":
    refresh()
