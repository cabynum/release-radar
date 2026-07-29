"""Condition evaluation logic for release-radar rules.

Each public function evaluates one condition type against a normalized issue.
The main entry point is `matches_condition()` which AND-gates all conditions
in a rule's condition block.
"""

import re
from datetime import datetime, timezone

# Rule field names -> snapshot field names
FIELD_ALIASES = {
    "assignee": "assignee",
    "team": "team",
    "component": "components",
    "story_points": "story_points",
    "activity_type": "activity_type",
    "status_summary": "status_summary",
    "color_status": "color_status",
    "epic_link": "epic_link",
    "parent_link": "parent_link",
    "target_version": "target_version",
    "fix_version": "fix_versions",
    "contributors": "contributors",
    "rice_score": "rice_score",
    "target_end": "target_end",
    "sprint": "sprint",
    "issue_links": "issue_links",
    "labels": "labels",
    "refinement_doc": "_EXTERNAL",
    "signoff_template": "_EXTERNAL",
    "release_type": "release_type",
    "product_manager": "product_manager",
    "products": "products",
    "docs_required": "docs_required",
    "git_pull_request": "git_pull_request",
    "blocked": "blocked",
    "blocked_reason": "blocked_reason",
    "release_blocker": "release_blocker",
    "release_note": "release_note",
    "release_note_type": "release_note_type",
    "release_text": "release_text",
    "test_coverage": "test_coverage",
    "qa_contact": "qa_contact",
}

# Fields not included in the snapshot. Rules referencing these are skipped.
UNFETCHED_FIELDS: set[str] = set()

# Versions exempt from RICE scoring requirement (pre-existing features).
_GRANDFATHERED_VERSIONS = {
    "rhoai-3.3", "rhoai-3.4-ea1",
    "3.3 GA RHOAI RELEASE", "3.4 EA1 RHOAI RELEASE",
}

# Jira keys for signoff templates (DP/TP/GA).
_SIGNOFF_TEMPLATE_KEYS = {"RHOAIENG-31244", "RHOAIENG-31290", "RHOAIENG-31303"}

KNOWN_CONDITION_KEYS = {
    "status", "status_category", "field_empty", "field_set",
    "in_active_sprint", "field_value", "field_not_value", "any_of", "project",
    "label_matches", "versions_differ",
    "fix_version_matches_release", "target_version_matches_release",
    "status_not", "label_missing", "priority",
    "no_clones_link_to", "has_outward_link", "linked_issue",
    "has_parent", "component_differs_from_parent",
    "component_matches", "any_missing", "status_summary_color_mismatch",
    "color_status",
    "days_in_status", "no_recent_update", "field_stale_days",
    "status_changed_after", "created_after",
    "updated_before_days", "not_grandfathered",
    "no_linked_signoff_template",
    "no_refinement_doc_in_drive", "no_doc_draft_linked",
    "no_signoff_complete",
    "pr_merged_to_release_branch", "no_jira_key_in_pr",
}

UNSUPPORTED_CONDITION_KEYS: set[str] = set()

# Module-level context for milestone date during RL rule evaluation.
milestone_date_context = [None]


# --- Temporal helpers ---

def parse_iso_date(ts: str | None) -> datetime | None:
    """Parse a Jira ISO timestamp to a timezone-aware datetime."""
    if not ts:
        return None
    ts = ts.strip()
    try:
        if "T" in ts:
            ts = ts.replace("Z", "+00:00")
            if "+" in ts[10:] and ":" not in ts.rsplit("+", 1)[-1]:
                offset = ts.rsplit("+", 1)[-1]
                ts = ts.rsplit("+", 1)[0] + "+" + offset[:2] + ":" + offset[2:]
            elif "-" in ts[10:] and ts[-5] == "-" and ":" not in ts[-4:]:
                offset = ts[-4:]
                ts = ts[:-5] + "-" + offset[:2] + ":" + offset[2:]
            if "." in ts:
                base, frac_and_tz = ts.split(".", 1)
                frac = ""
                tz_part = ""
                for i, ch in enumerate(frac_and_tz):
                    if ch in ("+", "-") or (ch == "Z"):
                        frac = frac_and_tz[:i]
                        tz_part = frac_and_tz[i:]
                        break
                else:
                    frac = frac_and_tz
                ts = base + "." + frac[:6] + tz_part
            return datetime.fromisoformat(ts)
        return datetime.fromisoformat(ts + "T00:00:00+00:00")
    except (ValueError, TypeError):
        return None


