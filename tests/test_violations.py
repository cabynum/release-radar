"""Tests for violation message templating."""

from engine.violations import build_violation


def _issue(**overrides):
    base = {
        "key": "RHAISTRAT-2591",
        "summary": "Example feature",
        "issue_type": "Feature",
        "status": "In Progress",
        "assignee": "Rishabh Singh",
        "project": "RHAISTRAT",
        "labels": [],
        "components": [],
        "target_version": ["3.6 GA RHOAI RELEASE"],
        "fix_versions": [],
        "release_type": "GA",
    }
    base.update(overrides)
    return base


def _rule(message: str):
    return {
        "id": "missing-signoff-template",
        "name": "Feature Signoff Template Missing",
        "condition": {"field_set": "release_type"},
        "action": {"message": message},
        "enforcement": "comment",
        "scope": "org",
        "verification": "heuristic",
        "sources": [],
        "_file": "missing-signoff-template.yaml",
    }


def test_release_type_placeholder_substituted():
    message = (
        "Feature {key} has Release Type = {release_type} but no linked "
        "signoff template."
    )
    violation = build_violation(_issue(release_type="Tech Preview"), _rule(message))
    assert "{release_type}" not in violation["message"]
    assert "Release Type = Tech Preview" in violation["message"]
    assert "RHAISTRAT-2591" in violation["message"]


def test_release_type_placeholder_empty_when_unset():
    message = "Feature {key} has Release Type = {release_type}."
    violation = build_violation(_issue(release_type=None), _rule(message))
    assert "{release_type}" not in violation["message"]
    assert "Release Type = ." in violation["message"]
