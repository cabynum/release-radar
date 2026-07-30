# How We Work in Jira

57 rules that encode our team's expectations for Jira hygiene and
release delivery. Each rule is sourced from org-wide process documents,
leadership announcements, or established team conventions. Nothing here
is invented.

This is meant to be the integrated picture: what we expect of issues
day-to-day, what the release cycle demands at each milestone, and how
we hold ourselves accountable to both.

## How rules work

Every rule has an **enforcement level** that determines how findings
surface:

| Level | Meaning |
|---|---|
| **Alert** | Actively raised. Release-blocking or time-sensitive. |
| **Comment** | A Jira comment prompting the owner to act. |
| **Flag** | Marked for review. No direct notification. |

Rules in the **Field Hygiene** section run continuously. Rules in the
**Release Lifecycle** section activate only within a milestone's trigger
window (e.g., 3 days before Planning Freeze).

---

## Field Hygiene (41 rules)

These are the baseline expectations for any issue in our Jira projects.
They run on every evaluation regardless of where you are in the release
cycle.

### Ownership & Accountability

Every piece of work needs a clear owner and organizational home. Without
these, work can't be tracked, reported on, or held accountable.

| Rule | What we expect |
|---|---|
| **Missing Assignee on Active Issue** | Any issue that's moved to In Progress, Review, or Testing must have an assignee. Unowned active work is invisible work. |
| **Missing Team Field** | Every non-Done issue must indicate which team owns it. This is how org-level reporting and filtering work. |
| **Missing Component** | Active issues need a Component set. This is how boards, filters, and dashboards slice work by domain. |
| **Missing Product Manager on Feature** | Features must have a PM assigned. Without one, there's no product voice guiding scope, priority, or acceptance. |
| **Missing Contributors on Feature** | Active features should list contributors so stakeholders and dependent teams know who's involved. |
| **Missing QA Contact on Epic** | Epics need a QA contact so test planning and quality gates have a named owner. |

### Planning & Release Commitment

Target Version and Fix Version are the two key signals for release
planning. Target Version is a PM request ("we'd like this in 3.6"). Fix
Version is an engineering commitment ("we will deliver this in 3.6").
Getting these right is how we avoid surprises at freeze time.

| Rule | What we expect |
|---|---|
| **Missing Target Version on Feature** | Active features must have a Target Version. Without one, there's no release association and the feature is invisible to release planning. |
| **Missing Fix Version on Committed Work** | Fix Version must be set at commit time, not after work is done. Features in In Progress or beyond without Fix Version indicate work advancing without delivery agreement. |
| **Fix Version Without Target Version** | If Fix Version is set but Target Version isn't, engineering has committed without PM planning approval. That's backwards. |
| **Labels Used as Commitment Substitute** | Labels are not a substitute for Fix Version. Use Fix Version for delivery commitments. |
| **Premature Release Target** | Issues still in New shouldn't have Target Version set yet. It creates false signals in release planning before any scoping has happened. |
| **Inconsistent Target Version vs Fix Version** | When both are set, they should point to the same release. A mismatch means PM and engineering disagree on timing. |
| **Missing Target End on Feature** | Features need a Target End date. This is what drives timeline reporting and helps identify schedule risk early. |

### Progress & Freshness

Stale issues erode trust in the board. If something hasn't moved or been
updated, it's either blocked (and should say so) or abandoned (and should
be moved). These rules enforce currency.

| Rule | What we expect |
|---|---|
| **Stale In Progress** | Issues in In Progress for 21+ days with no update (status change, comment, or field edit) are likely stalled. Update or move them. |
| **Stale Refinement** | Issues stuck in Refinement too long need attention. Either they're ready to move forward or they need to be descoped. |
| **Stale or Missing Status Summary** | Status Summary should be updated at least every 7 days on active work. This is how stakeholders get signal without interrupting engineers. |
| **Stale Backlog with Target Version** | Features sitting in New or Backlog for 60+ days with a Target Version are false commitments. Either activate them or remove the version. |
| **Missing Color Status** | Active issues with Target Version but no Color Status leave stakeholders guessing at health. Red/Yellow/Green takes 10 seconds to set. |
| **Color Status / Status Summary Mismatch** | When the color says Green but the summary describes problems (or vice versa), reporting becomes unreliable. Keep them consistent. |
| **Status/Sprint Mismatch** | Issues in an active status (In Progress, Review, Testing) should be in an active sprint. If they're not, either the status or the sprint association is wrong. |
| **Missing Story Points in Sprint** | Issues in an active sprint need story points for velocity tracking and capacity planning to work. |
| **Missing Activity Type** | Activity Type (TDQ, New Feature, L&E) drives 40/40/20 allocation tracking. Without it, investment balance reporting is blind. |

