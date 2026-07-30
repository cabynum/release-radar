"""Unit tests for release-radar condition evaluation logic."""

from datetime import datetime, timezone, timedelta

import pytest

from engine.conditions import (
    is_field_empty,
    is_field_set,
    check_field_value,
    check_sub_condition,
    matches_condition,
    parse_iso_date,
    days_since,
    milestone_date_context,
)


# --- Fixtures ---

def _make_issue(**overrides) -> dict:
    """Create a minimal normalized issue with sensible defaults."""
    issue = {
        "key": "RHAIENG-100",
        "summary": "Test issue",
        "project": "RHAIENG",
        "status": "In Progress",
        "status_category": "In Progress",
        "issue_type": "Story",
        "assignee": "Jane Doe",
        "components": ["Data Processing"],
        "fix_versions": [],
        "target_version": [],
        "labels": [],
        "team": "DP",
        "story_points": 5,
        "activity_type": "New Feature",
        "color_status": "Green",
        "status_summary": "Green as of 2026-07-28. On track.",
        "epic_link": None,
        "parent_link": None,
        "sprint": [{"name": "Sprint 42", "state": "active"}],
        "contributors": None,
        "rice_score": 100,
        "target_end": "2026-08-15",
        "issue_links": [],
        "qa_contact": "QA Person",
        "product_manager": "PM Person",
        "release_type": "Major",
        "docs_required": "Yes",
        "blocked": False,
        "blocked_reason": None,
        "git_pull_request": None,
        "test_coverage": ["Unit", "Integration"],
        "products": ["RHOAI"],
        "release_note": "Done",
        "release_note_type": "Feature",
        "release_text": "Added data processing support.",
        "created": "2026-01-15T10:00:00.000+0000",
        "changelog": {
            "last_status_change": "2026-07-01T12:00:00.000+0000",
            "last_update": "2026-07-25T09:00:00.000+0000",
            "field_history": {
                "status_summary": "2026-07-25T09:00:00.000+0000",
                "status": "2026-07-01T12:00:00.000+0000",
            },
        },
    }
    issue.update(overrides)
    return issue


def _make_rule(condition: dict, **overrides) -> dict:
    """Create a minimal rule dict for condition testing."""
    rule = {
        "id": "test-rule",
        "name": "Test Rule",
        "applies_to": ["Story", "Task", "Bug", "Epic", "Feature", "Spike"],
        "condition": condition,
        "action": {"type": "alert", "message": "test"},
        "severity": "medium",
    }
    rule.update(overrides)
    return rule


# --- _is_field_empty / _is_field_set ---

class TestFieldEmpty:
    def test_none_is_empty(self):
        issue = _make_issue(assignee=None)
        assert is_field_empty(issue, "assignee") is True

    def test_unassigned_is_empty(self):
        issue = _make_issue(assignee="Unassigned")
        assert is_field_empty(issue, "assignee") is True

    def test_empty_string_is_empty(self):
        issue = _make_issue(status_summary="")
        assert is_field_empty(issue, "status_summary") is True

    def test_empty_list_is_empty(self):
        issue = _make_issue(components=[])
        assert is_field_empty(issue, "component") is True

    def test_populated_string_not_empty(self):
        issue = _make_issue(assignee="Jane Doe")
        assert is_field_empty(issue, "assignee") is False

    def test_populated_list_not_empty(self):
        issue = _make_issue(components=["Data Processing"])
        assert is_field_empty(issue, "component") is False

    def test_external_field_never_empty(self):
        issue = _make_issue()
        assert is_field_empty(issue, "signoff_template") is False

    def test_field_set_inverse(self):
        issue = _make_issue(story_points=5)
        assert is_field_set(issue, "story_points") is True
        issue2 = _make_issue(story_points=None)
        assert is_field_set(issue2, "story_points") is False


# --- check_field_value ---

class TestFieldValue:
    def test_string_match_case_insensitive(self):
        issue = _make_issue(color_status="Green")
        assert check_field_value(issue, {"field": "color_status", "value": "green"}) is True

    def test_string_mismatch(self):
        issue = _make_issue(color_status="Red")
        assert check_field_value(issue, {"field": "color_status", "value": "green"}) is False

    def test_bool_match(self):
        issue = _make_issue(blocked=True)
        assert check_field_value(issue, {"field": "blocked", "value": True}) is True

    def test_bool_mismatch(self):
        issue = _make_issue(blocked=False)
        assert check_field_value(issue, {"field": "blocked", "value": True}) is False

    def test_none_matches_none(self):
        issue = _make_issue(blocked_reason=None)
        assert check_field_value(issue, {"field": "blocked_reason", "value": None}) is True

    def test_external_field_returns_false(self):
        issue = _make_issue()
        assert check_field_value(issue, {"field": "signoff_template", "value": "yes"}) is False