def days_since(ts: str | None, ref: datetime) -> int | None:
    """Calculate days between a timestamp and a reference datetime."""
    dt = parse_iso_date(ts)
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    return (ref - dt).days


# --- Field checks ---

def is_field_empty(issue: dict, field_name: str) -> bool:
    """Check if a field is effectively empty in the normalized snapshot."""
    snapshot_key = FIELD_ALIASES.get(field_name, field_name)
    if snapshot_key == "_EXTERNAL":
        return False
    value = issue.get(snapshot_key)
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in ("", "Unassigned", "Not Selected", "None"):
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


def is_field_set(issue: dict, field_name: str) -> bool:
    return not is_field_empty(issue, field_name)


def check_field_value(issue: dict, spec: dict) -> bool:
    """Check field_value: {field: X, value: Y}. True if field == value."""
    field = spec.get("field", "")
    expected = spec.get("value")
    snapshot_key = FIELD_ALIASES.get(field, field)
    if snapshot_key == "_EXTERNAL":
        return False
    actual = issue.get(snapshot_key)
    if isinstance(expected, bool):
        return bool(actual) == expected
    if actual is None:
        return expected is None
    return str(actual).lower() == str(expected).lower()


# --- Link checks ---

def _check_linked_issue(link: dict, spec: dict) -> bool:
    """Check if a linked issue matches a linked_issue spec."""
    if "status_category_not" in spec:
        excluded = spec["status_category_not"]
        if isinstance(excluded, str):
            excluded = [excluded]
        if link.get("target_status_category", "") in excluded:
            return False

    if "any_of" in spec:
        for sub in spec["any_of"]:
            if _check_linked_issue_sub(link, sub):
                return True
        return False
    return _check_linked_issue_sub(link, spec)


