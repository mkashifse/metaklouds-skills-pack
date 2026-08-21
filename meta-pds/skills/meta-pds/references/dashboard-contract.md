# Dashboard Contract

The Meta PDS dashboard is the Human's concise, read-only delivery cockpit. It
projects canonical artifacts and verified evidence without becoming another
place to manage work.

## Runtime and source

Do not create a dashboard folder, projection file, database, or duplicated
dashboard data inside a product repository. The installed skill owns the reusable
UI and parser. Launch it from the product root with:

```text
python3 <installed-meta-pds>/scripts/serve_dashboard.py <product-root>
```

The local service binds to `127.0.0.1:8765` by default, reparses canonical files
for every dashboard request, and keeps the assembled view only in memory. The
Human refreshes the page to see the current files. Canonical sources are:

- `initiative.md` for purpose, outcomes, and roadmap;
- `decision-log.yaml` for proposed, testing, locked, and superseded decisions;
- `delivery-state.yaml` for current initiative, slice, blocker, and next-action
  state;
- slice files for stories, acceptance, test definitions, dependencies, and
  planning gates;
- execution plans for work packages, owners, waves, dependencies, and required
  Test ID references;
- delivery reports and runtime evidence for QA and release status;
- optional `delivery-events.jsonl` for the recent activity timeline.

For UI preview before a product has canonical artifacts, use `--demo`. Demo mode
parses the bundled Authentication slice and execution-plan examples into a
temporary in-memory runtime, writes nothing into a product repository, and must
be visibly labelled as example data. Never treat it as delivery state.

Never infer a successful gate, test, release, or Human approval merely to fill
the display. Show unknown or missing evidence explicitly. Parse or validation
errors must be visible; never fall back to stale or invented data.

## Parseable conventions

- Markdown artifacts use YAML frontmatter for identity, revision, priority,
  order, state, and dependencies.
- Slice stories use `### US-<id> — <title>` headings, followed by `**Story:**`
  and `**Acceptance criteria:**` with ordinary bullet items.
- Slice tests use `### TC-<id> — <title>` headings and the labelled fields in
  `slice-template.md`. The slice is the sole source of test definitions.
- Initiative roadmap rows use the columns in `initiative-template.md`.
- Execution plans contain structured `integration_contracts` and
  `work_packages`; package `supports`, `depends_on`, and `required_tests` values
  join stories, packages, and slice test definitions by stable IDs.
- Delivery state owns current slice status, active work, Human attention, and
  next action. Counts, active agents, blockers, test totals, and progress are
  derived in memory and never copied back into artifacts.

## Status semantics

Normalize every displayed status through one shared renderer across the main
dashboard and all detail dialogs. Use the same semantic colors everywhere:

- complete, released, locked, passed, and validated: green;
- active, executing, and in progress: orange;
- verifying, testing, and Human review: blue;
- ready states: amber;
- blocked, failed, at risk, and rework states: red;
- draft, planned, proposed, paused, and unknown states: neutral.

Render every status as color-coded text without a pill, border, or background,
including main lists, properties, accordions, and detail dialogs. Avoid
duplicating status in a detail header when its properties already show it. The
label and semantic color must not change between contexts.

## Update rhythm

Update canonical artifacts at meaningful checkpoints:

- a prototype checkpoint or Human review;
- a decision status change;
- a slice gate, priority, dependency, or revision change;
- a work-package state change or newly reported blocker;
- a QA, release, rollback, or outcome result;
- pause, resume, or recommended-next-action change.

Do not write a separate projection at any checkpoint. The displayed generation
time states when the files were last parsed, not when delivery evidence changed.

## Required views

Keep the interface list-first, compact, and progressively populated:

1. initiative phase, health, update time, and source kind;
2. decisions grouped by status and affected slices;
3. a primary slice list with separate collapsible cards containing outcome,
   revision, priority, dependency, gate, progress, story, task, test, and
   contract summaries; a collapsed card becomes one row showing only identity,
   status, progress, task completion, and blockers; use the same Layers entity
   icon for a slice in its card and detail header; show progress everywhere as
   ten small vertical segments with exact partial fill plus the numeric percent;
   clicking the card header toggles the card while clicking its title opens
   full slice detail;
4. currently active or blocked work packages and assigned agents directly under
   each slice;
5. collapsible user-story rows in slice detail for acceptance and work-package
   tracing;
6. collapsible slice test-case rows showing level, method, owner, linked stories,
   expected result, and available QA evidence;
7. a large read-only issue-detail dialog with hierarchy breadcrumbs, a compact
   properties rail, and separate Overview, User Stories, Work Packages, and
   Test Cases tabs; work packages use status-bearing collapsible rows with a
   linear rendered-Markdown body; selecting a work-package title reuses the
   dialog for full description, owner, dependencies, evidence, and breadcrumb
   return while the rest of its row toggles the inline body;
8. dependencies and clickable contracts in the slice properties rail; selecting
   a contract reuses the detail dialog and renders its canonical Markdown or
   slice-recorded required behavior;
9. separate top tabs for slices, decisions, prototype checkpoints, and durable
   activity, with compact slice totals integrated into the tabs.

Hide or label unavailable downstream views during early discovery; do not create
fake progress.

## Interaction and browser boundary

Dashboard controls may filter or reveal projected information, but must not
change canonical artifacts, gates, or approvals. The Human opens and navigates
the page manually. Agents may edit the underlying files and use CLI validation,
but must never take control of an interactive browser to test the dashboard.