# --- Status conditions ---

class TestStatusConditions:
    def test_status_match(self):
        issue = _make_issue(status="In Progress")
        rule = _make_rule({"status": ["In Progress"]})
        assert matches_condition(issue, rule) is True

    def test_status_no_match(self):
        issue = _make_issue(status="Backlog")
        rule = _make_rule({"status": ["In Progress", "Review"]})
        assert matches_condition(issue, rule) is False

    def test_status_not_excluded(self):
        issue = _make_issue(status="Done")
        rule = _make_rule({"status_not": ["Done", "Closed"]})
        assert matches_condition(issue, rule) is False

    def test_status_not_passes(self):
        issue = _make_issue(status="In Progress")
        rule = _make_rule({"status_not": ["Done", "Closed"]})
        assert matches_condition(issue, rule) is True

    def test_status_category(self):
        issue = _make_issue(status_category="In Progress")
        rule = _make_rule({"status_category": ["In Progress"]})
        assert matches_condition(issue, rule) is True


# --- Sprint conditions ---

class TestSprintConditions:
    def test_in_active_sprint_true(self):
        issue = _make_issue(sprint=[{"name": "Sprint 42", "state": "active"}])
        rule = _make_rule({"in_active_sprint": True})
        assert matches_condition(issue, rule) is True

    def test_in_active_sprint_false(self):
        issue = _make_issue(sprint=[{"name": "Sprint 41", "state": "closed"}])
        rule = _make_rule({"in_active_sprint": True})
        assert matches_condition(issue, rule) is False

    def test_not_in_active_sprint(self):
        issue = _make_issue(sprint=None)
        rule = _make_rule({"in_active_sprint": False})
        assert matches_condition(issue, rule) is True


# --- Label conditions ---

class TestLabelConditions:
    def test_label_matches_regex(self):
        issue = _make_issue(labels=["qe-verified", "sprint-42"])
        rule = _make_rule({"label_matches": ["^qe-"]})
        assert matches_condition(issue, rule) is True

    def test_label_matches_no_hit(self):
        issue = _make_issue(labels=["sprint-42"])
        rule = _make_rule({"label_matches": ["^qe-"]})
        assert matches_condition(issue, rule) is False

    def test_label_missing_present(self):
        issue = _make_issue(labels=["qe-verified"])
        rule = _make_rule({"label_missing": ["qe-verified"]})
        assert matches_condition(issue, rule) is False

    def test_label_missing_absent(self):
        issue = _make_issue(labels=["sprint-42"])
        rule = _make_rule({"label_missing": ["qe-verified"]})
        assert matches_condition(issue, rule) is True


# --- Version conditions ---

class TestVersionConditions:
    def test_versions_differ(self):
        issue = _make_issue(target_version=["3.5 GA"], fix_versions=["3.6 GA"])
        rule = _make_rule({"versions_differ": True})
        assert matches_condition(issue, rule) is True

    def test_versions_same(self):
        issue = _make_issue(target_version=["3.5 GA"], fix_versions=["3.5 GA"])
        rule = _make_rule({"versions_differ": True})
        assert matches_condition(issue, rule) is False

    def test_fix_version_matches_release(self):
        issue = _make_issue(fix_versions=["3.5 GA RHOAI RELEASE"])
        rule = _make_rule({"fix_version_matches_release": True})
        assert matches_condition(
            issue, rule,
            release_versions=["3.5 GA RHOAI RELEASE", "rhoai-3.5"]
        ) is True

    def test_fix_version_no_match(self):
        issue = _make_issue(fix_versions=["3.6 GA RHOAI RELEASE"])
        rule = _make_rule({"fix_version_matches_release": True})
        assert matches_condition(
            issue, rule,
            release_versions=["3.5 GA RHOAI RELEASE"]
        ) is False

    def test_target_version_matches_release(self):
        issue = _make_issue(target_version=["rhoai-3.5"])
        rule = _make_rule({"target_version_matches_release": True})
        assert matches_condition(
            issue, rule,
            release_versions=["3.5 GA RHOAI RELEASE", "rhoai-3.5"]
        ) is True


