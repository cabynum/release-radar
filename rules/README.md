# Rules

57 YAML rules evaluated by the engine, organized into two categories.

## Field Hygiene (41 rules)

Data correctness checks that run on every evaluation. These fire
regardless of where you are in the release cycle.

| Rule | What it checks | Severity |
|---|---|---|
| `blocked-without-reason` | Blocked = true but no Blocked Reason | medium |
| `color-summary-mismatch` | Color Status word doesn't match Status Summary text | low |
| `component-hierarchy-mismatch` | Child issue Component differs from parent | low |
| `cross-team-dependency` | Blocked by another team's issue that is in Backlog/New or unassigned | high |
| `docs-required-no-link` | Docs Required = Yes but no linked documentation issue | medium |
| `fix-version-without-target` | Fix Version set but no Target Version (committed without PM planning) | low |
| `labels-as-commitment` | Labels used instead of Fix Version for delivery commitment | low |
| `missing-activity-type` | No Activity Type set (breaks 40/40/20 tracking) | low |
| `missing-assignee` | Active issue with no assignee | high |
| `missing-color-status` | Active issue with Target Version but no Color Status | medium |
| `missing-component` | Active issue with no Component | medium |
| `missing-contributors` | Active feature with no Contributors field | low |
| `missing-docs-required` | Feature missing Docs Required field | medium |
| `missing-epic-parent` | Story/Task/Spike with no Epic Link | medium |
| `missing-fix-version` | Committed work with no Fix Version | high |
| `missing-git-pr` | Issue in Review/Testing with no Git Pull Request field | medium |
| `missing-issue-links` | Feature with dependencies but no Issue Links | low |
| `missing-product-manager` | Feature with no Product Manager | high |
| `missing-products` | Active feature with no Products field | medium |
| `missing-qa-contact` | Active Epic with no QA Contact | low |
| `missing-release-notes` | Docs Required = Yes but Release Note fields empty | medium |
| `missing-release-type` | Feature with no Release Type (GA/TP/DP) | high |
| `missing-rfe-link` | Feature not linked to an approved RHAIRFE issue | medium |
| `missing-rice-score` | Feature in Refinement+ with no RICE score | medium |
| `missing-signoff-template` | Feature with no cloned sign-off template (DP/TP/GA) | medium |
| `missing-strat-creator-signoff` | Feature missing `strat-creator-human-sign-off` label | medium |
| `missing-story-points` | Issue in active sprint with no story points | medium |
| `missing-strat-parent` | Active Epic with no parent Feature/Initiative link | medium |
| `missing-target-end` | Feature with no Target End date | low |
| `missing-target-version` | Active feature with no Target Version | high |
| `missing-team` | Non-Done issue with no Team field | high |
| `missing-test-coverage` | Work item with no Test Coverage indication | low |
| `no-subtasks` | Subtask exists (team convention: track work at story/task level) | low |
| `premature-target-version` | Issue in New with Target Version already set | low |
| `signoff-incomplete` | Sign-off template subtasks not all Done | medium |
| `stale-backlog-with-tv` | Feature in New/Backlog 60+ days with Target Version | medium |
| `stale-in-progress` | In Progress 21+ days with no update | medium |
| `stale-refinement` | Stuck in Refinement too long | medium |
| `stale-status-summary` | Status Summary not updated in 7+ days | medium |
| `status-sprint-mismatch` | Active status but not in an active sprint | medium |
| `version-mismatch` | Target Version and Fix Version point to different releases | medium |

## Release Lifecycle (16 rules)

Org-policy checks that activate within milestone trigger windows.
Each rule fires only when its milestone date is approaching or has passed.

### Planning Freeze

| Rule | What it checks | Severity |
|---|---|---|
| `fix-version-at-planning-freeze` | Features with Target Version must have Fix Version applied | critical |
| `qg1-completeness` | Features must pass Quality Gate 1 (required labels + fields) | critical |
| `scope-exception-required` | Features added after Planning Freeze need a scope exception | high |
| `strat-review-required` | Features must have strat-review approval | high |
| `strat-status-at-planning-freeze` | STRAT status must be at least To Do or In Progress | high |

### Feature Freeze

| Rule | What it checks | Severity |
|---|---|---|
| `doc-draft-at-feature-freeze` | Features with Docs Required = Yes must have a doc draft | medium |
| `feature-freeze-enforcement` | Features still In Progress will have Fix Version removed | critical |
| `pre-feature-freeze-status` | Features must advance past In Progress | critical |
| `pre-freeze-signoff` | PM/UX sign-off must be obtained | high |

### Code Freeze

| Rule | What it checks | Severity |
|---|---|---|
| `post-code-freeze-exception` | All post-freeze changes need the blocker exception process | critical |
| `post-freeze-pr-jira-ref` | PRs merged after freeze must reference a Jira key | high |
| `pre-code-freeze-release-pending` | Features must move to Release Pending before freeze | critical |
| `release-blocker-field-required` | Post-freeze issues need Release Blocker field set | high |
| `release-notes-frozen` | Release notes must be submitted before freeze | high |
| `test-infra-exception` | Test changes also require the exception process | medium |
| `unresolved-blockers` | All blockers must be resolved or re-prioritized | critical |
