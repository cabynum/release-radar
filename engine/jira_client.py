"""Jira REST API client for release-radar.

Handles authentication, issue fetching, and changelog retrieval.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
JIRA_BASE = "https://redhat.atlassian.net"


def load_env():
    """Load .env from project root or dashboard dir."""
    for candidate in [PROJECT_DIR / ".env",
                      PROJECT_DIR.parent / "dashboard" / ".env"]:
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())
            return
    print("  WARNING: No .env found, using environment variables")


def _auth_header() -> str:
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not email or not token:
        sys.exit("JIRA_EMAIL and JIRA_API_TOKEN required in .env or environment")
    return f"Basic {base64.b64encode(f'{email}:{token}'.encode()).decode()}"


def jira_get(path: str) -> dict:
    url = f"{JIRA_BASE}{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", _auth_header())
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def jira_post(path: str, body: dict) -> dict:
    url = f"{JIRA_BASE}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", _auth_header())
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_issues(jql: str, fields: list[str],
                 verbose: bool = False) -> list[dict]:
    """Fetch issues from Jira REST API v3 with cursor pagination."""
    if verbose:
        print(f"  JQL: {jql}")

    all_issues = []
    next_token = None
    page_size = 50

    while True:
        body = {
            "jql": jql,
            "fields": fields,
            "maxResults": page_size,
        }
        if next_token:
            body["nextPageToken"] = next_token

        try:
            data = jira_post("/rest/api/3/search/jql", body)
        except urllib.error.HTTPError as e:
            resp_body = e.read().decode() if e.fp else ""
            sys.exit(f"Jira API error {e.code}: {resp_body[:500]}")

        issues = data.get("issues", [])
        all_issues.extend(issues)

        if verbose:
            print(f"  Fetched {len(all_issues)} issues so far")

        next_token = data.get("nextPageToken")
        if not next_token or not issues:
            break

    return all_issues


def fetch_changelogs(issue_keys: list[str],
                     verbose: bool = False) -> dict[str, list]:
    """Fetch changelog for each issue.

    Returns a dict mapping issue key -> list of changelog history entries.
    """
    changelogs = {}
    total = len(issue_keys)

    for i, key in enumerate(issue_keys, 1):
        histories = []
        start_at = 0

        while True:
            path = f"/rest/api/3/issue/{key}/changelog?startAt={start_at}&maxResults=100"
            try:
                data = jira_get(path)
            except urllib.error.HTTPError as e:
                if verbose:
                    print(f"  WARNING: changelog fetch failed for {key}: {e.code}")
                break

            values = data.get("values", [])
            histories.extend(values)

            if data.get("isLast", True) or not values:
                break
            start_at += len(values)

        changelogs[key] = histories

        if verbose and i % 20 == 0:
            print(f"  Changelogs: {i}/{total}")

    return changelogs
