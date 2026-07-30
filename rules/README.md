# How We Work in Jira

Rules that encode our expectations for Jira hygiene and release delivery.
Each traces back to org-wide process documents, leadership announcements,
or established team conventions. Nothing here is invented.

## How rules work

| Level | Meaning |
|---|---|
| **Alert** | Actively raised. Release-blocking or time-sensitive. |
| **Comment** | A Jira comment prompting the owner to act. |
| **Flag** | Marked for review. No direct notification. |

Field Hygiene rules apply on every evaluation, regardless of release
timing. Release Lifecycle rules activate only within a milestone's
trigger window.

---

## Field Hygiene

### Ownership & Accountability

| ID | Rule | What we expect |
|---|---|---|
| `blocked-without-reason` | Blocked Without Reason | If the Blocked flag is set, explain why. A flag without context doesn't help anyone resolve it. |
| `cross-team-dependency` | Cross-Team Dependency in Bad State | If you're blocked by another team's issue that's in Backlog/New or unassigned, that's a risk needing escalation. |
| `missing-assignee` | Missing Assignee on Active Issue | Issues in In Progress, Review, or Testing must have an assignee. Unowned active work is invisible work. |
| `missing-component` | Missing Component | Active issues need a Component. This is how boards, filters, and dashboards slice work by domain. |
| `missing-contributors` | Missing Contributors on Feature | Active features should list contributors so dependent teams know who's involved. |
| `missing-product-manager` | Missing Product Manager on Feature | Features must have a PM. Without one, there's no product voice guiding scope or acceptance. |
| `missing-qa-contact` | Missing QA Contact on Epic | Epics need a QA contact so test planning has a named owner. |
| `missing-team` | Missing Team Field | Every non-Done issue must indicate which team owns it. Org-level reporting depends on it. |

### Planning & Release Commitment

Target Version = PM request. Fix Version = engineering commitment.

| ID | Rule | What we expect |
|---|---|---|
| `fix-version-without-target` | Fix Version Without Target Version | Engineering committed without PM planning approval. That's backwards. |
| `labels-as-commitment` | Labels Used as Commitment Substitute | Labels are not Fix Version. Use Fix Version for delivery commitments. |
| `missing-fix-version` | Missing Fix Version on Committed Work | Fix Version must be set at commit time, not after work is done. |
| `missing-target-end` | Missing Target End on Feature | Features need a Target End date for timeline reporting and schedule risk. |
| `missing-target-version` | Missing Target Version on Feature | No Target Version means the feature is invisible to release planning. |
| `premature-target-version` | Premature Release Target | Issues in New shouldn't have Target Version yet. No scoping has happened. |
| `version-mismatch` | Inconsistent Target vs Fix Version | When both are set, they should point to the same release. A mismatch means PM and engineering disagree. |

### Progress & Freshness

Stale issues erode trust in the board.

| ID | Rule | What we expect |
|---|---|---|
| `color-summary-mismatch` | Color Status / Summary Mismatch | Color says Green but summary describes problems? Keep them consistent. |
| `missing-activity-type` | Missing Activity Type | Drives 40/40/20 allocation tracking. Without it, investment balance reporting is blind. |
| `missing-color-status` | Missing Color Status | Active issues with Target Version need Red/Yellow/Green. Takes 10 seconds to set. |
| `missing-story-points` | Missing Story Points in Sprint | Velocity tracking and capacity planning require story points on sprint issues. |
| `stale-backlog-with-tv` | Stale Backlog with Target Version | 60+ days in New/Backlog with a Target Version is a false commitment. Activate or remove the version. |
| `stale-in-progress` | Stale In Progress | 21+ days in In Progress with no update. Either blocked (say so) or abandoned (move it). |
| `stale-refinement` | Stale Refinement | Stuck in Refinement too long. Move forward or descope. |
| `stale-status-summary` | Stale or Missing Status Summary | Status Summary should be updated at least every 7 days on active work. |
| `status-sprint-mismatch` | Status/Sprint Mismatch | Active status but not in an active sprint (or vice versa). One of them is wrong. |

### Documentation & Release Readiness

| ID | Rule | What we expect |
|---|---|---|
| `docs-required-no-link` | Docs Required but No Doc Link | Docs Required = Yes but no linked documentation issue for the docs team to track. |
| `missing-docs-required` | Missing Docs Required Field | Every feature must indicate whether docs are needed. Docs team plans capacity from this. |
| `missing-products` | Missing Products Field on Feature | Products field organizes cross-product impact and release notes. |
| `missing-release-notes` | Missing Release Note Fields | Docs Required = Yes but release note content is empty. This delays releases. |
| `missing-release-type` | Missing Release Type on Feature | Dev Preview, Tech Preview, or GA. Determines support contract and doc requirements. |

### Structure & Hierarchy

