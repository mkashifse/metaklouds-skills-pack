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
frozen contract satisfied, and no unexplained scope change.

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

Maintain one active planning slice and one active development slice. Start only
work packages whose dependencies are `DONE` and entry checks pass:

```text
BLOCKED → READY → IN_PROGRESS → VERIFYING → DONE
```

A contract revision marks affected work `REVERIFY_REQUIRED` and recomputes the
ready queue.

## Retry circuit breaker

Stop and escalate when any occurs unless the Human extends the boundary:

- the same evidence-identical failure is observed twice;
- one defect exhausts three remediation cycles;
- a slice accumulates five upstream returns;
- a slice accumulates eight total remediation cycles.

## Visibility summary

At meaningful checkpoints and every resume, report:

```text
Current phase:
Active planning slice:
Active execution slice:
Recently locked decisions:
Work completed:
Current blockers and risks:
Human decision required:
Recommended next action:
Safe alternatives:
```
