# How We Work in Jira

This is the integrated picture of how our Jira process works and what
we expect at each stage of the release cycle. Every rule here traces to a process doc,leadership announcement, or established team conventions.

- **Field Hygiene** rules check Jira data quality each time the engine runs.
- **Release Lifecycle** rules a are driven by release milestone windows (i.e fire 3 days before Code Freeze)

## Field Hygiene

### 👤 Ownership & Accountability

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

### 🎯 Planning & Release Commitment

- **Target Version** is set by Product Management. Requested release for delivery.
- **Fix Version** is set by Engineering. Committed release for delivery.

| ID | Expectation |
|---|---|
| `missing-target-version` | **Active features need a Target Version.** Without one, the feature is invisible to release planning. |
| `missing-fix-version` | **Fix Version** must be set when work begins, not after it ships. If **status** is In Progress or beyond, this field should already be populated. |
| `fix-version-without-target` | If **Fix Version** is set but **Target Version** is not, engineering has committed to delivery without PM planning approval. |
| `labels-as-commitment` | **Labels** should not be used as a substitute for **Fix Version**. Delivery commitments belong in **Fix Version**. |
| `premature-target-version` | If **status** = **New**, **Target Version** should not be set yet. No scoping or refinement has happened. |
| `version-mismatch` | **Target Version** and **Fix Version** should point to the same release. A mismatch means PM and engineering disagree on timing. |
| `missing-target-end` | **Features need a Target End date.** Drives timeline reporting and surfaces schedule risk. |

### ⏱️ Progress & Maintenance

Issues that haven't moved or been updated are either blocked or forgotten.
These rules surface both.

| ID | Expectation |
|---|---|
| `stale-in-progress` | If **status** = **In Progress** for 21+ days with no update (status change, comment, or field edit), the issue is likely stalled. Update it or move it. |
| `stale-refinement` | If **status** = **Refinement** for an extended period with no progress, the issue needs to move forward or be removed from scope. |
| `stale-status-summary` | **Status Summary** should be updated at least every 7 days on active work. This is how stakeholders get signal without interrupting engineers. |
| `stale-backlog-with-tv` | If **status** = **New/Backlog** for 60+ days but **Target Version** is set, that's a false commitment. Either activate the work or remove the version. |
| `missing-color-status` | If **Target Version** is set on an active issue, **Color Status** (Red/Yellow/Green) should be set too. Takes 10 seconds and gives stakeholders visibility. |
| `color-summary-mismatch` | **Color Status** and **Status Summary** should tell the same story. If color is Green but the summary says "blocked on dependency," reporting becomes unreliable. |
| `status-sprint-mismatch` | If **status** is active (In Progress, Review, Testing) the issue should be in an active sprint. If it's not, either the status or the sprint association is wrong. |
| `missing-story-points` | **Sprint issues need story points.** Velocity tracking and capacity planning depend on it. |
| `missing-activity-type` | **Issues need an Activity Type.** Drives 40/40/20 allocation tracking. |

### 📄 Documentation & Release Readiness

Documentation fields need to be set early enough for tech writers and
release managers to plan around them.

| ID | Expectation |
|---|---|
| `missing-docs-required` | **Features must indicate whether docs are needed.** Docs team plans capacity from this field. |
| `docs-required-no-link` | If **Docs Required** = **Yes**, there should be a linked documentation issue. This gives the docs team something to track and plan against. |
| `missing-release-notes` | If **Docs Required** = **Yes**, the **Release Note** fields must be populated. Empty release notes delay the release. |
| `missing-release-type` | **Features need a Release Type.** Dev Preview, Tech Preview, or GA determines support contract and doc scope. |
| `missing-products` | **Features need the Products field.** Organizes cross-product impact and release notes. |

### 🔗 Structure & Hierarchy

Our Jira hierarchy connects individual work items to strategic goals.
These rules ensure the links between levels actually exist.

| ID | Expectation |
|---|---|
| `missing-epic-parent` | **Stories, Tasks, and Spikes must link to an Epic.** Orphaned items are invisible to feature tracking. |
| `missing-strat-parent` | **Epics must link to a Feature or Initiative.** No link means no line of sight to strategy. |
| `component-hierarchy-mismatch` | **Child Component should match parent.** A mismatch means something is miscategorized. |
| `missing-issue-links` | **Features with dependencies should use Issue Links.** Makes relationships explicit and trackable. |
| `no-subtasks` | **Track work at Story/Task level, not subtasks.** Team convention. Subtasks don't surface in sprint boards. |

### ✅ Refinement & Sign-off

Features go through a refinement and approval process before delivery.
These rules check that the process is complete and traceable.

