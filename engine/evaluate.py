#!/usr/bin/env python3
"""release-radar evaluation engine.

Loads YAML rules, reads a Jira snapshot, evaluates field-hygiene and
release-lifecycle rules, and outputs violations with full provenance.

Usage:
    python3 engine/evaluate.py --snapshot output/snapshot.json [--verbose]
"""

import argparse
import json
import sys
from datetime import datetime, date, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

PROJECT_DIR = Path(__file__).resolve().parent.parent

from .conditions import (
    matches_condition,
    preflight_check,
    is_field_empty,
    is_field_set,
    check_field_value,
    check_sub_condition,
    parse_iso_date,
    days_since,
    milestone_date_context,
    FIELD_ALIASES,
    KNOWN_CONDITION_KEYS,
    UNSUPPORTED_CONDITION_KEYS,
    UNFETCHED_FIELDS,
)
from .milestones import load_milestones, trigger_active
from .violations import build_violation, find_matched_link

# --- Backward-compatibility aliases (used by tests and run.py) ---
_is_field_empty = is_field_empty
_is_field_set = is_field_set
_check_field_value = check_field_value
_check_sub_condition = check_sub_condition
_matches_condition = matches_condition
_parse_iso_date = parse_iso_date
_days_since = days_since
_trigger_active = trigger_active
_current_milestone_date = milestone_date_context
_KNOWN_CONDITION_KEYS = KNOWN_CONDITION_KEYS
_UNSUPPORTED_CONDITION_KEYS = UNSUPPORTED_CONDITION_KEYS
_UNFETCHED_FIELDS = UNFETCHED_FIELDS


# --- Rule loading ---

def _load_rules(rules_dir: Path) -> list[dict]:
    """Load all YAML rule files from subdirectories."""
    rules = []
    for yaml_file in sorted(rules_dir.rglob("*.yaml")):
        with open(yaml_file) as f:
            rule = yaml.safe_load(f)
        if rule and isinstance(rule, dict) and "id" in rule:
            rule["_file"] = str(yaml_file.relative_to(rules_dir))
            rules.append(rule)
    return rules


def _applies_to_issue(issue: dict, rule: dict) -> bool:
    """Check if the rule's applies_to includes this issue type."""
    applies_to = rule.get("applies_to", [])
    return issue["issue_type"] in applies_to


# --- Main evaluation ---

