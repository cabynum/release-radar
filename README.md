# release-radar

A rule engine that evaluates Jira issues against field-hygiene and
release-lifecycle policies. Outputs structured violations with full
provenance (rule ID, severity, source references).

Built for the RHOAI Data Processing team's Jira workflow on
`redhat.atlassian.net`.

![System Design](design/system-design.png)

## What it does

- Fetches issues from Jira REST API (with changelog for staleness detection)
- Normalizes raw API responses into a flat snapshot format
- Evaluates 49 YAML rules (40 field-hygiene + 9 release-lifecycle)
- Some rules check external sources (GitHub PRs, Jira subtask sign-offs)
- Outputs `violations.json` with per-issue findings

## Quick start

```bash
# Clone and install
git clone https://github.com/cabynum/release-radar.git
cd release-radar
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Set credentials
cp .env.example .env
# Edit .env with your Jira email and API token

# Run against live Jira
python3 -m engine.run --releases 3.5,3.6

# Run against a saved snapshot (no network needed)
python3 -m engine.run --snapshot output/snapshot.json
```

## Rules

Rules are YAML files in `rules/`. Each rule specifies:

- `applies_to` - issue types it checks
- `trigger` (optional) - milestone-based activation window
- `condition` - AND-gated field checks that must all pass for a violation
- `action` - what to report (message template, recipients)
- `sources` - provenance (SOURCE-XX references to process docs)

### Field hygiene (40 rules)

Data correctness checks that run on every evaluation. Missing required
fields, data integrity, staleness, hierarchy violations, cross-system
checks (sign-off completeness, doc links, PR compliance).

### Release lifecycle (9 rules)

Org-policy checks that activate within milestone windows (post-freeze
requirements, exception processes, quality gates).

## Architecture

```
engine/
  conditions.py   - condition operators (AND-gate evaluation)
  normalize.py    - Jira REST API -> flat snapshot
  evaluate.py     - rule loop orchestrator
  violations.py   - violation building + message templates
  milestones.py   - milestone loading + trigger windows
  jira_client.py  - Jira REST auth/fetch
  enrich.py       - external data resolution (GitHub, Jira subtasks)
  run.py          - CLI pipeline
```

## Tests

```bash
pytest
```

134 unit tests covering condition operators, normalization, changelog
parsing, and milestone trigger logic.

## Configuration

### Required

- `JIRA_EMAIL` - Jira account email
- `JIRA_API_TOKEN` - Jira API token

### Optional (for full enrichment)

- `gh` CLI authenticated (for GitHub PR inspection post-code-freeze)

## Milestones

`milestones.yaml` defines release schedules. Release-lifecycle rules
use these dates to determine when their trigger windows are active.
Update this file when new releases are planned.