| ID | Rule | What we expect |
|---|---|---|
| `component-hierarchy-mismatch` | Component Mismatch Across Hierarchy | Child issue Component differs from parent. Something is miscategorized. |
| `missing-epic-parent` | Missing Epic Parent Link | Stories, Tasks, and Spikes must link to an Epic. Orphaned items are invisible to feature tracking. |
| `missing-issue-links` | Missing Issue Links on Feature | Features with dependencies should use Issue Links to make relationships explicit. |
| `missing-strat-parent` | Missing Feature Parent Link on Epic | Epics must link to a Feature or Initiative. No link means no line of sight to strategy. |
| `no-subtasks` | No Subtask Usage | Team convention: track work at Story/Task level. Subtasks don't surface in sprint boards. |

### Refinement & Sign-off

| ID | Rule | What we expect |
|---|---|---|
| `missing-rfe-link` | Missing RFE Link on Feature | Features should link to an approved RHAIRFE issue connecting delivery to intake. |
| `missing-rice-score` | Missing RICE Score on Feature | Features past Refinement need a RICE score for objective prioritization. |
| `missing-signoff-template` | Feature Signoff Template Missing | Features must have a cloned sign-off template (DP/TP/GA checklist). |
| `missing-strat-creator-signoff` | Missing Strat-Creator Human Sign-Off | The `strat-creator-human-sign-off` label confirms a human reviewed AI-generated strategy content. |
| `signoff-incomplete` | Incomplete Sign-Off on Feature | All sign-off template subtasks must be Done before the feature is delivered. |

### Cross-System Integrity

| ID | Rule | What we expect |
|---|---|---|
| `missing-git-pr` | Missing Git Pull Request Field | Issues in Review or Testing should have the PR field populated. Traces code to work items. |
| `missing-test-coverage` | Missing Test Coverage Field | Test coverage status feeds quality dashboards and release confidence. |

---

## Release Lifecycle

### Planning Freeze

Scope locks. Everything in the release needs ownership, commitment, and
strategy approval.

| ID | Rule | What we expect |
|---|---|---|
| `fix-version-at-planning-freeze` | Fix Version Required | Features with Target Version must have Fix Version by Planning Freeze. Converts PM request into engineering commitment. |
| `qg1-completeness` | Quality Gate 1 Completeness | Required: `strat-creator-human-sign-off` + `rp-qg1-pass` labels, PM, Assignee, Release Type, Target Version, Product, Components. Fail = excluded from GA scope. |
| `scope-exception-required` | Scope Exception Required | Features added after Planning Freeze need a Release Scope Exception. Hard cap: 5 per release. |
| `strat-review-required` | Strat-Review Approval Required | Features must have strat-review approval confirming leadership sign-off on scope. |
| `strat-status-at-planning-freeze` | STRAT Status At Least To Do | The associated STRAT issue must be at least To Do or In Progress, not unstarted. |

### Feature Freeze

Development complete. Stable code, documentation started. Features still
in flight get descoped.

| ID | Rule | What we expect |
|---|---|---|
| `doc-draft-at-feature-freeze` | Doc Draft Required | Features with Docs Required = Yes must have a draft available to Tech Writers. |
| `feature-freeze-enforcement` | Feature Freeze Enforcement | Features still In Progress at freeze have Fix Version removed. The release moves on. |
| `pre-feature-freeze-status` | Features Must Advance | Features must move past In Progress before freeze. Not complete = not in this release. |
| `pre-freeze-signoff` | PM/UX Signoff Required | PM and UX sign-off confirms delivered work matches what was planned. |

### Code Freeze

Blocker fixes only. Every change requires an exception.

| ID | Rule | What we expect |
|---|---|---|
| `post-code-freeze-exception` | Exception Process Required | All post-freeze changes need: Release Blocker = Proposed, versions populated, risk assessment. 1-biz-day turnaround. |
| `post-freeze-pr-jira-ref` | PR Must Reference Jira | Every PR merged after freeze must reference a Jira key. 3.5 EA2 audit: only 32/54 human PRs had keys. |
| `pre-code-freeze-release-pending` | Release Pending Before Freeze | Features must be in Release Pending before Code Freeze, meaning all child work is complete. |
| `release-blocker-field-required` | Release Blocker Field Required | Post-freeze issues need the Release Blocker field set for the exception process to evaluate them. |
| `release-notes-frozen` | Release Notes Frozen | Release notes must be submitted before Code Freeze. Late notes delay releases. |
| `test-infra-exception` | Test Changes Need Exceptions Too | Test and infra changes also require the exception process. "Just a test fix" doesn't bypass the gate. |
| `unresolved-blockers` | Unresolved Blockers | All blockers must be resolved or reprioritized before freeze. Unresolved blockers create churn. |

---

## Provenance

Every rule traces to one or more internal process documents (Confluence
pages, leadership announcements, team playbooks, or cross-team tooling).
Each rule YAML includes `sources` with document IDs and excerpts for
verification.

---

## Adding rules

Rules are YAML files in `rules/field-hygiene/` or `rules/release-lifecycle/`.
Each specifies: `applies_to`, `condition`, `action`, `enforcement`, and
`sources`. To add one: write the YAML, add a test, run `pytest`, and
reference the source document that establishes the expectation.
