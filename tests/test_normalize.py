"""Unit tests for Jira issue normalization and changelog parsing."""

import pytest

from engine.normalize import normalize_rest_issue, parse_changelog, normalize_issue_links


# --- Fixtures: raw Jira REST API format ---

def _raw_issue(**field_overrides) -> dict:
    """Create a minimal raw Jira REST API issue."""
    fields = {
        "summary": "Implement data pipeline",
        "status": {"name": "In Progress", "statusCategory": {"name": "In Progress"}},
        "issuetype": {"name": "Story"},
        "assignee": {"displayName": "Jane Doe"},
        "components": [{"name": "Data Processing"}],
        "fixVersions": [{"name": "3.5 GA RHOAI RELEASE"}],
        "labels": ["sprint-42", "qe-verified"],
        "issuelinks": [],
        "parent": {"key": "RHAIENG-50"},
        "created": "2026-06-01T10:00:00.000+0000",
        "customfield_10028": 5,
        "customfield_10020": [{"name": "Sprint 42", "state": "active"}],
        "customfield_10464": {"value": "New Feature"},
        "customfield_10469": {"displayName": "PM Person"},
        "customfield_10470": {"displayName": "QA Person"},
        "customfield_10483": None,
        "customfield_10517": None,
        "customfield_10638": [{"value": "Unit"}, {"value": "Integration"}],
        "customfield_10665": {"value": "Yes"},
        "customfield_10712": {"value": "Green"},
        "customfield_10783": None,
        "customfield_10785": {"value": "Feature"},
        "customfield_10807": {"value": "Done"},
        "customfield_10814": {
            "type": "doc",
            "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "Green as of 2026-07-28. On track."}
            ]}],
        },
        "customfield_10851": {"value": "Major"},
        "customfield_10855": [{"name": "3.5 GA RHOAI RELEASE"}],
        "customfield_10864": 150,
        "customfield_10868": [{"value": "RHOAI"}],
        "customfield_10875": None,
        "customfield_10023": "2026-08-15",
    }
    fields.update(field_overrides)
    return {"key": "RHAIENG-100", "fields": fields}


# --- normalize_rest_issue ---

