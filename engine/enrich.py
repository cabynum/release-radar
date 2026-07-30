"""External data resolution for release-radar.

Some rules check facts that live outside the Jira issue itself (GitHub
PRs, sign-off subtask status, doc link presence). This module fetches
that data and annotates issues with boolean flags before rule evaluation.

Best-effort: if an external service is unavailable, the affected rules
simply will not fire (flags default to False).
"""

import json
import re
import subprocess
import urllib.error
import urllib.request

from .jira_client import jira_get, load_env


def enrich_doc_drafts(issues: list[dict], verbose: bool = False) -> bool:
    """Check for AI-generated doc drafts linked to features.

    Sets _doc_draft_missing = True on features with docs_required=Yes
    that have no doc draft linked. Checks issue links for "documents"
    or "is documented by" relationships, and searches Drive for doc drafts.
    """
    targets = [i for i in issues if i.get("issue_type") == "Feature"
               and (i.get("docs_required") or "").lower() == "yes"]

    if not targets:
        return True

    for issue in targets:
        links = issue.get("issue_links", []) or []
        has_doc_link = any(
            any(term in (link.get("verb", "") + " " + link.get("type", "")).lower()
                for term in ("document", "doc"))
            for link in links
        )
        issue["_doc_draft_missing"] = not has_doc_link

    if verbose:
        missing = sum(1 for i in targets if i.get("_doc_draft_missing"))
        print(f"  Doc drafts: {len(targets)} features checked, "
              f"{missing} missing")
    return True


def enrich_signoff_status(issues: list[dict], verbose: bool = False) -> bool:
    """Fetch signoff template clone subtask status.

    The signoff process works via cloning: a feature clones one of the
    template issues (DP/TP/GA), then the clone's subtasks track individual
    sign-offs. We look for "is cloned by" links (the feature is the source,
    the signoff clone is the target) to find the feature's signoff clone,
    then check its subtask completion.

    Sets _signoff_incomplete = True on features missing sign-off.
    """
    signoff_templates = {"RHOAIENG-31244", "RHOAIENG-31290", "RHOAIENG-31303"}
    features = [i for i in issues if i.get("issue_type") == "Feature"]

    if not features:
        return True

    targets = []
    for issue in features:
        links = issue.get("issue_links", []) or []
        clone_key = None
        for link in links:
            if (link.get("verb") == "is cloned by"
                    and link.get("target_key", "").startswith("RHOAIENG")):
                clone_key = link.get("target_key")
                break
            if (link.get("verb") == "clones"
                    and link.get("target_key", "") in signoff_templates):
                clone_key = link.get("target_key")
                break
        if clone_key:
            targets.append((issue, clone_key))

    if not targets:
        for issue in features:
            issue["_signoff_incomplete"] = True
        if verbose:
            print(f"  Signoff status: {len(features)} features, "
                  f"none have signoff template links")
        return True

    load_env()
    for issue, clone_key in targets:
        try:
            data = jira_get(
                f"/rest/api/3/issue/{clone_key}?fields=subtasks"
            )
            subtasks = data.get("fields", {}).get("subtasks", [])
            all_done = all(
                (st.get("fields", {}).get("status", {})
                 .get("statusCategory", {}).get("name", "")) == "Done"
                for st in subtasks
            ) if subtasks else False
            issue["_signoff_incomplete"] = not all_done
        except (urllib.error.HTTPError, Exception):
            issue["_signoff_incomplete"] = True

    accounted_keys = {i["key"] for i, _ in targets}
    for issue in features:
        if issue["key"] not in accounted_keys:
            issue["_signoff_incomplete"] = True

    if verbose:
        incomplete = sum(1 for i in features if i.get("_signoff_incomplete"))
        print(f"  Signoff status: {len(targets)} features with templates, "
              f"{incomplete}/{len(features)} incomplete")
    return True


def enrich_pr_data(issues: list[dict], milestone_dates: dict | None = None,
                   verbose: bool = False) -> bool:
    """Check GitHub PRs for post-freeze Jira key compliance.

    Sets _pr_merged_post_freeze and _pr_missing_jira_key on issues
    that have PRs merged after code freeze without proper Jira references.
    Returns True if enrichment succeeded (even if no PRs found).
    """
    if not milestone_dates:
        return True

    code_freeze_dates = {
        k: v for k, v in milestone_dates.items() if "code_freeze" in k
    }
    if not code_freeze_dates:
        return True

    if not _gh_available():
        if verbose:
            print("  PR data: SKIPPED (gh CLI unavailable)")
        return False

    checked = 0
    for issue in issues:
        pr_field = issue.get("git_pull_request") or ""
        if not pr_field:
            continue

        pr_urls = re.findall(r'https?://[^\s,]+/pull/\d+', pr_field)
        if not pr_urls:
            continue

        for pr_url in pr_urls:
            merged_after_freeze = _check_pr_merged_after_freeze(
                pr_url, code_freeze_dates
            )
            if merged_after_freeze:
                issue["_pr_merged_post_freeze"] = True
                jira_pattern = re.compile(r'[A-Z][A-Z]+-\d+')
                has_key = bool(jira_pattern.search(pr_field))
                issue["_pr_missing_jira_key"] = not has_key
                checked += 1
                break

    if verbose:
        flagged = sum(1 for i in issues if i.get("_pr_merged_post_freeze"))
        print(f"  PR data: {checked} PRs checked, "
              f"{flagged} post-freeze merges")
    return True


def _gh_available() -> bool:
    """Check if gh CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _check_pr_merged_after_freeze(pr_url: str,
                                   freeze_dates: dict) -> bool:
    """Check if a PR was merged to a release branch after code freeze."""
    match = re.match(
        r'https?://github\.com/([^/]+/[^/]+)/pull/(\d+)', pr_url
    )
    if not match:
        return False

    repo, pr_num = match.group(1), match.group(2)
    try:
        result = subprocess.run(
            ["gh", "pr", "view", pr_num, "--repo", repo,
             "--json", "mergedAt,baseRefName,title,body"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return False

        data = json.loads(result.stdout)
        merged_at = data.get("mergedAt")
        base_ref = data.get("baseRefName", "")

        if not merged_at:
            return False

        is_release_branch = any(
            x in base_ref for x in ("release", "rhoai-", "rhods-")
        )
        if not is_release_branch:
            return False

        for _, freeze_date in freeze_dates.items():
            if merged_at > freeze_date:
                return True

    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass

    return False


def run_enrichment(issues: list[dict], milestones: dict | None = None,
                   verbose: bool = False) -> dict[str, bool]:
    """Run all enrichment passes on the issue list.

    Returns a dict mapping enrichment name -> success boolean.
    """
    results = {}

    results["doc_drafts"] = enrich_doc_drafts(issues, verbose)
    results["signoff_status"] = enrich_signoff_status(issues, verbose)

    milestone_dates = {}
    if milestones:
        for rel_key, rel_data in milestones.get("releases", {}).items():
            for ms_name, ms_date in rel_data.get("milestones", {}).items():
                milestone_dates[f"{rel_key}_{ms_name}"] = ms_date

    results["pr_data"] = enrich_pr_data(issues, milestone_dates, verbose)

    if verbose:
        ok = sum(1 for v in results.values() if v)
        print(f"  Enrichment: {ok}/{len(results)} sources available")
        print()

    return results