### Documentation & Release Readiness

Documentation isn't an afterthought. These rules ensure doc-related
fields are populated early enough for tech writers and release managers
to plan.

| Rule | What we expect |
|---|---|
| **Missing Docs Required Field on Feature** | Every feature must indicate whether docs are needed. This is how the docs team plans capacity. |
| **Docs Required but No Doc Link** | If you said docs are required, there should be a linked documentation issue so the docs team can track it. |
| **Missing Release Note Fields** | When docs are required, release note content must be provided. Leaving this empty delays releases. |
| **Missing Release Type on Feature** | Features must declare their release type (Dev Preview, Tech Preview, or GA). This determines the support contract and documentation requirements. |
| **Missing Products Field on Feature** | Active features need the Products field set. This is how cross-product impact and release notes are organized. |

### Structure & Hierarchy

Jira's hierarchy (Initiative > Feature > Epic > Story/Task) is how we
connect individual work items to strategic goals. These rules ensure the
links exist.

| Rule | What we expect |
|---|---|
| **Missing Epic Parent Link** | Stories, Tasks, and Spikes must be linked to an Epic. Orphaned work items are invisible to feature-level tracking. |
| **Missing Feature Parent Link on Epic** | Epics must link to a Feature or Initiative. Without this, there's no line of sight from execution to strategy. |
| **Component Mismatch Across Hierarchy** | When a child issue's Component differs from its parent, something is miscategorized. This creates confusion in board views and reporting. |
| **Missing Issue Links on Feature** | Features with dependencies should use Jira Issue Links to make those relationships explicit and trackable. |
| **No Subtask Usage** | Our team convention is to track work at the Story/Task level, not as subtasks. Subtasks don't surface well in sprint boards or reports. |

### Refinement & Sign-off

Features go through a refinement and approval process before delivery.
These rules ensure that process is complete and traceable.

| Rule | What we expect |
|---|---|
| **Missing RICE Score on Feature** | Features past Refinement should have a RICE score (Reach, Impact, Confidence, Effort). This is how we objectively prioritize. |
| **Missing RFE Link on Feature** | Features should link to an approved RHAIRFE issue. This connects delivery work to the RFE intake process that justified it. |
| **Missing Strat-Creator Human Sign-Off** | Features need the `strat-creator-human-sign-off` label confirming a human reviewed the AI-generated strategy content. |
| **Feature Signoff Template Missing** | Features must have a cloned sign-off template (DP/TP/GA) with the checklist of pre-delivery requirements. |
| **Incomplete Sign-Off on Feature** | All subtasks in the sign-off template must be completed before a feature can be considered delivered. |

### Cross-System Integrity

Some expectations span Jira and external systems (GitHub, docs tooling,
cross-team boards). These rules check that those connections are sound.

| Rule | What we expect |
|---|---|
| **Missing Git Pull Request Field** | Issues in Review or Testing should have the Git Pull Request field populated. This is how we trace code changes back to Jira work items. |
| **Cross-Team Dependency in Bad State** | If you're blocked by another team's issue and that issue is in Backlog/New or unassigned, that's a risk that needs escalation, not silence. |
| **Blocked Without Blocked Reason** | If the Blocked flag is set, there must be a Blocked Reason explaining why. A flag without context doesn't help anyone resolve it. |
| **Missing Test Coverage Field** | Work items should indicate their test coverage status. This feeds quality dashboards and release confidence. |

---

## Release Lifecycle (16 rules)

These rules activate within milestone trigger windows. They encode the
expectations that tighten as we approach each release gate. Each fires
only when its milestone date is approaching or has passed.

### Planning Freeze

The point where release scope locks. After this, everything in the
release should have clear ownership, commitment signals, and strategy
approval. Adding anything new requires a formal exception.

| Rule | What we expect |
|---|---|
| **Fix Version Required at Planning Freeze** | By Planning Freeze, all features with Target Version for the release must have Fix Version applied. This converts a PM request into an engineering commitment. |
| **Quality Gate 1 Completeness** | Features must pass QG1: the `strat-creator-human-sign-off` and `rp-qg1-pass` labels, plus all mandatory fields (PM, Assignee, Release Type, Target Version, Product, Components). Features failing QG1 are excluded from GA scope. |
| **Post-Planning-Freeze Scope Exception Required** | Features added after Planning Freeze require a Release Scope Exception. Hard cap of 5 exceptions per release. |
| **Strat-Review Approval Required** | Features must have strat-review approval before Planning Freeze. This confirms leadership sign-off on scope. |
| **STRAT Status Must Be At Least To Do** | By Planning Freeze, the associated STRAT issue must be at least in To Do or In Progress, not sitting unstarted in New. |

### Feature Freeze