def _check_linked_issue_sub(link: dict, sub: dict) -> bool:
    """Evaluate a single sub-condition against linked issue data."""
    if "status" in sub:
        allowed = sub["status"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if link.get("target_status", "") not in allowed:
            return False
    if "field_empty" in sub:
        field = sub["field_empty"]
        if field == "assignee":
            assignee = link.get("target_assignee", "")
            if assignee and assignee != "Unassigned":
                return False
        else:
            return False
    return True


# --- Sub-condition (any_of) ---

def check_sub_condition(issue: dict, sub: dict) -> bool:
    """Evaluate a single sub-condition dict (used inside any_of)."""
    for key, val in sub.items():
        if key == "field_empty":
            if not is_field_empty(issue, val):
                return False
        elif key == "field_set":
            if not is_field_set(issue, val):
                return False
        elif key == "status":
            if issue["status"] not in (val if isinstance(val, list) else [val]):
                return False
        elif key == "field_value":
            if not check_field_value(issue, val):
                return False
        elif key == "color_status":
            actual = (issue.get("color_status") or "")
            if actual.lower() != str(val).lower():
                return False
        elif key == "status_summary_color_mismatch" and val:
            color_status = (issue.get("color_status") or "").lower()
            summary = (issue.get("status_summary") or "").lower()
            if not color_status or not summary:
                return False
            color_words = {"green", "yellow", "red"}
            summary_colors = {w for w in color_words if w in summary}
            if color_status in summary_colors:
                return False
        elif key == "field_stale_days":
            field = val.get("field", "")
            threshold = val.get("threshold", 7)
            changelog = issue.get("changelog") or {}
            field_history = changelog.get("field_history", {})
            snapshot_key = FIELD_ALIASES.get(field, field)
            last_modified = field_history.get(snapshot_key)
            if last_modified is None:
                return False
            now = datetime.now(timezone.utc)
            d = days_since(last_modified, now)
            if d is None or d < threshold:
                return False
        elif key in UNSUPPORTED_CONDITION_KEYS:
            return False
        elif key not in KNOWN_CONDITION_KEYS:
            return False
    return True


# --- Version helpers ---

def _version_matches_release(issue_versions: list, release_versions: list) -> bool:
    if not issue_versions or not release_versions:
        return False
    issue_set = set(issue_versions) if isinstance(issue_versions, list) else {issue_versions}
    return bool(issue_set & set(release_versions))


# --- Main condition evaluation ---

def matches_condition(issue: dict, rule: dict,
                      release_versions: list[str] | None = None) -> bool:
    """Check if an issue matches a rule's condition block.

    All top-level condition keys are AND-ed together.
    """
    condition = rule.get("condition", {})

    for key in condition:
        if key not in KNOWN_CONDITION_KEYS and key not in UNSUPPORTED_CONDITION_KEYS:
            return False
        if key in UNSUPPORTED_CONDITION_KEYS:
            return False

    if "status" in condition:
        allowed = condition["status"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if issue["status"] not in allowed:
            return False

    if "status_not" in condition:
        excluded = condition["status_not"]
        if isinstance(excluded, str):
            excluded = [excluded]
        if issue["status"] in excluded:
            return False

    if "status_category" in condition:
        allowed = condition["status_category"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if issue["status_category"] not in allowed:
            return False

    if "project" in condition:
        allowed = condition["project"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if issue["project"] not in allowed:
            return False

    if "priority" in condition:
        allowed = condition["priority"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if issue.get("priority", "") not in allowed:
            return False

    if "field_empty" in condition:
        if not is_field_empty(issue, condition["field_empty"]):
            return False

    if "field_set" in condition:
        if not is_field_set(issue, condition["field_set"]):
            return False

    if "field_value" in condition:
        if not check_field_value(issue, condition["field_value"]):
            return False

    if "field_not_value" in condition:
        if check_field_value(issue, condition["field_not_value"]):
            return False

    if "fix_version_matches_release" in condition and condition["fix_version_matches_release"]:
        if not release_versions:
            return False
        fv = issue.get("fix_versions", [])
        fv_list = fv if isinstance(fv, list) else ([fv] if fv else [])
        if not _version_matches_release(fv_list, release_versions):
            return False

    if "target_version_matches_release" in condition and condition["target_version_matches_release"]:
        if not release_versions:
            return False
        tv = issue.get("target_version", [])
        tv_list = tv if isinstance(tv, list) else ([tv] if tv else [])
        if not _version_matches_release(tv_list, release_versions):
            return False

    if "label_missing" in condition:
        required = condition["label_missing"]
        if isinstance(required, str):
            required = [required]
        labels = issue.get("labels", []) or []
        for req_label in required:
            if any(req_label == lbl for lbl in labels):
                return False

    if "in_active_sprint" in condition:
        sprint_data = issue.get("sprint")
        has_active = False
        if isinstance(sprint_data, list):
            has_active = any(
                s.get("state") == "active"
                for s in sprint_data if isinstance(s, dict)
            )
        if has_active != condition["in_active_sprint"]:
            return False

    if "label_matches" in condition:
        patterns = condition["label_matches"]
        if isinstance(patterns, str):
            patterns = [patterns]
        labels = issue.get("labels", []) or []
        if not any(re.search(pat, lbl) for pat in patterns for lbl in labels):
            return False

    if "versions_differ" in condition and condition["versions_differ"]:
        tv = issue.get("target_version")
        fv = issue.get("fix_versions")
        tv_list = tv if isinstance(tv, list) else ([tv] if tv else [])
        fv_list = fv if isinstance(fv, list) else ([fv] if fv else [])
        if not tv_list or not fv_list:
            return False
        if set(tv_list) == set(fv_list):
            return False

    if "component_matches" in condition:
        patterns = condition["component_matches"]
        if isinstance(patterns, str):
            patterns = [patterns]
        components = issue.get("components", []) or []
        if not any(pat.lower() in comp.lower() for pat in patterns for comp in components):
            return False

    if "any_missing" in condition:
        items = condition["any_missing"]
        labels = issue.get("labels", []) or []
        has_missing = False
        for item in items:
            if "label" in item:
                if item["label"] not in labels:
                    has_missing = True
                    break
            elif "field" in item:
                if is_field_empty(issue, item["field"]):
                    has_missing = True
                    break
        if not has_missing:
            return False

    if "color_status" in condition:
        expected = condition["color_status"]
        actual = issue.get("color_status", "")
        if str(actual).lower() != str(expected).lower():
            return False

    if "status_summary_color_mismatch" in condition and condition["status_summary_color_mismatch"]:
        color_status = (issue.get("color_status") or "").lower()
        summary = (issue.get("status_summary") or "").lower()
        if not color_status or not summary:
            return False
        color_words = {"green", "yellow", "red"}
        summary_colors = {w for w in color_words if w in summary}
        if color_status in summary_colors:
            return False

    if "any_of" in condition:
        subs = condition["any_of"]
        if not any(check_sub_condition(issue, sub) for sub in subs):
            return False

    # --- Changelog/staleness conditions ---

    now = datetime.now(timezone.utc)
    changelog = issue.get("changelog") or {}

    if "days_in_status" in condition:
        threshold = condition["days_in_status"]
        last_change = changelog.get("last_status_change")
        if last_change is None:
            last_change = issue.get("created")
        d = days_since(last_change, now)
        if d is None or d < threshold:
            return False

    if "no_recent_update" in condition and condition["no_recent_update"]:
        threshold = condition.get("days_in_status", 14)
        last_update = changelog.get("last_update")
        if last_update is None:
            last_update = issue.get("created")
        d = days_since(last_update, now)
        if d is None or d < threshold:
            return False

    if "status_changed_after" in condition:
        last_change = changelog.get("last_status_change")
        if last_change is None:
            return False
        ms_date = milestone_date_context[0]
        if ms_date is None:
            return False
        change_dt = parse_iso_date(last_change)
        if change_dt is None:
            return False
        ms_dt = datetime.fromisoformat(ms_date + "T00:00:00+00:00")
        if change_dt <= ms_dt:
            return False

    if "created_after" in condition:
        created = issue.get("created")
        if created is None:
            return False
        ms_date = milestone_date_context[0]
        if ms_date is None:
            return False
        created_dt = parse_iso_date(created)
        if created_dt is None:
            return False
        ms_dt = datetime.fromisoformat(ms_date + "T00:00:00+00:00")
        if created_dt <= ms_dt:
            return False

    # --- Cross-issue lookup conditions ---

    if "no_clones_link_to" in condition:
        pattern = condition["no_clones_link_to"]
        links = issue.get("issue_links", []) or []
        has_clone = any(
            link.get("verb") == "clones"
            and re.match(pattern.replace("*", ".*"), link.get("target_key", ""))
            for link in links
        )
        if has_clone:
            return False

    if "has_outward_link" in condition:
        verb = condition["has_outward_link"]
        links = issue.get("issue_links", []) or []
        matching_links = [link for link in links if link.get("verb") == verb]
        if not matching_links:
            return False
        if "linked_issue" in condition:
            linked_spec = condition["linked_issue"]
            if not any(_check_linked_issue(link, linked_spec) for link in matching_links):
                return False
    elif "linked_issue" in condition:
        return False

    if "has_parent" in condition and condition["has_parent"]:
        if not issue.get("parent_link"):
            return False

    if "component_differs_from_parent" in condition and condition["component_differs_from_parent"]:
        parent_components = issue.get("parent_components")
        if parent_components is None:
            return False
        issue_components = set(issue.get("components", []))
        parent_set = set(parent_components)
        if not issue_components or not parent_set:
            return False
        if issue_components == parent_set:
            return False

    # --- Temporal: issue age check ---

    if "updated_before_days" in condition:
        threshold = condition["updated_before_days"]
        created = issue.get("created")
        d = days_since(created, now)
        if d is None or d < threshold:
            return False

    # --- Version grandfathering ---

    if "not_grandfathered" in condition and condition["not_grandfathered"]:
        grandfathered = _GRANDFATHERED_VERSIONS
        tv = issue.get("target_version") or []
        fv = issue.get("fix_versions") or []
        all_versions = set(tv if isinstance(tv, list) else [tv]) | set(fv if isinstance(fv, list) else [fv])
        all_versions.discard("")
        if all_versions and all_versions <= grandfathered:
            return False

    # --- Signoff template link check ---

    if "no_linked_signoff_template" in condition and condition["no_linked_signoff_template"]:
        links = issue.get("issue_links", []) or []
        has_template = any(
            link.get("verb") == "clones"
            and link.get("target_key", "") in _SIGNOFF_TEMPLATE_KEYS
            for link in links
        )
        if has_template:
            return False

    # --- External integration conditions ---

    if "no_refinement_doc_in_drive" in condition and condition["no_refinement_doc_in_drive"]:
        if not issue.get("_refinement_doc_missing"):
            return False

    if "no_doc_draft_linked" in condition and condition["no_doc_draft_linked"]:
        if not issue.get("_doc_draft_missing"):
            return False

    if "no_signoff_complete" in condition and condition["no_signoff_complete"]:
        if not issue.get("_signoff_incomplete"):
            return False

    if "pr_merged_to_release_branch" in condition and condition["pr_merged_to_release_branch"]:
        if not issue.get("_pr_merged_post_freeze"):
            return False

    if "no_jira_key_in_pr" in condition and condition["no_jira_key_in_pr"]:
        if not issue.get("_pr_missing_jira_key"):
            return False

    return True


# --- Preflight ---

def preflight_check(rule: dict) -> str | None:
    """Check if a rule can be evaluated. Returns skip reason or None."""
    condition = rule.get("condition", {})

    for field_key in ("field_empty", "field_set"):
        field_name = condition.get(field_key, "")
        if field_name:
            snapshot_key = FIELD_ALIASES.get(field_name, field_name)
            if snapshot_key == "_EXTERNAL":
                return f"external check: {field_name}"
            if field_name in UNFETCHED_FIELDS:
                return f"field not in snapshot: {field_name}"

    if "field_value" in condition:
        fv_field = condition["field_value"].get("field", "")
        if fv_field in UNFETCHED_FIELDS:
            return f"field not in snapshot: {fv_field}"

    if "field_not_value" in condition:
        fnv_field = condition["field_not_value"].get("field", "")
        if fnv_field in UNFETCHED_FIELDS:
            return f"field not in snapshot: {fnv_field}"

    if "any_of" in condition:
        for sub in condition["any_of"]:
            for sub_key in ("field_empty", "field_set"):
                sub_field = sub.get(sub_key, "")
                if sub_field and sub_field in UNFETCHED_FIELDS:
                    return f"field not in snapshot: {sub_field}"
            if "field_value" in sub:
                fv_field = sub["field_value"].get("field", "")
                if fv_field in UNFETCHED_FIELDS:
                    return f"field not in snapshot: {fv_field}"

    for key in condition:
        if key in UNSUPPORTED_CONDITION_KEYS:
            return f"unsupported condition: {key}"
        if key not in KNOWN_CONDITION_KEYS:
            return f"unknown condition: {key}"

    if "any_of" in condition:
        for sub in condition["any_of"]:
            for key in sub:
                if key in UNSUPPORTED_CONDITION_KEYS:
                    return f"unsupported condition in any_of: {key}"
                if key not in KNOWN_CONDITION_KEYS:
                    return f"unknown condition in any_of: {key}"

    return None
