"""Jira issue normalization for release-radar.

Converts raw Jira REST API responses into the flat snapshot format
consumed by the evaluation engine.
"""

# Jira custom field ID -> snapshot field name
CUSTOM_FIELDS = {
    "customfield_10028": "story_points",
    "customfield_10020": "sprint",
    "customfield_10464": "activity_type",
    "customfield_10469": "product_manager",
    "customfield_10470": "qa_contact",
    "customfield_10483": "blocked_reason",
    "customfield_10517": "blocked",
    "customfield_10638": "test_coverage",
    "customfield_10665": "docs_required",
    "customfield_10712": "color_status",
    "customfield_10783": "release_text",
    "customfield_10785": "release_note_type",
    "customfield_10807": "release_note",
    "customfield_10814": "status_summary",
    "customfield_10851": "release_type",
    "customfield_10855": "target_version",
    "customfield_10864": "rice_score",
    "customfield_10868": "products",
    "customfield_10875": "git_pull_request",
    "customfield_10023": "target_end",
    "customfield_10847": "release_blocker",
    "customfield_10849": "release_commit_exception",
}

JIRA_FIELDS = [
    "summary", "status", "issuetype", "assignee", "components",
    "fixVersions", "labels", "issuelinks", "parent", "created",
] + list(CUSTOM_FIELDS.keys())

# Changelog field name mapping for staleness tracking
_CHANGELOG_FIELD_MAP = {
    "Status Summary": "status_summary",
    "Color Status": "color_status",
    "status": "status",
    "Status": "status",
}


def _get_option_value(field_data):
    """Extract value from a Jira option/select field."""
    if isinstance(field_data, dict):
        return field_data.get("value")
    return field_data


def _get_user_display(field_data) -> str | None:
    """Extract display name from a user-picker field."""
    if isinstance(field_data, dict):
        return field_data.get("displayName")
    return None


def _get_adf_text(field_data) -> str | None:
    """Extract plain text from an ADF (Atlassian Document Format) field."""
    if not isinstance(field_data, dict):
        if isinstance(field_data, str):
            return field_data.strip() or None
        return None
    if field_data.get("type") == "doc":
        parts = []
        for block in field_data.get("content", []):
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    parts.append(inline.get("text", ""))
        text = " ".join(parts).strip()
        return text if text and text != "None" else None
    return None


def _get_multi_option(field_data) -> list:
    """Extract values from a multiselect option field."""
    if field_data is None:
        return []
    if isinstance(field_data, list):
        return [
            v.get("value", v) if isinstance(v, dict) else v
            for v in field_data
        ]
    if isinstance(field_data, dict):
        return [field_data.get("value", "")] if field_data.get("value") else []
    return [field_data] if field_data else []


def normalize_issue_links(raw_links) -> list[dict]:
    """Normalize Jira REST API issuelinks into a flat structured format."""
    if not raw_links or not isinstance(raw_links, list):
        return []

    normalized = []
    for link in raw_links:
        if not isinstance(link, dict):
            continue
        link_type = link.get("type", {})
        type_name = link_type.get("name", "")

        if "outwardIssue" in link:
            target = link["outwardIssue"]
            tf = target.get("fields", {}) or {}
            status = tf.get("status", {}) or {}
            normalized.append({
                "type": type_name,
                "direction": "outward",
                "verb": link_type.get("outward", ""),
                "target_key": target.get("key", ""),
                "target_status": status.get("name", ""),
                "target_status_category": (status.get("statusCategory") or {}).get("name", ""),
                "target_assignee": (tf.get("assignee") or {}).get("displayName", "Unassigned"),
            })

        if "inwardIssue" in link:
            target = link["inwardIssue"]
            tf = target.get("fields", {}) or {}
            status = tf.get("status", {}) or {}
            normalized.append({
                "type": type_name,
                "direction": "inward",
                "verb": link_type.get("inward", ""),
                "target_key": target.get("key", ""),
                "target_status": status.get("name", ""),
                "target_status_category": (status.get("statusCategory") or {}).get("name", ""),
                "target_assignee": (tf.get("assignee") or {}).get("displayName", "Unassigned"),
            })

    return normalized