Development must be complete. Stable, testable code with documentation
started. Features still in flight get descoped.

| Rule | What we expect |
|---|---|
| **Doc Draft Required at Feature Freeze** | Features where Docs Required = Yes must have a doc draft available to Tech Writers. AI-generated first drafts are acceptable. |
| **Feature Freeze Enforcement** | Features still In Progress at Feature Freeze will have their Fix Version removed. The release moves on without them. |
| **Features Must Advance Before Feature Freeze** | Features must move past In Progress before the freeze date. If development isn't complete, the feature isn't ready for this release. |
| **PM/UX Signoff Before Feature Freeze** | PM and UX sign-off must be obtained before Feature Freeze. This confirms the delivered work matches what was planned. |

### Code Freeze

Only blocker fixes merge after this point. Every change requires an
exception. The release is in hardening mode.

| Rule | What we expect |
|---|---|
| **Release Pending Transition Before Code Freeze** | Features must move to Release Pending before Code Freeze. This status means all child work is complete and the feature is confirmed for release. |
| **Post-Code-Freeze Exception Process** | All changes after Code Freeze require the blocker exception process: set Release Blocker to Proposed, populate versions, complete risk assessment. 1-business-day turnaround from Release Delivery. |
| **Post-Code-Freeze PR Must Reference Jira** | Every PR merged after freeze must reference a Jira key. In the 3.5 EA2 audit, only 32 of 54 human-authored PRs had Jira keys. This is the gap being closed. |
| **Release Blocker Field Required** | Post-freeze issues need the Release Blocker field set. Without it, the exception process can't evaluate or prioritize them. |
| **Release Notes Frozen** | Release notes must be submitted before Code Freeze. Late notes delay the release. |
| **Test Infrastructure Requires Exception Process** | Test and infrastructure changes also require the exception process post-freeze. "It's just a test fix" doesn't bypass the gate. |
| **Unresolved Blockers at Code Freeze** | All identified blockers must be resolved or reprioritized before Code Freeze. Carrying unresolved blockers into freeze creates churn. |

---

## Where these rules come from

Every rule traces back to one or more source documents. The ruleset is
derived from 25 distinct sources spanning org-wide process documents,
leadership announcements, and cross-team tooling:

**Process & policy documents**

- JIRA Standards for OpenShift AI (org-wide Jira field expectations)
- AAET Agile and Jira Playbook (team conventions, DoR/DoD)
- Standardize Agile Processes (process improvement proposals)
- Feature Refinement process and template (Confluence)
- RHAI Release Milestone Definitions and Expectations (Confluence, canonical)
- Release Process and Operations space (Confluence, 14 child pages)
- RHAI Release Stages and API Tiers practical guide
- Docs Intake Process (doc requirements by release type)
- RHAI Data Strategy 2026 (AI data layer vision, KSO field positioning)

**Leadership & program announcements**

- Target vs Fix Version policy (Tiffany Rozell + Sherard Griffin, effective 3.5 EA1)
- Strengthening Release Integrity and Predictability (scope exception + code freeze processes)
- Post-Code-Freeze Exception Audit (3.5 EA2 PR compliance findings)
- 3.6 Release Planning & Quality Gate 1 requirements
- Resolved Status Retirement (Release Pending replaces Resolved)
- Jira Team Standardization and AI SDLC Process Updates
- Unified Release Milestones + Automated Activity Type
- Quality First: Feature Signoff Process (DP/TP/GA templates)
- 40/40/20 Engineering Work Classification & Allocation Guidance
- Proposed Process Changes Supporting Release Improvements
- AI-Powered Security & FIPS Compliance Tools (strat-creator sign-off integration)

**Cross-team tooling & automation**

- `accorvin/jira-tracker` (Jira hygiene automation, staleness thresholds)
- Agent Ops `team_home/jira_process` (health scoring, cadence scoring, cross-field validations)
- Nathan Weinberg's Jira Agent Config (Llama Stack Core team conventions)
- Docs Planning Companion (Target Version vs Fix Version semantics)

Rules are added when new process expectations are announced or existing
expectations aren't yet encoded. Each rule YAML includes specific source
excerpts so provenance can be verified at the individual rule level.
The full source registry (with document links) lives in the Argus
knowledge base.

---

## Adding or extending rules

Rules are YAML files in `rules/field-hygiene/` or `rules/release-lifecycle/`.
Each specifies:

- `applies_to` - which issue types it checks
- `trigger` (lifecycle rules only) - milestone-based activation window
- `condition` - field checks that must all fail for a violation to fire
- `action` - what to report (message template, notification recipients)
- `enforcement` - alert, comment, or flag
- `sources` - provenance (source IDs with excerpts)

To add a rule: write the YAML, add a test, run `pytest`, and reference
the source document that establishes the expectation.
