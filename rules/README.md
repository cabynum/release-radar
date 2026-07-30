# Rules

57 YAML rules evaluated by the engine, organized into two categories.

## Field Hygiene (41 rules)

Data correctness checks that run on every evaluation. These fire
regardless of where you are in the release cycle.

| Rule | What it checks |
|---|---|
| `blocked-without-reason` | Blocked = true but no Blocked Reason |
| `color-summary-mismatch` | Color Status word doesn't match Status Summary text |
| `component-hierarchy-mismatch` | Child issue Component differs from parent |
| `cross-team-dependency` | Blocked by another team's issue that is in Backlog/New or unassigned |
| `docs-required-no-link` | Docs Required = Yes but no linked documentation issue |
| `fix-version-without-target` | Fix Version set but no Target Version (committed without PM planning) |
| `labels-as-commitment` | Labels used instead of Fix Version for delivery commitment |
| `missing-activity-type` | No Activity Type set (breaks 40/40/20 tracking) |
| `missing-assignee` | Active issue with no assignee |
| `missing-color-status` | Active issue with Target Version but no Color Status |
| `missing-component` | Active issue with no Component |
| `missing-contributors` | Active feature with no Contributors field |
| `missing-docs-required` | Feature missing Docs Required field |
| `missing-epic-parent` | Story/Task/Spike with no Epic Link |
| `missing-fix-version` | Committed work with no Fix Version |
| `missing-git-pr` | Issue in Review/Testing with no Git Pull Request field |
| `missing-issue-links` | Feature with dependencies but no Issue Links |
| `missing-product-manager` | Feature with no Product Manager |
| `missing-products` | Active feature with no Products field |
| `missing-qa-contact` | Active Epic with no QA Contact |
| `missing-release-notes` | Docs Required = Yes but Release Note fields empty |
| `missing-release-type` | Feature with no Release Type (GA/TP/DP) |
| `missing-rfe-link` | Feature not linked to an approved RHAIRFE issue |
| `missing-rice-score` | Feature in Refinement+ with no RICE score |
| `missing-signoff-template` | Feature with no cloned sign-off template (DP/TP/GA) |
| `missing-strat-creator-signoff` | Feature missing `strat-creator-human-sign-off` label |
| `missing-story-points` | Issue in active sprint with no story points |
| `missing-strat-parent` | Active Epic with no parent Feature/Initiative link |
| `missing-target-end` | Feature with no Target End date |
| `missing-target-version` | Active feature with no Target Version |
| `missing-team` | Non-Done issue with no Team field |
| `missing-test-coverage` | Work item with no Test Coverage indication |
| `no-subtasks` | Subtask exists (team convention: track work at story/task level) |
| `premature-target-version` | Issue in New with Target Version already set |
| `signoff-incomplete` | Sign-off template subtasks not all Done |
| `stale-backlog-with-tv` | Feature in New/Backlog 60+ days with Target Version |
| `stale-in-progress` | In Progress 21+ days with no update |
| `stale-refinement` | Stuck in Refinement too long |
| `stale-status-summary` | Status Summary not updated in 7+ days |
| `status-sprint-mismatch` | Active status but not in an active sprint |
| `version-mismatch` | Target Version and Fix Version point to different releases |

## Release Lifecycle (16 rules)

Org-policy checks that activate within milestone trigger windows.
Each rule fires only when its milestone date is approaching or has passed.

### Planning Freeze

| Rule | What it checks |
|---|---|
| `fix-version-at-planning-freeze` | Features with Target Version must have Fix Version applied |
| `qg1-completeness` | Features must pass Quality Gate 1 (required labels + fields) |
| `scope-exception-required` | Features added after Planning Freeze need a scope exception |
| `strat-review-required` | Features must have strat-review approval |
| `strat-status-at-planning-freeze` | STRAT status must be at least To Do or In Progress |

### Feature Freeze

| Rule | What it checks |
|---|---|
| `doc-draft-at-feature-freeze` | Features with Docs Required = Yes must have a doc draft |
| `feature-freeze-enforcement` | Features still In Progress will have Fix Version removed |
| `pre-feature-freeze-status` | Features must advance past In Progress |
| `pre-freeze-signoff` | PM/UX sign-off must be obtained |

### Code Freeze

| Rule | What it checks |
|---|---|
| `post-code-freeze-exception` | All post-freeze changes need the blocker exception process |
| `post-freeze-pr-jira-ref` | PRs merged after freeze must reference a Jira key |
| `pre-code-freeze-release-pending` | Features must move to Release Pending before freeze |
| `release-blocker-field-required` | Post-freeze issues need Release Blocker field set |
| `release-notes-frozen` | Release notes must be submitted before freeze |
| `test-infra-exception` | Test changes also require the exception process |
| `unresolved-blockers` | All blockers must be resolved or re-prioritized |
