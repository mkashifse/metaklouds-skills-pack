# Meta PDS Workflow and Gates

## Initiative discovery loop

```text
DISCOVERING
→ PROTOTYPING
→ INITIATIVE_REVIEW
→ INITIATIVE_READY
```

During `DISCOVERING` and `PROTOTYPING`, run short loops:

```text
Human idea
→ candidate decision
→ prototype change
→ manual Human review
→ lock, revise, or supersede
```

Before `INITIATIVE_READY`, confirm problem, target users, goals, measurable
outcomes, scope, non-goals, key journeys, business rules, constraints, risks,
prototype findings, and the proposed capability roadmap. The Human locks the
initiative and roadmap overview.

## Per-slice state machine

```text
DRAFT
→ PLANNING_REVIEW
→ READY_FOR_DEVELOPMENT
→ MOBILIZING
→ EXECUTION_READY
→ IN_PROGRESS
→ READY_FOR_QA
→ VERIFYING
→ RELEASE_READY
→ RELEASED
→ OUTCOME_VALIDATED
```

Exception states:

```text
NEEDS_UPSTREAM_CLARIFICATION
HUMAN_DECISION_REQUIRED
REWORK_REQUIRED
REVERIFY_REQUIRED
PAUSED
BLOCKED
REPLAN_REQUIRED
SUPERSEDED
```

## Gate ownership

### `INITIATIVE_READY`

- Product Manager synthesizes the initiative and roadmap.
- Human approves goals, boundaries, outcomes, and consequential decisions.

### `READY_FOR_DEVELOPMENT`

Requires all three:

1. structural and traceability validation;
2. Planning Lead content sign-off;
3. Development Intake feasibility review against the actual repositories.

No development-blocking decision may remain open. A failed check creates a
focused deficiency with source, impact, owner, recommendation, and blocked
work; it returns upstream for a revision.

### `EXECUTION_READY`

Requires a valid execution plan with:

- frozen contract version;
- bounded work packages and owners;
- dependency DAG with no unknown nodes or cycles;
- critical path and parallel waves;
- repository/path ownership;
- entry and exit checks;
- story, requirement, and test traceability;
- integration, merge, deploy, flag, observability, and rollback sequence.

`READY_FOR_DEVELOPMENT` allows mobilization. Production coding begins only at
`EXECUTION_READY`.

### `READY_FOR_QA`

Requires every work package completed or explicitly dispositioned, local
commits and changed paths recorded, required development tests passing, the
frozen contract satisfied, no unexplained scope change, and no unresolved drift
that affects the slice's acceptance, contract, or release evidence.

### `RELEASE_READY`

Requires independent QA evidence for the whole slice: complete lifecycle,
traceability, contracts, migrations, security, permissions, accessibility,
Playwright CLI results when applicable, observability, deployment order, and
rollback. A partial component cannot pass.

### `OUTCOME_VALIDATED`

After release observation, compare adoption, completion, errors, latency,
support incidents, user feedback, and operational findings with initiative
success measures. Mark `REPLAN_REQUIRED` when the outcome is not supported.

## Scheduling

Every actionable Human instruction first becomes a PM-Assistant-owned
coordination task. The Product Manager issues direction only; the PM Assistant
records, researches, writes, assigns, validates, and briefs. Questions and
casual brainstorming do not enter the task ledger. Coordination tasks use the
same flow across discovery, prototype, planning, development, QA, release, and
operations:

```text
BACKLOG → READY → IN_PROGRESS → VERIFYING → DONE
```

Development implementation remains decomposed into canonical execution-plan
work packages. Link those package IDs from the parent coordination task rather
than duplicating their state.

Maintain one active planning slice and one active development slice. A newly
assigned package remains `BACKLOG` while prerequisites are incomplete, becomes
`READY` when every dependency is `DONE` and entry checks pass, and becomes
`IN_PROGRESS` only when its assigned worker actually starts:

```text
BACKLOG → READY → IN_PROGRESS → VERIFYING → DONE
```

Use `BLOCKED`, `BLOCKED_BY_DRIFT`, `PAUSED`, `REWORK_REQUIRED`, and
`REVERIFY_REQUIRED` as exception states rather than disguising them as ordinary
backlog work.

A contract revision marks affected work `REVERIFY_REQUIRED` and recomputes the
ready queue.

Detected drift pauses only its affected dependency closure. Use
`BLOCKED_BY_DRIFT` with the Drift ID for packages waiting on Human approval and
continue independent `READY` work. Apply the confidence and escalation policy
in `drift-control.md`; do not hold the whole development slice unless every safe
path depends on the unresolved drift.

## Retry circuit breaker

Stop and escalate when any occurs unless the Human extends the boundary:

- the same evidence-identical failure is observed twice;
- one defect exhausts three remediation cycles;
- a slice accumulates five upstream returns;
- a slice accumulates eight total remediation cycles.

## Visibility summary

At meaningful checkpoints and every resume, the PM Assistant prepares this
delta-only brief for the Product Manager, who communicates the relevant parts:

```text
Current phase and interaction mode:
Active planning slice:
Active execution slice:
Recently locked decisions:
Active Scrum Board tasks and assignees:
Work completed:
Current blockers and risks:
Open drift and resolution status:
Human decision required:
Current branch and verified PR state:
Recommended next action:
Safe alternatives:
Dashboard:
```