# --- Component conditions ---

class TestComponentConditions:
    def test_component_matches(self):
        issue = _make_issue(components=["Data Processing"])
        rule = _make_rule({"component_matches": ["data processing"]})
        assert matches_condition(issue, rule) is True

    def test_component_no_match(self):
        issue = _make_issue(components=["Model Serving"])
        rule = _make_rule({"component_matches": ["data processing"]})
        assert matches_condition(issue, rule) is False

    def test_component_differs_from_parent(self):
        issue = _make_issue(
            parent_link="RHAIENG-50",
            components=["Data Processing"],
            parent_components=["Model Serving"],
        )
        rule = _make_rule({"has_parent": True, "component_differs_from_parent": True})
        assert matches_condition(issue, rule) is True

    def test_component_same_as_parent(self):
        issue = _make_issue(
            parent_link="RHAIENG-50",
            components=["Data Processing"],
            parent_components=["Data Processing"],
        )
        rule = _make_rule({"has_parent": True, "component_differs_from_parent": True})
        assert matches_condition(issue, rule) is False

    def test_parent_not_in_snapshot_skips(self):
        issue = _make_issue(
            parent_link="RHAIENG-50",
            components=["Data Processing"],
            parent_components=None,
        )
        rule = _make_rule({"has_parent": True, "component_differs_from_parent": True})
        assert matches_condition(issue, rule) is False


# --- Cross-issue link conditions ---

class TestLinkConditions:
    def test_no_clones_link_fires_when_absent(self):
        issue = _make_issue(issue_links=[])
        rule = _make_rule({"no_clones_link_to": "RHAIRFE-*"})
        assert matches_condition(issue, rule) is True

    def test_no_clones_link_suppressed_when_present(self):
        issue = _make_issue(issue_links=[
            {"type": "Cloners", "direction": "outward", "verb": "clones",
             "target_key": "RHAIRFE-500", "target_status": "Approved",
             "target_status_category": "Done", "target_assignee": "PM"},
        ])
        rule = _make_rule({"no_clones_link_to": "RHAIRFE-*"})
        assert matches_condition(issue, rule) is False

    def test_has_outward_link_with_linked_issue_check(self):
        issue = _make_issue(issue_links=[
            {"type": "Blocks", "direction": "outward", "verb": "blocks",
             "target_key": "RHAIENG-200", "target_status": "In Progress",
             "target_status_category": "In Progress", "target_assignee": "Unassigned"},
        ])
        rule = _make_rule({
            "has_outward_link": "blocks",
            "linked_issue": {
                "status_category_not": "Done",
                "any_of": [{"field_empty": "assignee"}],
            },
        })
        assert matches_condition(issue, rule) is True

    def test_linked_issue_done_excluded(self):
        issue = _make_issue(issue_links=[
            {"type": "Blocks", "direction": "outward", "verb": "blocks",
             "target_key": "RHAIENG-200", "target_status": "Closed",
             "target_status_category": "Done", "target_assignee": "Unassigned"},
        ])
        rule = _make_rule({
            "has_outward_link": "blocks",
            "linked_issue": {"status_category_not": "Done"},
        })
        assert matches_condition(issue, rule) is False


# --- any_of (OR logic) ---

class TestAnyOf:
    def test_any_of_first_sub_matches(self):
        issue = _make_issue(status_summary=None)
        rule = _make_rule({
            "status": ["In Progress"],
            "any_of": [
                {"field_empty": "status_summary"},
                {"field_empty": "color_status"},
            ],
        })
        assert matches_condition(issue, rule) is True

    def test_any_of_second_sub_matches(self):
        issue = _make_issue(color_status=None)
        rule = _make_rule({
            "status": ["In Progress"],
            "any_of": [
                {"field_empty": "status_summary"},
                {"field_empty": "color_status"},
            ],
        })
        assert matches_condition(issue, rule) is True

    def test_any_of_none_match(self):
        issue = _make_issue(status_summary="text", color_status="Green")
        rule = _make_rule({
            "status": ["In Progress"],
            "any_of": [
                {"field_empty": "status_summary"},
                {"field_empty": "color_status"},
            ],
        })
        assert matches_condition(issue, rule) is False


# --- any_missing ---

