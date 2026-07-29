"""Milestone loading and trigger-window logic for release-lifecycle rules."""

from datetime import date, timedelta
from pathlib import Path

import yaml


def load_milestones(milestones_path: Path) -> dict:
    """Load milestone config and build version-to-release lookup.

    Returns {
        "releases": { "3.6 EA1": { "versions": [...], "milestones": {...} } },
        "version_lookup": { "RHOAI 3.6": "3.6 EA1", ... }
    }
    """
    with open(milestones_path) as f:
        data = yaml.safe_load(f)
    releases = data.get("releases", {})
    lookup = {}
    for rel_key, rel_data in releases.items():
        for ver in rel_data.get("versions", []):
            lookup[ver] = rel_key
    return {"releases": releases, "version_lookup": lookup}


def trigger_active(rule: dict, milestones: dict, today: date) -> dict | None:
    """Check if an RL rule's trigger is active today.

    Returns context dict with matched release info, or None if not active.
    """
    trigger = rule.get("trigger")
    if not trigger:
        return None

    milestone_name = trigger.get("milestone", "")
    days_before = trigger.get("days_before")
    days_after = trigger.get("days_after")

    active_releases = []
    releases = milestones.get("releases", {})

    for rel_key, rel_data in releases.items():
        ms_dates = rel_data.get("milestones", {})
        ms_date_str = ms_dates.get(milestone_name)
        if not ms_date_str:
            continue
        ms_date = date.fromisoformat(ms_date_str)

        if days_before is not None:
            window_start = ms_date - timedelta(days=days_before)
            if window_start <= today <= ms_date:
                active_releases.append({
                    "release": rel_key,
                    "versions": rel_data.get("versions", []),
                    "milestone": milestone_name,
                    "milestone_date": ms_date_str,
                    "days_until": (ms_date - today).days,
                })

        if days_after is not None:
            if today >= ms_date:
                active_releases.append({
                    "release": rel_key,
                    "versions": rel_data.get("versions", []),
                    "milestone": milestone_name,
                    "milestone_date": ms_date_str,
                    "days_since": (today - ms_date).days,
                })

    if not active_releases:
        return None
    return {"active_releases": active_releases}
