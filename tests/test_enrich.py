"""Unit tests for release-radar enrichment: child completion checks."""

from unittest.mock import patch, MagicMock

import pytest

from engine.enrich import (
    enrich_child_completion,
    _check_docs_resolved,
    _fetch_all_children,
)


def _make_feature(**overrides) -> dict:
    """Create a minimal normalized Feature issue."""
    issue = {
        "key": "RHAISTRAT-1410",
        "summary": "Test feature",
        "project": "RHAISTRAT",
        "status": "Release Pending",
        "status_category": "Done",
        "issue_type": "Feature",
        "assignee": "Alina Ryan",
        "docs_required": "No",
        "issue_links": [],
    }
    issue.update(overrides)
    return issue


def _jira_search_response(issues: list[dict]) -> dict:
    """Build a mock Jira search API response."""
    return {
        "issues": [
            {
                "key": i["key"],
                "fields": {
                    "status": {
                        "statusCategory": {"name": i["status_category"]}
                    }
                },
            }
            for i in issues
        ]
    }


class TestCheckDocsResolved:
    def test_docs_not_required(self):
        issue = _make_feature(docs_required="No")
        assert _check_docs_resolved(issue) is True

    def test_docs_required_empty(self):
        issue = _make_feature(docs_required="")
        assert _check_docs_resolved(issue) is True

    def test_docs_required_none(self):
        issue = _make_feature(docs_required=None)
        assert _check_docs_resolved(issue) is True

    def test_docs_required_with_done_doc_link(self):
        issue = _make_feature(
            docs_required="Yes",
            issue_links=[
                {
                    "verb": "is documented by",
                    "type": "Documents",
                    "target_key": "RHAIENG-6047",
                    "target_status_category": "Done",
                }
            ],
        )
        assert _check_docs_resolved(issue) is True

    def test_docs_required_with_open_doc_link(self):
        issue = _make_feature(
            docs_required="Yes",
            issue_links=[
                {
                    "verb": "is documented by",
                    "type": "Documents",
                    "target_key": "RHAIENG-6047",
                    "target_status_category": "In Progress",
                }
            ],
        )
        assert _check_docs_resolved(issue) is False

    def test_docs_required_no_doc_link(self):
        issue = _make_feature(
            docs_required="Yes",
            issue_links=[
                {
                    "verb": "blocks",
                    "type": "Blocks",
                    "target_key": "RHAIENG-100",
                    "target_status_category": "Done",
                }
            ],
        )
        assert _check_docs_resolved(issue) is False


class TestEnrichChildCompletion:
    @patch("engine.enrich.load_env")
    @patch("engine.enrich.jira_get")
    def test_all_children_done(self, mock_jira_get, mock_load_env):
        feature = _make_feature(status="Release Pending")
        issues = [feature]

        epics = [
            {"key": "RHOAIENG-100", "status_category": "Done"},
            {"key": "RHOAIENG-101", "status_category": "Done"},
        ]
        stories = [
            {"key": "RHOAIENG-200", "status_category": "Done"},
            {"key": "RHOAIENG-201", "status_category": "Done"},
        ]

        mock_jira_get.side_effect = [
            _jira_search_response(epics),
            _jira_search_response(stories),
        ]

        result = enrich_child_completion(issues)

        assert result is True
        assert feature["_all_children_complete"] is True
        assert feature["_docs_resolved"] is True

    @patch("engine.enrich.load_env")
    @patch("engine.enrich.jira_get")
    def test_some_children_open(self, mock_jira_get, mock_load_env):
        feature = _make_feature(status="In Progress")
        issues = [feature]

        epics = [
            {"key": "RHOAIENG-100", "status_category": "Done"},
            {"key": "RHOAIENG-101", "status_category": "In Progress"},
        ]

        mock_jira_get.side_effect = [
            _jira_search_response(epics),
            _jira_search_response([]),
        ]

        result = enrich_child_completion(issues)

        assert result is True
        assert feature["_all_children_complete"] is False

    @patch("engine.enrich.load_env")
    @patch("engine.enrich.jira_get")
    def test_no_children_skips(self, mock_jira_get, mock_load_env):
        feature = _make_feature(status="Release Pending")
        issues = [feature]

        mock_jira_get.return_value = _jira_search_response([])

        result = enrich_child_completion(issues)

        assert result is True
        assert "_all_children_complete" not in feature

    @patch("engine.enrich.load_env")
    @patch("engine.enrich.jira_get")
    def test_level2_children_open_fails(self, mock_jira_get, mock_load_env):
        feature = _make_feature(status="Review")
        issues = [feature]

        epics = [{"key": "RHOAIENG-100", "status_category": "Done"}]
        stories = [
            {"key": "RHOAIENG-200", "status_category": "Done"},
            {"key": "RHOAIENG-201", "status_category": "In Progress"},
        ]

        mock_jira_get.side_effect = [
            _jira_search_response(epics),
            _jira_search_response(stories),
        ]

        result = enrich_child_completion(issues)

        assert result is True
        assert feature["_all_children_complete"] is False

    def test_non_feature_issues_ignored(self):
        story = {
            "key": "RHAIENG-100",
            "issue_type": "Story",
            "status": "In Progress",
        }
        result = enrich_child_completion([story])
        assert result is True

    def test_closed_features_ignored(self):
        feature = _make_feature(status="Closed")
        result = enrich_child_completion([feature])
        assert result is True
        assert "_all_children_complete" not in feature

    @patch("engine.enrich.load_env")
    @patch("engine.enrich.jira_get")
    def test_api_error_skips_gracefully(self, mock_jira_get, mock_load_env):
        import urllib.error
        feature = _make_feature(status="Release Pending")
        issues = [feature]

        mock_jira_get.side_effect = urllib.error.HTTPError(
            "url", 500, "Server Error", {}, None
        )

        result = enrich_child_completion(issues)

        assert result is True
        assert "_all_children_complete" not in feature