class TestAnyMissing:
    def test_missing_label(self):
        issue = _make_issue(labels=["sprint-42"])
        rule = _make_rule({"any_missing": [{"label": "qe-verified"}, {"field": "qa_contact"}]})
        assert matches_condition(issue, rule) is True

    def test_missing_field(self):
        issue = _make_issue(labels=["qe-verified"], qa_contact=None)
        rule = _make_rule({"any_missing": [{"label": "qe-verified"}, {"field": "qa_contact"}]})
        assert matches_condition(issue, rule) is True

    def test_nothing_missing(self):
        issue = _make_issue(labels=["qe-verified"], qa_contact="QA Person")
        rule = _make_rule({"any_missing": [{"label": "qe-verified"}, {"field": "qa_contact"}]})
        assert matches_condition(issue, rule) is False


# --- Color/status summary mismatch ---

class TestColorMismatch:
    def test_mismatch_detected(self):
        issue = _make_issue(color_status="Red", status_summary="Green as of today.")
        rule = _make_rule({"status_summary_color_mismatch": True})
        assert matches_condition(issue, rule) is True

    def test_matching_colors(self):
        issue = _make_issue(color_status="Green", status_summary="Green as of today.")
        rule = _make_rule({"status_summary_color_mismatch": True})
        assert matches_condition(issue, rule) is False

    def test_empty_summary_no_match(self):
        issue = _make_issue(color_status="Green", status_summary=None)
        rule = _make_rule({"status_summary_color_mismatch": True})
        assert matches_condition(issue, rule) is False


# --- Changelog/staleness conditions ---

class TestDaysInStatus:
    def test_stale_issue(self):
        old_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        issue = _make_issue(
            status="In Progress",
            changelog={"last_status_change": old_date, "last_update": old_date, "field_history": {}},
        )
        rule = _make_rule({"status": ["In Progress"], "days_in_status": 21})
        assert matches_condition(issue, rule) is True

    def test_fresh_issue(self):
        recent_date = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        issue = _make_issue(
            status="In Progress",
            changelog={"last_status_change": recent_date, "last_update": recent_date, "field_history": {}},
        )
        rule = _make_rule({"status": ["In Progress"], "days_in_status": 21})
        assert matches_condition(issue, rule) is False

    def test_fallback_to_created_when_no_changelog(self):
        old_created = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        issue = _make_issue(
            status="In Progress",
            changelog={"last_status_change": None, "last_update": None, "field_history": {}},
            created=old_created,
        )
        rule = _make_rule({"status": ["In Progress"], "days_in_status": 21})
        assert matches_condition(issue, rule) is True

    def test_no_data_at_all_skips(self):
        issue = _make_issue(
            status="In Progress",
            changelog={"last_status_change": None, "last_update": None, "field_history": {}},
            created=None,
        )
        rule = _make_rule({"status": ["In Progress"], "days_in_status": 21})
        assert matches_condition(issue, rule) is False


class TestNoRecentUpdate:
    def test_no_update_in_window(self):
        old_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        issue = _make_issue(
            status="In Progress",
            changelog={"last_status_change": old_date, "last_update": old_date, "field_history": {}},
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "days_in_status": 21,
            "no_recent_update": True,
        })
        assert matches_condition(issue, rule) is True

    def test_recent_update_suppresses(self):
        old_status = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        recent_update = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        issue = _make_issue(
            status="In Progress",
            changelog={
                "last_status_change": old_status,
                "last_update": recent_update,
                "field_history": {},
            },
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "days_in_status": 21,
            "no_recent_update": True,
        })
        assert matches_condition(issue, rule) is False


class TestFieldStaleDays:
    def test_stale_field_in_any_of(self):
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        issue = _make_issue(
            status="In Progress",
            status_summary="Green as of old date.",
            changelog={
                "last_status_change": old_date,
                "last_update": old_date,
                "field_history": {"status_summary": old_date},
            },
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "any_of": [
                {"field_empty": "status_summary"},
                {"field_stale_days": {"field": "status_summary", "threshold": 7}},
            ],
        })
        assert matches_condition(issue, rule) is True

    def test_fresh_field_in_any_of(self):
        recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        issue = _make_issue(
            status="In Progress",
            status_summary="Green as of today.",
            changelog={
                "last_status_change": recent,
                "last_update": recent,
                "field_history": {"status_summary": recent},
            },
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "any_of": [
                {"field_empty": "status_summary"},
                {"field_stale_days": {"field": "status_summary", "threshold": 7}},
            ],
        })
        assert matches_condition(issue, rule) is False

    def test_no_field_history_skips(self):
        issue = _make_issue(
            status="In Progress",
            status_summary="Green as of today.",
            changelog={"last_status_change": None, "last_update": None, "field_history": {}},
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "any_of": [
                {"field_stale_days": {"field": "status_summary", "threshold": 7}},
            ],
        })
        assert matches_condition(issue, rule) is False


