# How We Work in Jira

Rules encoding our expectations for Jira hygiene and release delivery.
Each traces to internal process documents, leadership announcements, or
team conventions. Nothing here is invented.

The rules fall into two categories: **Field Hygiene** rules apply on
every evaluation regardless of release timing. **Release Lifecycle**
rules activate only within a milestone's trigger window (e.g., 3 days
before Code Freeze).

## Field Hygiene

### Ownership & Accountability

| ID | Expectation |
|---|---|
| `missing-assignee` | **Active issues need an assignee.** Anything in In Progress, Review, or Testing without an owner can't be tracked or held accountable. |
| `missing-team` | **Every non-Done issue needs a Team.** Org-level reporting and filtering depend on it. |
| `missing-component` | **Active issues need a Component.** Boards, filters, and dashboards slice work by domain. |
| `missing-product-manager` | **Features need a PM.** No product voice means no one guiding scope or acceptance. |
| `missing-contributors` | **Active features should list contributors.** Dependent teams need to know who's involved. |
| `missing-qa-contact` | **Epics need a QA contact.** Test planning needs a named owner. |
| `blocked-without-reason` | **Blocked flag requires a reason.** A flag without context doesn't help anyone resolve it. |
| `cross-team-dependency` | **Cross-team blockers in bad state need escalation.** Blocked by another team's issue that's in Backlog/New or unassigned. |

### Planning & Release Commitment

Target Version = PM request. Fix Version = engineering commitment.

| ID | Expectation |
|---|---|
| `missing-target-version` | **Active features need a Target Version.** Without one, the feature is invisible to release planning. |
| `missing-fix-version` | **Committed work needs a Fix Version.** Must be set at commit time, not after work is done. |
| `fix-version-without-target` | **Fix Version without Target Version is backwards.** Engineering committed without PM planning approval. |
| `labels-as-commitment` | **Labels are not Fix Version.** Use Fix Version for delivery commitments. |
| `premature-target-version` | **Issues in New shouldn't have Target Version.** No scoping has happened yet. |
| `version-mismatch` | **Target and Fix Version should match.** A mismatch means PM and engineering disagree on timing. |
| `missing-target-end` | **Features need a Target End date.** Drives timeline reporting and surfaces schedule risk. |

### Progress & Freshness

Stale issues erode trust in the board.

| ID | Expectation |
|---|---|
| `stale-in-progress` | **21+ days in In Progress with no update.** Either blocked (say so) or abandoned (move it). |
| `stale-refinement` | **Stuck in Refinement too long.** Move forward or descope. |
| `stale-status-summary` | **Status Summary older than 7 days.** Stakeholders get signal from this without interrupting engineers. |
| `stale-backlog-with-tv` | **60+ days in Backlog with a Target Version.** That's a false commitment. Activate or remove the version. |
| `missing-color-status` | **Active issues with Target Version need a color.** Red/Yellow/Green takes 10 seconds to set. |
| `color-summary-mismatch` | **Color and summary should agree.** Green + "blocked on dependency" is unreliable reporting. |
| `status-sprint-mismatch` | **Active status but no active sprint (or vice versa).** One of them is wrong. |
| `missing-story-points` | **Sprint issues need story points.** Velocity tracking and capacity planning depend on it. |
| `missing-activity-type` | **Issues need an Activity Type.** Drives 40/40/20 allocation tracking. |

### Documentation & Release Readiness

| ID | Expectation |
|---|---|
| `missing-docs-required` | **Features must indicate whether docs are needed.** Docs team plans capacity from this field. |
| `docs-required-no-link` | **Docs Required = Yes needs a linked doc issue.** Gives the docs team something to track. |
| `missing-release-notes` | **Release note fields can't be empty when docs are required.** Empty notes delay releases. |
| `missing-release-type` | **Features need a Release Type.** Dev Preview, Tech Preview, or GA determines support contract and doc scope. |
| `missing-products` | **Features need the Products field.** Organizes cross-product impact and release notes. |

### Structure & Hierarchy

