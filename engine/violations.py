"""Violation building and message templating for release-radar."""

import re
from datetime import datetime, timezone

from .conditions import is_field_empty, days_since


def find_matched_link(issue: dict, rule: dict) -> dict | None:
    """For cross-issue rules, find the first linked issue that triggered the violation."""
    from .conditions import _check_linked_issue

    condition = rule.get("condition", {})
    if "has_outward_link" not in condition:
        return None

    verb = condition["has_outward_link"]
    links = issue.get("issue_links", []) or []
    matching_links = [link for link in links if link.get("verb") == verb]

    if "linked_issue" in condition:
        linked_spec = condition["linked_issue"]
        for link in matching_links:
            if _check_linked_issue(link, linked_spec):
                return link
    elif matching_links:
        return matching_links[0]
    return None


def build_violation(issue: dict, rule: dict,
                    release_ctx: dict | None = None,
                    matched_link: dict | None = None) -> dict:
    """Build a violation record with full provenance."""
    condition = rule.get("condition", {})

    message = rule.get("action", {}).get("message", "")
    if message:
        message = message.strip().replace("{key}", issue["key"])
        message = message.replace("{status}", issue["status"])

        if "{days}" in message and not release_ctx:
            changelog = issue.get("changelog") or {}
            last_change = changelog.get("last_status_change") or issue.get("created")
            days_val = days_since(last_change, datetime.now(timezone.utc))
            message = message.replace("{days}", str(days_val or "?"))

        tv = issue.get("target_version")
        fv = issue.get("fix_versions")
        message = message.replace(
            "{target_version}",
            ", ".join(tv) if isinstance(tv, list) else str(tv or "")
        )
        message = message.replace(
            "{fix_version}",
            ", ".join(fv) if isinstance(fv, list) else str(fv or "")
        )

        labels = issue.get("labels", [])
        matched_labels = [lbl for lbl in (labels or []) if any(
            re.search(p, lbl) for p in
            rule.get("condition", {}).get("label_matches", [])
        )]
        message = message.replace("{label}", ", ".join(matched_labels) if matched_labels else "")

        components = issue.get("components", [])
        message = message.replace("{component}", ", ".join(components) if components else "")
        parent_key = issue.get("parent_link", "")
        message = message.replace("{parent_key}", parent_key or "")
        parent_components = issue.get("parent_components", [])
        message = message.replace(
            "{parent_component}",
            ", ".join(parent_components) if parent_components else ""
        )

        if matched_link:
            message = message.replace("{linked_key}", matched_link.get("target_key", ""))
            message = message.replace("{linked_status}", matched_link.get("target_status", ""))
            assignee = matched_link.get("target_assignee", "Unassigned")
            note = f"assigned to {assignee}" if assignee != "Unassigned" else "unassigned"
            message = message.replace("{linked_assignee_note}", note)

        if "{missing_items}" in message and "any_missing" in condition:
            items = condition["any_missing"]
            labels = issue.get("labels", []) or []
            missing = []
            for item in items:
                if "label" in item and item["label"] not in labels:
                    missing.append(f"label:{item['label']}")
                elif "field" in item and is_field_empty(issue, item["field"]):
                    missing.append(item["field"])
            message = message.replace("{missing_items}", ", ".join(missing) if missing else "none")

        color_status = issue.get("color_status", "")
        message = message.replace("{color_status}", color_status or "")
        if "{mismatch_detail}" in message:
            summary = issue.get("status_summary") or ""
            if not summary:
                message = message.replace("{mismatch_detail}", "is empty (needs immediate update)")
            else:
                message = message.replace("{mismatch_detail}", f"text does not reference '{color_status}'")

        if release_ctx:
            ms_date = release_ctx.get("milestone_date", "")
            days = release_ctx.get("days_until", release_ctx.get("days_since", 0))
            message = message.replace("{milestone_date}", ms_date)
            message = message.replace("{days}", str(days))

    violation = {
        "issue_key": issue["key"],
        "issue_summary": issue["summary"],
        "issue_type": issue["issue_type"],
        "issue_status": issue["status"],
        "assignee": issue["assignee"],
        "project": issue["project"],
        "rule_id": rule["id"],
        "rule_name": rule.get("name", ""),
        "rule_file": rule.get("_file", ""),
        "severity": rule.get("severity", "medium"),
        "enforcement": rule.get("enforcement", "alert"),
        "scope": rule.get("scope", "team"),
        "verification": rule.get("verification", "deterministic"),
        "condition_field": condition.get("field_empty", condition.get("field_set", "")),
        "message": message,
        "sources": rule.get("sources", []),
        "detected_at": datetime.now(timezone.utc).isoformat(),
    }
    if release_ctx:
        violation["release"] = release_ctx.get("release", "")
        violation["milestone"] = release_ctx.get("milestone", "")
        violation["milestone_date"] = release_ctx.get("milestone_date", "")
    return violation