class TestStatusChangedAfter:
    def test_status_changed_after_milestone(self):
        milestone_date_context[0] = "2026-07-24"
        try:
            issue = _make_issue(
                changelog={
                    "last_status_change": "2026-07-26T10:00:00.000+0000",
                    "last_update": "2026-07-26T10:00:00.000+0000",
                    "field_history": {},
                },
            )
            rule = _make_rule({"status_changed_after": "code_freeze_date"})
            assert matches_condition(issue, rule) is True
        finally:
            milestone_date_context[0] = None

    def test_status_changed_before_milestone(self):
        milestone_date_context[0] = "2026-07-24"
        try:
            issue = _make_issue(
                changelog={
                    "last_status_change": "2026-07-20T10:00:00.000+0000",
                    "last_update": "2026-07-26T10:00:00.000+0000",
                    "field_history": {},
                },
            )
            rule = _make_rule({"status_changed_after": "code_freeze_date"})
            assert matches_condition(issue, rule) is False
        finally:
            milestone_date_context[0] = None

    def test_no_milestone_date_skips(self):
        milestone_date_context[0] = None
        issue = _make_issue(
            changelog={
                "last_status_change": "2026-07-26T10:00:00.000+0000",
                "last_update": "2026-07-26T10:00:00.000+0000",
                "field_history": {},
            },
        )
        rule = _make_rule({"status_changed_after": "code_freeze_date"})
        assert matches_condition(issue, rule) is False


class TestCreatedAfter:
    def test_created_after_milestone(self):
        milestone_date_context[0] = "2026-07-01"
        try:
            issue = _make_issue(created="2026-07-15T10:00:00.000+0000")
            rule = _make_rule({"created_after": "planning_freeze_date"})
            assert matches_condition(issue, rule) is True
        finally:
            milestone_date_context[0] = None

    def test_created_before_milestone(self):
        milestone_date_context[0] = "2026-07-01"
        try:
            issue = _make_issue(created="2026-06-15T10:00:00.000+0000")
            rule = _make_rule({"created_after": "planning_freeze_date"})
            assert matches_condition(issue, rule) is False
        finally:
            milestone_date_context[0] = None


# --- ISO date parsing ---

class TestParseIsoDate:
    def test_jira_format_with_offset(self):
        dt = parse_iso_date("2026-07-15T10:30:00.000+0000")
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 7
        assert dt.day == 15

    def test_z_suffix(self):
        dt = parse_iso_date("2026-07-15T10:30:00Z")
        assert dt is not None
        assert dt.tzinfo is not None

    def test_colon_offset(self):
        dt = parse_iso_date("2026-07-15T10:30:00.000+00:00")
        assert dt is not None

    def test_none_returns_none(self):
        assert parse_iso_date(None) is None

    def test_empty_string_returns_none(self):
        assert parse_iso_date("") is None

    def test_date_only(self):
        dt = parse_iso_date("2026-07-15")
        assert dt is not None
        assert dt.year == 2026


class TestDaysSince:
    def test_known_difference(self):
        ref = datetime(2026, 7, 28, 12, 0, 0, tzinfo=timezone.utc)
        days = days_since("2026-07-20T12:00:00.000+0000", ref)
        assert days == 8

    def test_none_input(self):
        ref = datetime(2026, 7, 28, 12, 0, 0, tzinfo=timezone.utc)
        assert days_since(None, ref) is None


# --- Unsupported/unknown conditions ---

class TestUnsupportedConditions:
    def test_unsupported_key_skips_rule(self):
        issue = _make_issue()
        rule = _make_rule({"some_removed_condition": True})
        assert matches_condition(issue, rule) is False

    def test_unknown_key_skips_rule(self):
        issue = _make_issue()
        rule = _make_rule({"totally_made_up_condition": True})
        assert matches_condition(issue, rule) is False


# --- Combined conditions (AND logic) ---