| ID | Expectation |
|---|---|
| `missing-epic-parent` | **Stories, Tasks, and Spikes must link to an Epic.** Orphaned items are invisible to feature tracking. |
| `missing-strat-parent` | **Epics must link to a Feature or Initiative.** No link means no line of sight to strategy. |
| `component-hierarchy-mismatch` | **Child Component should match parent.** A mismatch means something is miscategorized. |
| `missing-issue-links` | **Features with dependencies should use Issue Links.** Makes relationships explicit and trackable. |
| `no-subtasks` | **Track work at Story/Task level, not subtasks.** Team convention. Subtasks don't surface in sprint boards. |

### Refinement & Sign-off

| ID | Expectation |
|---|---|
| `missing-rice-score` | **Features past Refinement need a RICE score.** Objective prioritization requires it. |
| `missing-rfe-link` | **Features should link to an approved RFE.** Connects delivery work to the intake process that justified it. |
| `missing-strat-creator-signoff` | **Features need `strat-creator-human-sign-off`.** Confirms a human reviewed AI-generated strategy content. |
| `missing-signoff-template` | **Features need a sign-off template.** The DP/TP/GA checklist of pre-delivery requirements. |
| `signoff-incomplete` | **All sign-off subtasks must be Done.** The checklist isn't optional. |

### Cross-System Integrity

| ID | Expectation |
|---|---|
| `missing-git-pr` | **Issues in Review/Testing need the PR field populated.** Traces code changes back to work items. |
| `missing-test-coverage` | **Issues should indicate test coverage status.** Feeds quality dashboards and release confidence. |

## Release Lifecycle

### Planning Freeze

Scope locks. Adding anything new requires a formal exception.

| ID | Expectation |
|---|---|
| `fix-version-at-planning-freeze` | **Features with Target Version must have Fix Version by freeze.** Converts PM request into engineering commitment. |
| `qg1-completeness` | **Quality Gate 1 must pass.** Required labels + PM, Assignee, Release Type, Target Version, Product, Components. Fail = excluded from GA. |
| `scope-exception-required` | **Post-freeze additions need a Scope Exception.** Hard cap: 5 per release. |
| `strat-review-required` | **Strat-review approval required.** Leadership sign-off on scope. |
| `strat-status-at-planning-freeze` | **STRAT issue must be at least To Do.** Can't be sitting unstarted in New. |

### Feature Freeze

Development complete. Features still in flight get descoped.

| ID | Expectation |
|---|---|
| `doc-draft-at-feature-freeze` | **Doc draft must be available to Tech Writers.** AI-generated first drafts are acceptable. |
| `feature-freeze-enforcement` | **In Progress at freeze = Fix Version removed.** The release moves on. |
| `pre-feature-freeze-status` | **Features must advance past In Progress.** Not complete = not in this release. |
| `pre-freeze-signoff` | **PM/UX sign-off required.** Confirms delivered work matches what was planned. |

### Code Freeze

Blocker fixes only. Every change requires an exception.

| ID | Expectation |
|---|---|
| `post-code-freeze-exception` | **All post-freeze changes need the exception process.** Release Blocker = Proposed, versions populated, risk assessment. 1-biz-day turnaround. |
| `post-freeze-pr-jira-ref` | **Every post-freeze PR must reference a Jira key.** 3.5 EA2 audit found only 32/54 human PRs had them. |
| `pre-code-freeze-release-pending` | **Features must be Release Pending before freeze.** Means all child work is complete. |
| `release-blocker-field-required` | **Post-freeze issues need Release Blocker field set.** Exception process can't evaluate without it. |
| `release-notes-frozen` | **Release notes must be submitted before freeze.** Late notes delay releases. |
| `test-infra-exception` | **Test changes need exceptions too.** "Just a test fix" doesn't bypass the gate. |
| `unresolved-blockers` | **All blockers must be resolved or reprioritized.** Carrying them into freeze creates churn. |

## Provenance

Every rule traces to one or more internal process documents. Each rule
YAML includes `sources` with document IDs and excerpts for verification.

## Adding rules

Rules are YAML files in `rules/field-hygiene/` or `rules/release-lifecycle/`.
Each specifies: `applies_to`, `condition`, `action`, `enforcement`, and
`sources`. To add one: write the YAML, add a test, run `pytest`, and
reference the source document that establishes the expectation.
