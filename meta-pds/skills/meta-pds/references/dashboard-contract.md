# Dashboard Contract

The Meta PDS dashboard is the Human's concise, read-only delivery cockpit. It
projects canonical artifacts and verified evidence without becoming another
place to manage work.

## Installation and source

Copy `assets/dashboard/` to `docs/meta-pds/dashboard/` when an initiative starts
or when the Human requests the dashboard. The folder is directly openable from
`index.html` and has no external runtime dependency.

`dashboard-data.js` contains the projection consumed by `app.js`. Replace the
included demonstration data with initiative data; preserve the schema shape.
Canonical sources remain:

- `initiative.md` for purpose, outcomes, and roadmap;
- `decision-log.yaml` for proposed, testing, locked, and superseded decisions;
- `delivery-state.yaml` for current initiative, slice, blocker, and next-action
  state;
- slice files for stories, acceptance, dependencies, and planning gates;
- execution plans for work packages, owners, waves, dependencies, and tests;
- delivery reports and runtime evidence for QA and release status;
- optional `delivery-events.jsonl` for the recent activity timeline.

Never infer a successful gate, test, release, or Human approval merely to fill
the display. Show unknown or missing evidence explicitly.

## Update rhythm

Refresh the projection at meaningful checkpoints:

- a prototype checkpoint or Human review;
- a decision status change;
- a slice gate, priority, dependency, or revision change;
- a work-package state change or newly reported blocker;
- a QA, release, rollback, or outcome result;
- pause, resume, or recommended-next-action change.

Do not update on every keystroke. A stale dashboard must display its last update
time rather than pretending to be live.

## Required views

Keep the interface list-first, compact, and progressively populated:

1. initiative phase, health, progress, update time, and exact next action;
2. Human attention items and active prototype checkpoint;
3. decisions grouped by status and affected slices;
4. a primary slice list with outcome, revision, priority, dependency, gate,
   progress, story, task, test, and contract summaries;
5. currently active or blocked work packages and assigned agents directly under
   each slice;
6. collapsible user-story rows for quick acceptance and work-package tracing;
7. a large read-only issue-detail dialog with hierarchy breadcrumbs, a spacious
   rendered-Markdown description and acceptance criteria, child tasks below,
   and a compact properties rail; selecting a task reuses the same dialog for
   its description, owner, dependencies, evidence, and breadcrumb return;
8. separate top tabs for slices, decisions, prototype checkpoints, and durable
   activity.

Hide or label unavailable downstream views during early discovery; do not create
fake progress.

## Interaction and browser boundary

Dashboard controls may filter or reveal projected information, but must not
change canonical artifacts, gates, or approvals. The Human opens and navigates
the page manually. Agents may edit the underlying files and use CLI validation,
but must never take control of an interactive browser to test the dashboard.
