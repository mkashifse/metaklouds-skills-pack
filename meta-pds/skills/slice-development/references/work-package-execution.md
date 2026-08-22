# Work-Package Execution Contract

## Package boundary

A work package is a bounded technical assignment sized for one fresh agent
session. It may implement part of one story or shared infrastructure used by
several stories. It never becomes a separate product or release boundary.

Every package declares:

- ID, owner, status, and contract version;
- priority, assigning Product Manager, and assignment time;
- an immutable Development Lead brief containing the original instruction,
  expected outcome, scope, exclusions, and acceptance criteria;
- supported slice requirements or user stories;
- dependencies, inputs, and produced outputs;
- owned and forbidden paths within the single product repository;
- entry checks and exit checks;
- required canonical Test IDs, CLI checks, and evidence;
- repository-evidenced applicable support skills;
- integration owner and dependants.

Append dated clarifications to the Lead brief; never replace the original
instruction after assignment. Do not use changed line count as the sole size measure. Split a package when it
crosses unrelated modules, needs materially different context, or cannot be
completed and verified in one focused session.

## Context capsule

Give a worker only:

- slice ID/revision and relevant requirement/story excerpts;
- package definition and dependency outputs;
- current contract subset and version;
- assigned paths plus repository instructions;
- applicable implementation skills;
- required Test IDs from the slice and result schema.

Do not pass the full conversation or unrelated slice history. Before context
pressure causes compaction or degraded reasoning, checkpoint the package with a
local commit, tests, status, remaining work, and exact resume instruction. A
fresh worker resumes from artifacts and evidence.

Before launch, read the Meta PDS implementation-skill routing reference. Record
the selected names in the package's `applicable_skills` field, verify that each
is installed, and require the worker to read those skills. Do not select a
framework skill without repository evidence or broaden the package to justify
an installed skill.

## Scheduling

A newly assigned package is `BACKLOG` until every dependency is `DONE`, required
inputs exist at the cited revisions, and entry checks pass. It then becomes
`READY`; it becomes `IN_PROGRESS` only when the worker starts. The Development
Lead owns the ready queue.

Prefer dependency-aware waves rather than rigid layer order:

```text
contract and risk decisions
→ enabling foundations and test harnesses
→ parallel feature implementation
→ integration and recovery/security flows
→ whole-slice verification
```

## Worker result

```yaml
package_id: WP-0001
status: DONE | REWORK_REQUIRED | BLOCKED
contract_version: ""
changed_paths: []
local_commits: []
tests:
  - command: ""
    result: passed | failed
    evidence: ""
produces: []
risks: []
remaining_work: []
```

The Development Lead independently inspects the result before unblocking
dependants.

## Code-area isolation

Frontend packages own paths under `frontend/`; backend and database packages
own paths under `backend/`. A cross-area slice uses separate bounded packages
joined by a versioned integration contract and an integration package or check.
Workers must not solve integration by importing application source code from
the other area. Any exception returns to the Product Manager as an architecture
decision instead of being introduced silently.