class TestCombinedConditions:
    def test_all_conditions_must_pass(self):
        issue = _make_issue(
            status="In Progress",
            fix_versions=["3.5 GA RHOAI RELEASE"],
            labels=[],
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "field_set": "fix_version",
            "label_missing": ["qe-verified"],
        })
        assert matches_condition(issue, rule) is True

    def test_one_failing_condition_blocks(self):
        issue = _make_issue(
            status="Backlog",
            fix_versions=["3.5 GA RHOAI RELEASE"],
            labels=[],
        )
        rule = _make_rule({
            "status": ["In Progress"],
            "field_set": "fix_version",
            "label_missing": ["qe-verified"],
        })
        assert matches_condition(issue, rule) is False


# --- field_not_value ---

class TestFieldNotValue:
    def test_fires_when_field_differs(self):
        issue = _make_issue(release_blocker="Proposed")
        rule = _make_rule({"field_not_value": {"field": "release_blocker", "value": "Approved"}})
        assert matches_condition(issue, rule) is True

    def test_suppressed_when_field_matches(self):
        issue = _make_issue(release_blocker="Approved")
        rule = _make_rule({"field_not_value": {"field": "release_blocker", "value": "Approved"}})
        assert matches_condition(issue, rule) is False

    def test_fires_when_field_empty(self):
        issue = _make_issue(release_blocker=None)
        rule = _make_rule({"field_not_value": {"field": "release_blocker", "value": "Approved"}})
        assert matches_condition(issue, rule) is True


# --- updated_before_days ---

class TestUpdatedBeforeDays:
    def test_old_issue_matches(self):
        old_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        issue = _make_issue(created=old_date)
        rule = _make_rule({"updated_before_days": 7})
        assert matches_condition(issue, rule) is True

    def test_new_issue_skipped(self):
        recent_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        issue = _make_issue(created=recent_date)
        rule = _make_rule({"updated_before_days": 7})
        assert matches_condition(issue, rule) is False


# --- not_grandfathered ---

class TestNotGrandfathered:
    def test_old_version_grandfathered(self):
        issue = _make_issue(
            target_version=["rhoai-3.3"],
            fix_versions=[],
        )
        rule = _make_rule({"not_grandfathered": True})
        assert matches_condition(issue, rule) is False

    def test_new_version_not_grandfathered(self):
        issue = _make_issue(
            target_version=["3.5 GA RHOAI RELEASE"],
            fix_versions=[],
        )
        rule = _make_rule({"not_grandfathered": True})
        assert matches_condition(issue, rule) is True

    def test_mixed_versions_not_grandfathered(self):
        issue = _make_issue(
            target_version=["rhoai-3.3"],
            fix_versions=["3.5 GA RHOAI RELEASE"],
        )
        rule = _make_rule({"not_grandfathered": True})
        assert matches_condition(issue, rule) is True


# --- no_linked_signoff_template ---

class TestSignoffTemplate:
    def test_no_clone_link_fires(self):
        issue = _make_issue(issue_links=[])
        rule = _make_rule({"no_linked_signoff_template": True})
        assert matches_condition(issue, rule) is True

    def test_clone_to_template_suppresses(self):
        issue = _make_issue(issue_links=[
            {"verb": "clones", "target_key": "RHOAIENG-31303",
             "type": "Cloners", "direction": "outward"},
        ])
        rule = _make_rule({"no_linked_signoff_template": True})
        assert matches_condition(issue, rule) is False

    def test_clone_to_other_issue_still_fires(self):
        issue = _make_issue(issue_links=[
            {"verb": "clones", "target_key": "RHAIRFE-1234",
             "type": "Cloners", "direction": "outward"},
        ])
        rule = _make_rule({"no_linked_signoff_template": True})
        assert matches_condition(issue, rule) is True


# --- External enrichment flags ---

class TestExternalEnrichmentFlags:
    def test_signoff_incomplete_flag(self):
        issue = _make_issue()
        issue["_signoff_incomplete"] = True
        rule = _make_rule({"no_signoff_complete": True})
        assert matches_condition(issue, rule) is True

    def test_pr_merged_post_freeze_flag(self):
        issue = _make_issue()
        issue["_pr_merged_post_freeze"] = True
        rule = _make_rule({"pr_merged_to_release_branch": True})
        assert matches_condition(issue, rule) is True

    def test_pr_missing_jira_key_flag(self):
        issue = _make_issue()
        issue["_pr_missing_jira_key"] = True
        rule = _make_rule({"no_jira_key_in_pr": True})
        assert matches_condition(issue, rule) is True
