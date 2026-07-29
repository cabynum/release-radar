"""Unit tests for milestone loading and trigger logic."""

from datetime import date
from pathlib import Path

import pytest

from engine.milestones import load_milestones, trigger_active


# --- Fixtures ---

def _milestones() -> dict:
    """Build a milestones dict matching the real milestones.yaml structure."""
    return load_milestones(Path(__file__).resolve().parent.parent / "milestones.yaml")


def _make_rule(trigger: dict) -> dict:
    return {
        "id": "test-rule",
        "trigger": trigger,
        "condition": {},
        "applies_to": ["Feature"],
    }


# --- load_milestones ---

class TestLoadMilestones:
    def test_loads_releases(self):
        ms = _milestones()
        assert "releases" in ms
        assert "3.5 GA" in ms["releases"]
        assert "3.6 EA1" in ms["releases"]

    def test_version_lookup(self):
        ms = _milestones()
        lookup = ms["version_lookup"]
        assert lookup["3.5 GA RHOAI RELEASE"] == "3.5 GA"
        assert lookup["rhoai-3.5"] == "3.5 GA"
        assert lookup["3.6 EA1 RHOAI RELEASE"] == "3.6 EA1"

    def test_milestone_dates_present(self):
        ms = _milestones()
        milestones = ms["releases"]["3.5 GA"]["milestones"]
        assert "planning_freeze" in milestones
        assert "feature_freeze" in milestones
        assert "code_freeze" in milestones
        assert "ga" in milestones


# --- trigger_active ---

class TestTriggerActive:
    def test_days_before_in_window(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "planning_freeze", "days_before": 7})
        # 3.6 EA1 planning_freeze is 2026-07-29; 2026-07-25 is 4 days before
        ctx = trigger_active(rule, ms, date(2026, 7, 25))
        assert ctx is not None
        releases = [r["release"] for r in ctx["active_releases"]]
        assert "3.6 EA1" in releases

    def test_days_before_outside_window(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "planning_freeze", "days_before": 7})
        # 2026-07-15 is 14 days before 3.6 EA1 planning_freeze
        ctx = trigger_active(rule, ms, date(2026, 7, 15))
        # Should not include 3.6 EA1 (outside 7-day window)
        if ctx:
            releases = [r["release"] for r in ctx["active_releases"]]
            assert "3.6 EA1" not in releases

    def test_days_after_active(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "code_freeze", "days_after": 0})
        # 3.5 GA code_freeze is 2026-07-24; testing on 2026-07-28
        ctx = trigger_active(rule, ms, date(2026, 7, 28))
        assert ctx is not None
        releases = [r["release"] for r in ctx["active_releases"]]
        assert "3.5 GA" in releases
        # Verify days_since is computed
        match = next(r for r in ctx["active_releases"] if r["release"] == "3.5 GA")
        assert match["days_since"] == 4

    def test_days_after_before_milestone(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "code_freeze", "days_after": 0})
        # 3.6 EA1 code_freeze is 2026-08-21; testing before that
        ctx = trigger_active(rule, ms, date(2026, 7, 28))
        if ctx:
            releases = [r["release"] for r in ctx["active_releases"]]
            assert "3.6 EA1" not in releases

    def test_no_matching_milestone(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "nonexistent_milestone", "days_before": 7})
        ctx = trigger_active(rule, ms, date(2026, 7, 28))
        assert ctx is None

    def test_on_milestone_day_days_before(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "planning_freeze", "days_before": 7})
        # On the exact day of 3.6 EA1 planning_freeze (2026-07-29)
        ctx = trigger_active(rule, ms, date(2026, 7, 29))
        assert ctx is not None
        releases = [r["release"] for r in ctx["active_releases"]]
        assert "3.6 EA1" in releases
        match = next(r for r in ctx["active_releases"] if r["release"] == "3.6 EA1")
        assert match["days_until"] == 0

    def test_on_milestone_day_days_after(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "code_freeze", "days_after": 0})
        # On the exact code_freeze day for 3.5 GA (2026-07-24)
        ctx = trigger_active(rule, ms, date(2026, 7, 24))
        assert ctx is not None
        releases = [r["release"] for r in ctx["active_releases"]]
        assert "3.5 GA" in releases

    def test_multiple_releases_can_match(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "planning_freeze", "days_after": 0})
        # Far enough in the future that multiple releases' planning_freeze passed
        ctx = trigger_active(rule, ms, date(2026, 10, 1))
        assert ctx is not None
        assert len(ctx["active_releases"]) >= 3

    def test_context_includes_versions(self):
        ms = _milestones()
        rule = _make_rule({"milestone": "code_freeze", "days_after": 0})
        ctx = trigger_active(rule, ms, date(2026, 7, 28))
        match = next(r for r in ctx["active_releases"] if r["release"] == "3.5 GA")
        assert "3.5 GA RHOAI RELEASE" in match["versions"]
        assert "rhoai-3.5" in match["versions"]