| ID | Expectation |
|---|---|
| `missing-rice-score` | **Features past Refinement need a RICE score.** Objective prioritization requires it. |
| `missing-rfe-link` | **Features should link to an approved RFE.** Connects delivery work to the intake process that justified it. |
| `missing-strat-creator-signoff` | **Features need `strat-creator-human-sign-off`.** Confirms a human reviewed AI-generated strategy content. |
| `missing-signoff-template` | **Features need a sign-off template.** The DP/TP/GA checklist of pre-delivery requirements. |
| `signoff-incomplete` | **All sign-off subtasks must be Done.** The checklist isn't optional. |

### 🔌 Cross-System Integrity

Some expectations span Jira and external systems like GitHub and docs
tooling. These rules check that those connections are in place.

| ID | Expectation |
|---|---|
| `missing-git-pr` | **Issues in Review/Testing need the PR field populated.** Traces code changes back to work items. |
| `missing-test-coverage` | **Issues should indicate test coverage status.** Feeds quality dashboards and release confidence. |

## Release Lifecycle

### 🔒 Planning Freeze

Planning Freeze is where release scope locks. After Planning Freeze, adding anything new
to the release requires a formal exception with a hard cap of 5 per release before requiring executive approval.

| ID | Expectation |
|---|---|
| `fix-version-at-planning-freeze` | If **Target Version** is set for the upcoming release, **Fix Version** must also be set by Planning Freeze. This is what converts a PM request into an engineering commitment. |
| `qg1-completeness` | Features must pass Quality Gate 1: the `strat-creator-human-sign-off` and `rp-qg1-pass` labels, plus **PM**, **Assignee**, **Release Type**, **Target Version**, **Product**, and **Components** must all be populated. Features that fail are excluded from GA scope. |
| `scope-exception-required` | Features added after Planning Freeze require a formal Release Scope Exception. Hard cap of 5 exceptions per release before requiring executive review. |
| `strat-review-required` | Features must have **strat-review** approval before Planning Freeze, confirming leadership sign-off on scope. |
| `strat-status-at-planning-freeze` | The associated STRAT issue must have **status** at least **To Do** or **In Progress** by Planning Freeze. It cannot still be sitting in **New**. |

### 🧊 Feature Freeze

Feature Freeze marks "development complete" and focus shifts to testing and
stabilization. If a feature is still in flight at Feature Freeze, it
gets removed from the release. Only applies to stable/GA releases (EA releases skip
this and go straight from Planning Freeze to Code Freeze).

| ID | Expectation |
|---|---|
| `doc-draft-at-feature-freeze` | If **Docs Required** = **Yes**, a doc draft must be available to Tech Writers by Feature Freeze. AI-generated first drafts are acceptable. |
| `feature-freeze-enforcement` | If **status** = **In Progress** at Feature Freeze, **Fix Version** is removed. The feature is no longer included in the release. |
| `pre-feature-freeze-status` | Features must advance past **In Progress** before Feature Freeze. If development is not complete, the feature is not in this release. |
| `pre-freeze-signoff` | **PM** and **UX** sign-off must be obtained before Feature Freeze, confirming delivered work matches what was planned. |

### ⛔ Code Freeze

After Code Freeze, only blocker fixes merge and every single change
goes through the exception process. Bug fixes that were ok to merge during the
Feature Freeze window now require formal approval too.

| ID | Expectation |
|---|---|
| `post-code-freeze-exception` | All changes after Code Freeze require the exception process: set **Release Blocker** = **Proposed**, populate **Affected Version** and **Fix Version**, and complete a risk assessment. Turnaround is 1 business day. |
| `post-freeze-pr-jira-ref` | Every PR merged after Code Freeze must reference a Jira key. In the 3.5 EA2 audit, only 32 of 54 human-authored PRs included one. |
| `pre-code-freeze-release-pending` | Features must move to **status** = **Release Pending** before Code Freeze. This status means all child work is complete and the feature is confirmed for release. |
| `release-blocker-field-required` | Post-freeze issues must have the **Release Blocker** field set. The exception process cannot evaluate or prioritize without it. |
| `release-notes-frozen` | **Release Notes** must be submitted before Code Freeze. Late notes delay the release. |
| `test-infra-exception` | Test and infrastructure changes also require the exception process after Code Freeze. "Just a test fix" does not bypass the gate. |
| `unresolved-blockers` | All identified blockers must be resolved or reprioritized before Code Freeze. Carrying unresolved blockers into freeze creates churn. |

## Provenance

Every rule traces to one or more internal process documents, and each rule's YAML file includes the specific source IDs and excerpts so you can verify where it came from.

## Adding rules

Rules live as YAML files in `rules/field-hygiene/` or
`rules/release-lifecycle/`. Each one specifies what issue types it
applies to, what conditions trigger a violation, what action to take,
and where the expectation comes from. To add a new rule, write the
YAML, add a test, run `pytest`, and cite the source document that
establishes the expectation.
