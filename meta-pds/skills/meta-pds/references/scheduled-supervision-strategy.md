# Scheduled Supervision Strategy

Status: **PROPOSED**. This records the intended design. Do not claim scheduled
supervision, locking, leases, or automatic shutdown are implemented until the
artifact schema, validator, dashboard, and skill behavior support them together.

## Purpose

Use Codex scheduled tasks to wake Meta PDS during an explicitly authorized
autonomous delivery window. Scheduling is a wake-up mechanism, not project
memory, truth, or delivery authority.

The layers remain separate:

```text
Codex scheduled task        wakes the supervisor
Meta PDS skill              supplies operating policy and routing
canonical project artifacts supply durable state and evidence
Human authority envelope    bounds every action
```

Conversation context may help a run, but every scheduled cycle must be able to
reconstruct the initiative from repository evidence after compaction or in a
fresh context.

## Recommended scheduled tasks

### Active supervisor heartbeat

Use a task attached to the active chat for a Human-approved autonomous run.
Default to a 15-minute cadence and a finite lease, such as four hours. The
Human may choose another cadence or duration.

Each heartbeat performs one bounded supervisor cycle:

1. Invoke `meta-pds` explicitly and resolve the canonical product root.
2. Load the authority envelope, Truth, delivery state, slices, execution plans,
   Scrum tasks, drift, Git branches, pull requests, tests, and worker evidence.
3. Acquire the single-supervisor lease. Exit without work when another healthy
   cycle owns it.
4. Reconcile completed or failed work and run structural validation.
5. Select the highest-priority ready action inside the authority envelope and
   existing work-in-progress limits.
6. Dispatch or continue only bounded work. Never start duplicate dashboard
   servers, workers, branches, or tasks for the same project responsibility.
7. Record the checkpoint, next action, heartbeat time, and relevant delivery
   event; refresh the dashboard projection; then release the cycle lock.

The heartbeat must not blindly request "keep coding." Its prompt must identify
the product root, invoke Meta PDS, require rehydration, preserve scope and Human
approval boundaries, and define terminal conditions.

Suggested durable prompt:

```text
Invoke $meta-pds for <absolute-product-root>. If no approved autonomous run is
ACTIVE, exit. Rehydrate from canonical artifacts and repository evidence. If a
healthy supervisor cycle already owns the project lease, exit. Reconcile work,
tests, drift, branches, and pull requests; then continue one highest-priority
safe supervisor cycle within the recorded authority envelope and WIP limits.
Never widen scope, bypass Human approval, or duplicate project processes.
Checkpoint canonical state and dashboard-visible evidence before finishing.
Stop or pause scheduling when the run completes, its lease expires, no
independent work remains, a circuit breaker trips, or the Human stops it.
```

### Daily resume brief

Use a separate project-scoped scheduled task at the Human's chosen local time.
It should be read-only by default and report:

- current phase and mode;
- recently locked or revised Truth;
- active, completed, paused, and next slices;
- Scrum Board movement and current owners;
- unresolved and auto-resolved drift;
- branch and pull-request state;
- Human approvals required;
- one recommended next action.

The resume brief does not start development unless the Human separately granted
that authority.

## Durable supervisory state

A future schema revision should add one canonical supervision block to
`delivery-state.yaml`, including:

- immutable run ID and explicit objective;
- measurable completion condition;
- `ACTIVE`, `WAITING_FOR_HUMAN`, `COMPLETE`, `STOPPED`, or `EXPIRED` status;
- authority-envelope reference and stop conditions;
- start time, last heartbeat, and lease expiry;
- supervisor owner and short lock expiry;
- current slice and task, completed work, remaining work, and next safe action;
- scheduled-task identifier and cadence;
- Human approvals and dependency-scoped paused work.

The validator must reject duplicate active runs, expired locks presented as
healthy, unknown task or slice references, and terminal runs that still claim
active work. The dashboard should show run status, lease time, last heartbeat,
next action, and why work is waiting or stopped.

An optional durable Codex goal may mirror the terminal objective only when the
Human explicitly asks to create one. It does not replace Meta PDS artifacts.

## Human approval and non-blocking work

When drift needs Human approval, pause only affected tasks and continue the
independent ready queue. Record the recommendation, ambiguity, confidence,
affected Truth and slices, and paused versus continuing work.

If no independent work remains, mark the run `WAITING_FOR_HUMAN`, report one
focused decision packet, and avoid repeated notifications until evidence
changes or a reasonable reminder interval passes.

## Terminal and safety behavior

Pause or disable the active heartbeat when any occurs:

- the completion condition is satisfied;
- the finite run lease expires;
- the Human pauses or stops the run;
- all remaining work requires Human approval;
- repository access or required infrastructure remains unavailable;
- the retry circuit breaker is reached;
- validation shows unsafe or contradictory canonical state.

Scheduled work runs unattended, so it must use the narrowest useful local
permissions. The canonical supervisor should operate on one product state;
implementation workers may use isolated branches or worktrees. Do not create a
fresh worktree for every heartbeat when that would fragment the shared ledger.

## Adoption sequence

1. Extend the delivery-state template and artifact contract.
2. Add parser and repository-wide validator coverage.
3. Project supervision state and scheduler health in the dashboard.
4. Add automation creation, update, and shutdown behavior to Meta PDS.
5. Test manual ticks, overlapping ticks, compaction/fresh-context recovery,
   approval waits, lease expiry, circuit breakers, and completed-run shutdown.
6. Enable scheduled supervision only after those checks pass.