def parse_changelog(raw: dict = None, histories: list | None = None) -> dict:
    """Extract temporal data from changelog history entries.

    Returns:
    {
        "last_status_change": ISO timestamp or None,
        "last_update": ISO timestamp or None,
        "field_history": {"status_summary": ISO timestamp, ...}
    }
    """
    if histories is None:
        raw = raw or {}
        changelog = raw.get("changelog", {})
        histories = changelog.get("histories", [])

    last_status_change = None
    last_update = None
    field_history: dict[str, str] = {}

    for entry in histories:
        created = entry.get("created", "")
        if not created:
            continue

        if last_update is None or created > last_update:
            last_update = created

        for item in entry.get("items", []):
            field_name = item.get("field", "")

            if field_name in ("status", "Status"):
                if last_status_change is None or created > last_status_change:
                    last_status_change = created

            mapped = _CHANGELOG_FIELD_MAP.get(field_name)
            if mapped:
                if mapped not in field_history or created > field_history[mapped]:
                    field_history[mapped] = created

    return {
        "last_status_change": last_status_change,
        "last_update": last_update,
        "field_history": field_history,
    }


def normalize_rest_issue(raw: dict, histories: list | None = None) -> dict:
    """Convert a Jira REST API issue to the evaluator snapshot format."""
    f = raw.get("fields", {})

    status = f.get("status", {})
    status_cat = status.get("statusCategory", {})
    issue_type = f.get("issuetype", {})
    assignee = f.get("assignee")

    fix_versions = [v.get("name", "") for v in (f.get("fixVersions") or [])]
    tv_raw = f.get("customfield_10855") or []
    target_version = [v.get("name", "") for v in tv_raw] if isinstance(tv_raw, list) else []

    components = [c.get("name", "") for c in (f.get("components") or [])]
    labels = f.get("labels") or []

    sprint_raw = f.get("customfield_10020")
    sprint = None
    if isinstance(sprint_raw, list):
        sprint = [
            {"name": s.get("name", ""), "state": s.get("state", "")}
            for s in sprint_raw if isinstance(s, dict)
        ]

    blocked_raw = _get_option_value(f.get("customfield_10517"))
    blocked = str(blocked_raw).lower() == "true" if blocked_raw else False

    parent = f.get("parent")
    parent_key = parent.get("key", "") if isinstance(parent, dict) else None

    issue_links = normalize_issue_links(f.get("issuelinks"))
    changelog_data = parse_changelog(raw, histories=histories)

    return {
        "key": raw.get("key", ""),
        "summary": f.get("summary", ""),
        "project": raw.get("key", "").split("-")[0],
        "status": status.get("name", ""),
        "status_category": status_cat.get("name", ""),
        "issue_type": issue_type.get("name", ""),
        "assignee": assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
        "components": components,
        "fix_versions": fix_versions,
        "target_version": target_version,
        "labels": labels,
        "team": None,
        "story_points": f.get("customfield_10028"),
        "activity_type": _get_option_value(f.get("customfield_10464")),
        "color_status": _get_option_value(f.get("customfield_10712")),
        "status_summary": _get_adf_text(f.get("customfield_10814")),
        "epic_link": None,
        "parent_link": parent_key,
        "sprint": sprint,
        "contributors": None,
        "rice_score": f.get("customfield_10864"),
        "target_end": f.get("customfield_10023"),
        "issue_links": issue_links,
        "qa_contact": _get_user_display(f.get("customfield_10470")),
        "product_manager": _get_user_display(f.get("customfield_10469")),
        "release_type": _get_option_value(f.get("customfield_10851")),
        "docs_required": _get_option_value(f.get("customfield_10665")),
        "blocked": blocked,
        "blocked_reason": _get_adf_text(f.get("customfield_10483")),
        "git_pull_request": _get_adf_text(f.get("customfield_10875")),
        "test_coverage": _get_multi_option(f.get("customfield_10638")),
        "products": _get_multi_option(f.get("customfield_10868")),
        "release_note": _get_option_value(f.get("customfield_10807")),
        "release_note_type": _get_option_value(f.get("customfield_10785")),
        "release_text": _get_adf_text(f.get("customfield_10783")),
        "release_blocker": _get_option_value(f.get("customfield_10847")),
        "release_commit_exception": _get_option_value(f.get("customfield_10849")),
        "created": f.get("created"),
        "changelog": changelog_data,
    }


def enrich_parent_components(issues: list[dict]):
    """Add parent_components using a key->components lookup within the snapshot."""
    key_to_components = {iss["key"]: iss["components"] for iss in issues}
    for issue in issues:
        parent_key = issue.get("parent_link")
        if parent_key and parent_key in key_to_components:
            issue["parent_components"] = key_to_components[parent_key]
        else:
            issue["parent_components"] = None
