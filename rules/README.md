# How We Work in Jira

This is the integrated picture of how our Jira process works and what
we expect at each stage of the release cycle. Every rule here traces to a process doc,leadership announcement, or established team conventions.

- **Field Hygiene** rules check Jira data quality each time the engine runs.
- **Release Lifecycle** rules a are driven by release milestone windows (i.e fire 3 days before Code Freeze)

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

- **Target Version** is set by Product Management. Requested release for delivery.
- **Fix Version** is set by Engineering. Committed release for delivery.

| ID | Expectation |
|---|---|
| `missing-target-version` | **Active features need a Target Version.** Without one, the feature is invisible to release planning. |
| `missing-fix-version` | **Committed work needs a Fix Version.** Must be set at commit time, not after work is done. |
| `fix-version-without-target` | **Fix Version without Target Version is backwards.** Engineering committed without PM planning approval. |
| `labels-as-commitment` | **Labels are not Fix Version.** Use Fix Version for delivery commitments. |
| `premature-target-version` | **Issues in New shouldn't have Target Version.** No scoping has happened yet. |
| `version-mismatch` | **Target and Fix Version should match.** A mismatch means PM and engineering disagree on timing. |
| `missing-target-end` | **Features need a Target End date.** Drives timeline reporting and surfaces schedule risk. |

### Progress & Maintenance

Issues that haven't moved or been updated are either blocked or forgotten.
These rules surface both.

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

Documentation fields need to be set early enough for tech writers and
release managers to plan around them.

| ID | Expectation |
|---|---|
| `missing-docs-required` | **Features must indicate whether docs are needed.** Docs team plans capacity from this field. |
| `docs-required-no-link` | **Docs Required = Yes needs a linked doc issue.** Gives the docs team something to track. |
| `missing-release-notes` | **Release note fields can't be empty when docs are required.** Empty notes delay releases. |
| `missing-release-type` | **Features need a Release Type.** Dev Preview, Tech Preview, or GA determines support contract and doc scope. |
| `missing-products` | **Features need the Products field.** Organizes cross-product impact and release notes. |

### Structure & Hierarchy

Our Jira hierarchy connects individual work items to strategic goals.
These rules ensure the links between levels actually exist.

| ID | Expectation |
|---|---|
| `missing-epic-parent` | **Stories, Tasks, and Spikes must link to an Epic.** Orphaned items are invisible to feature tracking. |
| `missing-strat-parent` | **Epics must link to a Feature or Initiative.** No link means no line of sight to strategy. |
| `component-hierarchy-mismatch` | **Child Component should match parent.** A mismatch means something is miscategorized. |
| `missing-issue-links` | **Features with dependencies should use Issue Links.** Makes relationships explicit and trackable. |
| `no-subtasks` | **Track work at Story/Task level, not subtasks.** Team convention. Subtasks don't surface in sprint boards. |

### Refinement & Sign-off

Features go through a refinement and approval process before delivery.
These rules check that the process is complete and traceable.

| ID | Expectation |
|---|---|
| `missing-rice-score` | **Features past Refinement need a RICE score.** Objective prioritization requires it. |
| `missing-rfe-link` | **Features should link to an approved RFE.** Connects delivery work to the intake process that justified it. |
| `missing-strat-creator-signoff` | **Features need `strat-creator-human-sign-off`.** Confirms a human reviewed AI-generated strategy content. |
| `missing-signoff-template` | **Features need a sign-off template.** The DP/TP/GA checklist of pre-delivery requirements. |
| `signoff-incomplete` | **All sign-off subtasks must be Done.** The checklist isn't optional. |

### Cross-System Integrity

Some expectations span Jira and external systems like GitHub and docs
tooling. These rules check that those connections are in place.

| ID | Expectation |
|---|---|
| `missing-git-pr` | **Issues in Review/Testing need the PR field populated.** Traces code changes back to work items. |
| `missing-test-coverage` | **Issues should indicate test coverage status.** Feeds quality dashboards and release confidence. |

## Release Lifecycle

### Planning Freeze

Planning Freeze is where release scope locks. After Planning Freeze, adding anything new
to the release requires a formal exception with a hard cap of 5 per release before requiring executive approval.

| ID | Expectation |
|---|---|
| `fix-version-at-planning-freeze` | **Features with Target Version must have Fix Version by freeze.** Converts PM request into engineering commitment. |
| `qg1-completeness` | **Quality Gate 1 must pass.** Required labels + PM, Assignee, Release Type, Target Version, Product, Components. Fail = excluded from GA. |
| `scope-exception-required` | **Post-freeze additions need a Scope Exception.** Hard cap: 5 per release. |
| `strat-review-required` | **Strat-review approval required.** Leadership sign-off on scope. |
| `strat-status-at-planning-freeze` | **STRAT issue must be at least To Do.** Can't be sitting unstarted in New. |

### Feature Freeze

Feature Freeze marks "development complete" and focus shifts to testing and
stabilization. If a feature is still in flight at Feature Freeze, it
gets removed from the release. Only applies to stable/GA releases (EA releases skip
this and go straight from Planning Freeze to Code Freeze).

| ID | Expectation |
|---|---|
| `doc-draft-at-feature-freeze` | **Doc draft must be available to Tech Writers.** AI-generated first drafts are acceptable. |
| `feature-freeze-enforcement` | **In Progress at freeze = Fix Version removed.** The release moves on. |
| `pre-feature-freeze-status` | **Features must advance past In Progress.** Not complete = not in this release. |
| `pre-freeze-signoff` | **PM/UX sign-off required.** Confirms delivered work matches what was planned. |

### Code Freeze

After Code Freeze, only blocker fixes merge and every single change
goes through the exception process. Bug fixes that were ok to merge during the
Feature Freeze window now require formal approval too.

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

Every rule traces to one or more internal process documents, and each rule's YAML file includes the specific source IDs and excerpts so you can verify where it came from.

## Adding rules

Rules live as YAML files in `rules/field-hygiene/` or
`rules/release-lifecycle/`. Each one specifies what issue types it
applies to, what conditions trigger a violation, what action to take,
and where the expectation comes from. To add a new rule, write the
YAML, add a test, run `pytest`, and cite the source document that
establishes the expectation.