def evaluate(rules_dir: Path, issues: list[dict], verbose: bool = False,
             milestones: dict | None = None,
             eval_date: date | None = None) -> dict:
    """Run field-hygiene and release-lifecycle rules against issues."""
    today = eval_date or date.today()

    print(f"Loading rules from {rules_dir}...")
    rules = _load_rules(rules_dir)
    print(f"  Loaded {len(rules)} rules")

    fh_rules = [r for r in rules if "field-hygiene" in r.get("_file", "")]
    rl_rules = [r for r in rules if "release-lifecycle" in r.get("_file", "")]
    sp_rules = [r for r in rules if "sprint-level" in r.get("_file", "")]

    print(f"  Field-hygiene: {len(fh_rules)}")
    if milestones:
        print(f"  Release-lifecycle: {len(rl_rules)} (milestone-aware, date={today})")
    else:
        print(f"  Release-lifecycle: {len(rl_rules)} (no milestones provided, skipping)")
    print(f"  Sprint-level: {len(sp_rules)} (deferred - manual/cadence checks)")
    print(f"\nEvaluating against {len(issues)} issues...")
    print()

    violations = []
    rules_evaluated = 0
    rules_skipped = {}
    checks_performed = 0

    # --- Field-hygiene rules (always-on) ---
    for rule in fh_rules:
        rule_violations = 0
        rule_checks = 0

        skipped_reason = preflight_check(rule)
        if skipped_reason:
            rules_skipped[rule["id"]] = skipped_reason
            continue

        rules_evaluated += 1
        for issue in issues:
            if not _applies_to_issue(issue, rule):
                continue
            rule_checks += 1
            checks_performed += 1
            if matches_condition(issue, rule):
                matched_link = find_matched_link(issue, rule)
                violations.append(
                    build_violation(issue, rule, matched_link=matched_link)
                )
                rule_violations += 1

        if verbose:
            status = f"violations={rule_violations}" if rule_violations else "clean"
            print(f"  {rule['id']:40s} checked={rule_checks:4d}  {status}")

    # --- Release-lifecycle rules (milestone-driven) ---
    if milestones and rl_rules:
        if verbose:
            print()
            print("  --- Release-lifecycle rules ---")

        for rule in rl_rules:
            rule_violations = 0
            rule_checks = 0

            skipped_reason = preflight_check(rule)
            if skipped_reason:
                rules_skipped[rule["id"]] = skipped_reason
                continue

            trigger_ctx = trigger_active(rule, milestones, today)
            if not trigger_ctx:
                rules_skipped[rule["id"]] = "trigger not active"
                continue

            rules_evaluated += 1
            for rel_ctx in trigger_ctx["active_releases"]:
                rel_versions = rel_ctx["versions"]
                milestone_date_context[0] = rel_ctx.get("milestone_date")
                for issue in issues:
                    if not _applies_to_issue(issue, rule):
                        continue
                    rule_checks += 1
                    checks_performed += 1
                    if matches_condition(issue, rule, release_versions=rel_versions):
                        violations.append(
                            build_violation(issue, rule, release_ctx=rel_ctx)
                        )
                        rule_violations += 1
                milestone_date_context[0] = None

            if verbose:
                releases = ", ".join(
                    r["release"] for r in trigger_ctx["active_releases"]
                )
                status = f"violations={rule_violations}" if rule_violations else "clean"
                print(f"  {rule['id']:40s} checked={rule_checks:4d}  {status}  [{releases}]")

    print(f"\nEvaluation complete:")
    print(f"  Rules evaluated: {rules_evaluated}")
    print(f"  Rules skipped:   {len(rules_skipped)}")
    print(f"  Checks performed: {checks_performed}")
    print(f"  Violations found: {len(violations)}")

    if rules_skipped and verbose:
        print(f"\n  Skipped rules:")
        for rule_id, reason in rules_skipped.items():
            print(f"    {rule_id}: {reason}")

    rule_counts = {}
    for v in violations:
        rid = v["rule_id"]
        rule_counts[rid] = rule_counts.get(rid, 0) + 1

    return {
        "meta": {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "eval_date": str(today),
            "issues_evaluated": len(issues),
            "rules_total": len(rules),
            "rules_evaluated": rules_evaluated,
            "rules_skipped": rules_skipped,
        },
        "summary": {
            "total_violations": len(violations),
            "by_rule": dict(sorted(rule_counts.items(), key=lambda x: -x[1])),
        },
        "violations": violations,
    }


def main():
    parser = argparse.ArgumentParser(description="release-radar evaluation engine")
    parser.add_argument("--snapshot", type=Path,
                        default=PROJECT_DIR / "output" / "snapshot.json")
    parser.add_argument("--rules-dir", type=Path,
                        default=PROJECT_DIR / "rules")
    parser.add_argument("--output", type=Path,
                        default=PROJECT_DIR / "output" / "violations.json")
    parser.add_argument("--milestones", type=Path, default=None)
    parser.add_argument("--date", type=str, default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not args.snapshot.exists():
        sys.exit(f"Snapshot not found: {args.snapshot}")

    snapshot = json.loads(args.snapshot.read_text())
    issues = snapshot.get("issues", [])
    print(f"Snapshot: {args.snapshot.name} ({len(issues)} issues, "
          f"fetched {snapshot.get('fetched_at', 'unknown')})")
    print()

    ms = None
    if args.milestones:
        ms = load_milestones(args.milestones)
    eval_date = date.fromisoformat(args.date) if args.date else None

    result = evaluate(args.rules_dir, issues, verbose=args.verbose,
                      milestones=ms, eval_date=eval_date)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2))
    print(f"\nOutput written to {args.output}")


if __name__ == "__main__":
    main()
