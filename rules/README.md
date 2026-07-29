# release-radar Rules Catalog

Each YAML file is a self-contained rule definition with provenance,
condition logic, action templates, and scope classification.

See [`../planning/sources.md`](../planning/sources.md) for the full source
inventory backing these rules.

---

## Field-Hygiene

Always-on checks regardless of release cycle position.

### Org-Scoped (enforceable across RHAI)

| ID | File | Severity | Description |
|---|---|---|---|
| FH-01 | `missing-assignee.yaml` | High | Issue is in active status (In Progress, Review, Testing) but has no one assigned to it |
| FH-02 | `missing-team.yaml` | High | Issue exists without a Team field, making ownership and board filtering impossible |
| FH-03 | `missing-component.yaml` | Medium | Active issue has no Component set, breaking routing and query scoping |
| FH-04 | `missing-story-points.yaml` | Medium | Issue is committed to a sprint but has no story points, which breaks velocity and allocation math |
| FH-05 | `missing-activity-type.yaml` | Low | Activity Type is empty after 7+ days (auto-classifier should have caught it) |
| FH-06 | `stale-status-summary.yaml` | Medium | Status Summary is either missing or hasn't been updated in over 7 days |
| FH-07 | `missing-color-status.yaml` | Medium | Issue has Target Version and is actively being worked, but no Green/Yellow/Red health indicator |
| FH-08 | `color-summary-mismatch.yaml` | Low | The color word in Status Summary text doesn't match the Color Status dropdown value |
| FH-09 | `missing-epic-parent.yaml` | Medium | Story, Task, or Spike has no Epic Link, making it invisible to hierarchy rollups |
| FH-10 | `missing-strat-parent.yaml` | Medium | Epic has no Parent Link to a Feature in RHAISTRAT, disconnecting it from release tracking |
| FH-11 | `missing-target-version.yaml` | High | Feature is being actively worked but PM hasn't set a Target Version (desired release) |
| FH-12 | `fix-version-without-target.yaml` | Low | Engineering committed (Fix Version set) but PM hasn't planned it (no Target Version) |
| FH-13 | `version-mismatch.yaml` | Medium | Target Version and Fix Version point to different releases, signaling a planning conflict |
| FH-14 | `missing-fix-version.yaml` | High | Feature has progressed past Refinement without a Fix Version, meaning no delivery commitment exists |
| FH-15 | `labels-as-commitment.yaml` | Low | Labels like "committed" or "3.6" are being used instead of the Fix Version field |
| FH-16 | `missing-release-type.yaml` | High | Feature has no Release Type (GA, Tech Preview, Dev Preview), which determines signoff and docs requirements |
| FH-17 | `missing-product-manager.yaml` | High | Feature has no Product Manager assigned; required by Quality Gate 1 |
| FH-18 | `missing-products.yaml` | Medium | Feature is missing the Products field that identifies which product line it belongs to |
| FH-19 | `missing-docs-required.yaml` | Medium | Feature hasn't declared whether documentation is needed (field is empty or "None") |
| FH-20 | `stale-in-progress.yaml` | Medium | Issue has been In Progress for 21+ days with no status change, comment, or field update |
| FH-21 | `missing-git-pr.yaml` | Medium | Issue is in Review or Testing but the Git Pull Request field is empty (links in comments don't count) |
| FH-22 | `blocked-without-reason.yaml` | Medium | Issue is marked Blocked but doesn't explain why in the Blocked Reason field |
| FH-23 | `missing-signoff-template.yaml` | Medium | Feature has a Release Type but no linked DP/TP/GA signoff template for PM/UX sign-off |
| FH-24 | `stale-refinement.yaml` | Medium | Issue has been stuck in Refinement for 21+ days without advancing or returning to Backlog |
| FH-25 | `status-sprint-mismatch.yaml` | Medium | Issue shows active status (In Progress, Review, Testing) but isn't assigned to any sprint |
| FH-26 | `cross-team-dependency.yaml` | High | Issue is blocked by another team's issue that is stalled (in Backlog/New or unassigned) |
| FH-27 | `missing-release-notes.yaml` | Medium | Feature needs documentation (Docs Required = Yes) but Release Note fields are empty |

### Team-Scoped (DP conventions, advisory for others)

| ID | File | Severity | Description |
|---|---|---|---|
| FH-28 | `missing-rfe-link.yaml` | Medium | Feature isn't linked via "clones" to an approved RHAIRFE, meaning it may have skipped RFE Council |
| FH-29 | `premature-target-version.yaml` | Low | Issue in New status already has a Target Version before refinement has confirmed scope |
| FH-30 | `missing-target-end.yaml` | Low | Feature lacks a Target End date (PM's "no later than" delivery expectation) |
| FH-31 | `missing-rice-score.yaml` | Medium | Feature is missing RICE scoring (Reach, Impact, Confidence, Effort) needed for prioritization |
| FH-32 | `missing-test-coverage.yaml` | Low | Work item hasn't declared its test coverage status (Automated, Manual, or No Coverage) |
| FH-33 | `component-hierarchy-mismatch.yaml` | Low | Child issue has a different Component than its parent, which confuses ownership queries |
| FH-34 | `stale-backlog-with-tv.yaml` | Medium | Feature has sat in New/Backlog for 60+ days with a Target Version, suggesting a stale commitment |
| FH-35 | `missing-contributors.yaml` | Low | Active Feature doesn't list who is doing the day-to-day work in the Contributors field |
| FH-36 | `missing-refinement-doc.yaml` | Medium | Feature has no Refinement Doc in the DP verification Drive folder |
| FH-37 | `missing-qa-contact.yaml` | Low | Epic in active status has no named QA owner for test coordination |
| FH-38 | `missing-issue-links.yaml` | Low | Feature likely has dependencies or blockers but the Issue Links field is empty |

---

## Release-Lifecycle

Deadline-driven rules that activate based on proximity to release milestones.

| ID | File | Severity | Trigger | Description |
|---|---|---|---|---|
| RL-01 | `qg1-completeness.yaml` | Critical | Planning Freeze -7d | Feature is missing Quality Gate 1 requirements (labels, mandatory fields) and will be excluded from GA scope |
| RL-02 | `strat-review-required.yaml` | High | Planning Freeze -7d | Feature targeting the release hasn't passed strat-review with approved status |
| RL-03 | `fix-version-at-planning-freeze.yaml` | Critical | Planning Freeze -3d | Feature has Target Version but no Fix Version, meaning engineering hasn't committed |
| RL-04 | `scope-exception-required.yaml` | High | Planning Freeze +0d | Feature was added to the release after Planning Freeze and needs a formal scope exception |
| RL-05 | `pre-freeze-signoff.yaml` | High | Feature Freeze -14d | Feature hasn't obtained PM/UX sign-off and time is running out before Feature Freeze |
| RL-06 | `pre-feature-freeze-status.yaml` | Critical | Feature Freeze -7d | Feature is still In Progress with Feature Freeze approaching; must advance or be removed |
| RL-07 | `feature-freeze-enforcement.yaml` | Critical | Feature Freeze +0d | Feature is incomplete at Feature Freeze; Fix Version will be removed |
| RL-08 | `doc-draft-at-feature-freeze.yaml` | Medium | Feature Freeze +0d | Feature needs docs but no AI-generated draft exists for Tech Writer handoff |
| RL-09 | `pre-code-freeze-release-pending.yaml` | Critical | Code Freeze -3d | Feature hasn't moved to Release Pending status before Code Freeze |
| RL-10 | `unresolved-blockers.yaml` | Critical | Code Freeze -3d | Blocker-priority issue is still open and needs leadership approval to persist |
| RL-11 | `test-infra-exception.yaml` | Medium | Code Freeze -3d | Test/infrastructure work also requires the exception process (not exempt) |
| RL-12 | `release-notes-frozen.yaml` | High | Code Freeze +0d | Feature needs docs but Release Note field is empty at Code Freeze (submissions are now closed) |
| RL-13 | `post-code-freeze-exception.yaml` | Critical | Code Freeze +0d | Change was made after Code Freeze without going through the blocker exception process |
| RL-14 | `post-freeze-pr-jira-ref.yaml` | High | Code Freeze +0d | PR was merged to release branch after Code Freeze without referencing a Jira issue |
| RL-15 | `release-blocker-field-required.yaml` | High | Code Freeze +0d | Issue was modified after Code Freeze but Release Blocker field is empty |

---

## Sprint-Level

Sprint-cadence checks evaluated at planning or sprint boundaries.

| ID | File | Severity | Description |
|---|---|---|---|
| SP-01 | `allocation-imbalance.yaml` | Low | Sprint composition deviates more than 15% from the 40/40/20 allocation target |
| SP-02 | `no-subtasks.yaml` | Low | A subtask was created; team convention is to track all work as Stories, Tasks, or Spikes |
| SP-03 | `retro-action-not-tracked.yaml` | Low | Manual check: are retrospective action items created as Jira issues in the next sprint? |

---

## Rule Schema

Every YAML file follows this structure:

```yaml
id: kebab-case-identifier
name: Human-readable name
description: >
  What this rule enforces and why.

applies_to: [Feature, Epic, Story, ...]

# Field-hygiene rules have condition only:
condition:
  status: [...]
  field_empty: field_name

# Release-lifecycle rules also have trigger:
trigger:
  milestone: planning_freeze | feature_freeze | code_freeze
  days_before: N  # or days_after: N

action:
  type: alert | reminder | flag
  message: >
    Template with {key}, {status}, {days}, {milestone_date} placeholders.
  recipients: [assignee, manager, product_manager]

scope: org | team
verification: deterministic | heuristic | manual
enforcement: alert | comment | flag
severity: critical | high | medium | low

sources:
  - id: SOURCE-XX
    excerpt: "Relevant quote from the source"

date_added: YYYY-MM-DD
```
