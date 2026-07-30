#!/usr/bin/env python3
"""release-radar pipeline runner.

Single command to fetch Jira data, evaluate rules, and output violations.

Usage:
    python3 -m engine.run [--releases 3.5,3.6] [--verbose]
    python3 -m engine.run --snapshot output/snapshot.json [--verbose]

Requires JIRA_EMAIL and JIRA_API_TOKEN in .env or environment.
Run from the release-radar project root.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

from .jira_client import load_env, fetch_issues, fetch_changelogs
from .normalize import (
    JIRA_FIELDS, normalize_rest_issue, enrich_parent_components,
)
from .milestones import load_milestones
from .evaluate import evaluate
from .enrich import run_enrichment

DEFAULT_RELEASES = ["3.5", "3.6"]
DEFAULT_COMPONENT = "Data Processing"
DEFAULT_PROJECTS = ["RHAISTRAT", "RHAIENG", "RHOAIENG"]


def _build_jql(releases: list[str], projects: list[str],
               component: str, milestones: dict | None = None) -> str:
    """Build JQL targeting issues for the given team and release cycles."""
    projects_str = ", ".join(projects)

    all_versions = set()
    if milestones:
        for rel_key, rel_data in milestones.get("releases", {}).items():
            if any(rel_key.startswith(r) for r in releases):
                for v in rel_data.get("versions", []):
                    all_versions.add(v)

    if not all_versions:
        sys.exit("No version names found. Check milestones.yaml and --releases.")

    versions = ", ".join(f'"{v}"' for v in sorted(all_versions))

    return (
        f"project in ({projects_str}) AND "
        f"component = '{component}' AND ("
        f"fixVersion in ({versions}) OR "
        f'"Target Version" in ({versions}) OR '
        f"statusCategory = 'In Progress'"
        f") ORDER BY key ASC"
    )


def run_pipeline(releases: list[str], rules_dir: Path, output_dir: Path,
                 verbose: bool = False, snapshot_path: Path | None = None,
                 milestones_path: Path | None = None,
                 component: str = DEFAULT_COMPONENT,
                 projects: list[str] | None = None):
    """Full pipeline: fetch -> normalize -> evaluate -> output."""
    now = datetime.now(timezone.utc)
    projects = projects or DEFAULT_PROJECTS

    ms = None
    if milestones_path and milestones_path.exists():
        ms = load_milestones(milestones_path)
    elif (PROJECT_DIR / "milestones.yaml").exists():
        ms = load_milestones(PROJECT_DIR / "milestones.yaml")

    if not ms:
        sys.exit("milestones.yaml required (version names drive JQL and RL rules)")

    if snapshot_path:
        print(f"=== OFFLINE MODE: reading {snapshot_path.name} ===\n")
        snapshot_data = json.loads(snapshot_path.read_text())
        issues = snapshot_data.get("issues", [])
        enrich_parent_components(issues)
        print(f"Snapshot: {len(issues)} issues (fetched {snapshot_data.get('fetched_at', 'unknown')})")
    else:
        print(f"=== release-radar | {now.strftime('%Y-%m-%d %H:%M UTC')} ===")
        print(f"Component: {component}")
        print(f"Projects: {', '.join(projects)}")
        print(f"Releases: {', '.join(releases)}")
        print()

        print("Fetching from Jira...")
        load_env()
        jql = _build_jql(releases, projects, component, ms)
        raw_issues = fetch_issues(jql, JIRA_FIELDS, verbose=verbose)
        print(f"  {len(raw_issues)} issues fetched")

        print("Fetching changelogs...")
        issue_keys = [i.get("key", "") for i in raw_issues]
        changelogs = fetch_changelogs(issue_keys, verbose=verbose)
        print(f"  {len(changelogs)} changelogs fetched")

        print("Normalizing...")
        issues = [
            normalize_rest_issue(i, histories=changelogs.get(i.get("key", "")))
            for i in raw_issues
        ]
        enrich_parent_components(issues)

        by_project = {}
        by_type = {}
        for iss in issues:
            by_type[iss["issue_type"]] = by_type.get(iss["issue_type"], 0) + 1
            by_project[iss["project"]] = by_project.get(iss["project"], 0) + 1
        print(f"  By project: {dict(sorted(by_project.items()))}")
        print(f"  By type: {dict(sorted(by_type.items()))}")

        snapshot_data = {
            "fetched_at": now.isoformat(),
            "releases": releases,
            "projects": PROJECTS,
            "jql": jql,
            "issues": issues,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        snapshot_file = output_dir / "snapshot.json"
        snapshot_file.write_text(json.dumps(snapshot_data, indent=2))
        print(f"  Snapshot saved: {snapshot_file}")

    print("Resolving external data...")
    ext_status = run_enrichment(issues, milestones=ms, verbose=verbose)

    result = evaluate(rules_dir, issues, verbose=verbose, milestones=ms)
    result["meta"]["external_sources"] = ext_status

    violations_file = output_dir / "violations.json"
    violations_file.write_text(json.dumps(result, indent=2))
    print(f"\nViolations saved: {violations_file}")

    _print_summary(result)
    return result


def _print_summary(result: dict):
    """Print a human-readable summary."""
    print()
    print("=" * 70)
    print("VIOLATIONS BY RULE")
    print("=" * 70)
    for rule_id, count in result["summary"]["by_rule"].items():
        print(f"  {rule_id:40s} {count:4d}")

    print()
    print("BY SEVERITY")
    print("-" * 40)
    for sev in ("critical", "high", "medium", "low"):
        count = result["summary"]["by_severity"].get(sev, 0)
        if count:
            print(f"  {sev:12s} {count:4d}")

    print()
    skipped = result["meta"].get("rules_skipped", {})
    if skipped:
        print(f"SKIPPED RULES ({len(skipped)})")
        print("-" * 40)
        for rule_id, reason in skipped.items():
            print(f"  {rule_id}: {reason}")


def main():
    parser = argparse.ArgumentParser(
        description="release-radar: fetch, evaluate, report"
    )
    parser.add_argument(
        "--releases", default=",".join(DEFAULT_RELEASES),
        help=f"Comma-separated release versions (default: {','.join(DEFAULT_RELEASES)})"
    )
    parser.add_argument(
        "--component", default=DEFAULT_COMPONENT,
        help=f"Jira component to filter on (default: {DEFAULT_COMPONENT})"
    )
    parser.add_argument(
        "--projects", default=",".join(DEFAULT_PROJECTS),
        help=f"Comma-separated Jira projects (default: {','.join(DEFAULT_PROJECTS)})"
    )
    parser.add_argument("--snapshot", type=Path, default=None)
    parser.add_argument("--rules-dir", type=Path, default=PROJECT_DIR / "rules")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_DIR / "output")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    releases = [r.strip() for r in args.releases.split(",")]
    projects = [p.strip() for p in args.projects.split(",")]

    run_pipeline(
        releases=releases,
        rules_dir=args.rules_dir,
        output_dir=args.output_dir,
        verbose=args.verbose,
        snapshot_path=args.snapshot,
        component=args.component,
        projects=projects,
    )


if __name__ == "__main__":
    main()