class TestNormalizeRestIssue:
    def test_basic_fields(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["key"] == "RHAIENG-100"
        assert result["project"] == "RHAIENG"
        assert result["status"] == "In Progress"
        assert result["status_category"] == "In Progress"
        assert result["issue_type"] == "Story"
        assert result["assignee"] == "Jane Doe"
        assert result["summary"] == "Implement data pipeline"

    def test_components(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["components"] == ["Data Processing"]

    def test_fix_versions(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["fix_versions"] == ["3.5 GA RHOAI RELEASE"]

    def test_target_version(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["target_version"] == ["3.5 GA RHOAI RELEASE"]

    def test_labels(self):
        result = normalize_rest_issue(_raw_issue())
        assert "sprint-42" in result["labels"]
        assert "qe-verified" in result["labels"]

    def test_custom_fields(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["story_points"] == 5
        assert result["activity_type"] == "New Feature"
        assert result["color_status"] == "Green"
        assert result["rice_score"] == 150
        assert result["target_end"] == "2026-08-15"

    def test_user_fields(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["qa_contact"] == "QA Person"
        assert result["product_manager"] == "PM Person"

    def test_option_fields(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["release_type"] == "Major"
        assert result["docs_required"] == "Yes"
        assert result["release_note"] == "Done"
        assert result["release_note_type"] == "Feature"

    def test_multi_option_fields(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["test_coverage"] == ["Unit", "Integration"]
        assert result["products"] == ["RHOAI"]

    def test_adf_text_extraction(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["status_summary"] == "Green as of 2026-07-28. On track."

    def test_sprint_normalization(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["sprint"] == [{"name": "Sprint 42", "state": "active"}]

    def test_parent_link(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["parent_link"] == "RHAIENG-50"

    def test_no_parent(self):
        result = normalize_rest_issue(_raw_issue(parent=None))
        assert result["parent_link"] is None

    def test_blocked_true(self):
        result = normalize_rest_issue(_raw_issue(customfield_10517={"value": "True"}))
        assert result["blocked"] is True

    def test_blocked_false(self):
        result = normalize_rest_issue(_raw_issue(customfield_10517=None))
        assert result["blocked"] is False

    def test_unassigned(self):
        result = normalize_rest_issue(_raw_issue(assignee=None))
        assert result["assignee"] == "Unassigned"

    def test_created_field(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["created"] == "2026-06-01T10:00:00.000+0000"

    def test_changelog_with_histories(self):
        histories = [
            {
                "created": "2026-07-01T12:00:00.000+0000",
                "items": [{"field": "status", "fromString": "Backlog", "toString": "In Progress"}],
            },
            {
                "created": "2026-07-20T09:00:00.000+0000",
                "items": [{"field": "Status Summary", "fromString": "", "toString": "Green"}],
            },
        ]
        result = normalize_rest_issue(_raw_issue(), histories=histories)
        assert result["changelog"]["last_status_change"] == "2026-07-01T12:00:00.000+0000"
        assert result["changelog"]["last_update"] == "2026-07-20T09:00:00.000+0000"
        assert result["changelog"]["field_history"]["status_summary"] == "2026-07-20T09:00:00.000+0000"

    def test_changelog_without_histories(self):
        result = normalize_rest_issue(_raw_issue())
        assert result["changelog"]["last_status_change"] is None
        assert result["changelog"]["last_update"] is None

    def test_empty_target_version(self):
        result = normalize_rest_issue(_raw_issue(customfield_10855=None))
        assert result["target_version"] == []

    def test_empty_fix_versions(self):
        result = normalize_rest_issue(_raw_issue(fixVersions=[]))
        assert result["fix_versions"] == []


# --- normalize_issue_links ---

class TestNormalizeIssueLinks:
    def test_outward_link(self):
        raw = [
            {
                "type": {"name": "Blocks", "outward": "blocks", "inward": "is blocked by"},
                "outwardIssue": {
                    "key": "RHAIENG-200",
                    "fields": {
                        "status": {
                            "name": "In Progress",
                            "statusCategory": {"name": "In Progress"},
                        },
                        "assignee": {"displayName": "Bob"},
                    },
                },
            },
        ]
        result = normalize_issue_links(raw)
        assert len(result) == 1
        assert result[0]["type"] == "Blocks"
        assert result[0]["direction"] == "outward"
        assert result[0]["verb"] == "blocks"
        assert result[0]["target_key"] == "RHAIENG-200"
        assert result[0]["target_status"] == "In Progress"
        assert result[0]["target_assignee"] == "Bob"

    def test_inward_link(self):
        raw = [
            {
                "type": {"name": "Cloners", "outward": "clones", "inward": "is cloned by"},
                "inwardIssue": {
                    "key": "RHAIRFE-500",
                    "fields": {
                        "status": {
                            "name": "Approved",
                            "statusCategory": {"name": "Done"},
                        },
                        "assignee": None,
                    },
                },
            },
        ]
        result = normalize_issue_links(raw)
        assert len(result) == 1
        assert result[0]["direction"] == "inward"
        assert result[0]["verb"] == "is cloned by"
        assert result[0]["target_key"] == "RHAIRFE-500"
        assert result[0]["target_status_category"] == "Done"
        assert result[0]["target_assignee"] == "Unassigned"

    def test_empty_links(self):
        assert normalize_issue_links([]) == []
        assert normalize_issue_links(None) == []

    def test_bidirectional_link(self):
        raw = [
            {
                "type": {"name": "Blocks", "outward": "blocks", "inward": "is blocked by"},
                "outwardIssue": {
                    "key": "RHAIENG-201",
                    "fields": {"status": {"name": "New", "statusCategory": {"name": "To Do"}}, "assignee": None},
                },
                "inwardIssue": {
                    "key": "RHAIENG-199",
                    "fields": {"status": {"name": "Done", "statusCategory": {"name": "Done"}}, "assignee": {"displayName": "Alice"}},
                },
            },
        ]
        result = normalize_issue_links(raw)
        assert len(result) == 2


# --- parse_changelog ---

class TestParseChangelog:
    def test_status_change_detected(self):
        histories = [
            {
                "created": "2026-06-15T10:00:00.000+0000",
                "items": [{"field": "status", "fromString": "Backlog", "toString": "Refinement"}],
            },
            {
                "created": "2026-07-01T12:00:00.000+0000",
                "items": [{"field": "status", "fromString": "Refinement", "toString": "In Progress"}],
            },
        ]
        result = parse_changelog({}, histories=histories)
        assert result["last_status_change"] == "2026-07-01T12:00:00.000+0000"
        assert result["last_update"] == "2026-07-01T12:00:00.000+0000"

    def test_field_history_tracked(self):
        histories = [
            {
                "created": "2026-07-10T09:00:00.000+0000",
                "items": [{"field": "Status Summary", "fromString": "", "toString": "Yellow as of..."}],
            },
            {
                "created": "2026-07-20T09:00:00.000+0000",
                "items": [{"field": "Status Summary", "fromString": "Yellow", "toString": "Green as of..."}],
            },
        ]
        result = parse_changelog({}, histories=histories)
        assert result["field_history"]["status_summary"] == "2026-07-20T09:00:00.000+0000"

    def test_multiple_items_in_one_entry(self):
        histories = [
            {
                "created": "2026-07-15T14:00:00.000+0000",
                "items": [
                    {"field": "status", "fromString": "Backlog", "toString": "In Progress"},
                    {"field": "assignee", "from": None, "to": "user123"},
                ],
            },
        ]
        result = parse_changelog({}, histories=histories)
        assert result["last_status_change"] == "2026-07-15T14:00:00.000+0000"
        assert result["last_update"] == "2026-07-15T14:00:00.000+0000"

    def test_empty_histories(self):
        result = parse_changelog({}, histories=[])
        assert result["last_status_change"] is None
        assert result["last_update"] is None
        assert result["field_history"] == {}

    def test_color_status_tracked(self):
        histories = [
            {
                "created": "2026-07-18T11:00:00.000+0000",
                "items": [{"field": "Color Status", "fromString": "Green", "toString": "Yellow"}],
            },
        ]
        result = parse_changelog({}, histories=histories)
        assert result["field_history"]["color_status"] == "2026-07-18T11:00:00.000+0000"

    def test_fallback_to_raw_changelog_key(self):
        raw = {
            "changelog": {
                "histories": [
                    {
                        "created": "2026-07-05T08:00:00.000+0000",
                        "items": [{"field": "status", "fromString": "New", "toString": "Backlog"}],
                    },
                ],
            },
        }
        result = parse_changelog(raw)
        assert result["last_status_change"] == "2026-07-05T08:00:00.000+0000"
