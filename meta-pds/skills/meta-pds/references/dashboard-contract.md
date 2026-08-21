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
- slice files for stories, acceptance, dependencies, and planning gates;
- execution plans for work packages, owners, waves, dependencies, and tests;
- delivery reports and runtime evidence for QA and release status;
- optional `delivery-events.jsonl` for the recent activity timeline.

For UI preview before a product has canonical artifacts, use `--demo`. Demo mode
parses the bundled Authentication slice example into a temporary in-memory
runtime, writes nothing into a product repository, and must be visibly labelled
as example data. Never treat it as delivery state.

Never infer a successful gate, test, release, or Human approval merely to fill
the display. Show unknown or missing evidence explicitly. Parse or validation
errors must be visible; never fall back to stale or invented data.

## Parseable conventions

- Markdown artifacts use YAML frontmatter for identity, revision, priority,
  order, state, and dependencies.
- Slice stories use `### US-<id> — <title>` headings, followed by `**Story:**`
  and `**Acceptance criteria:**` with ordinary bullet items.
- Initiative roadmap rows use the columns in `initiative-template.md`.
- Execution plans contain structured `integration_contracts`, `test_cases`, and
  `work_packages`; package `supports`, `depends_on`, and `required_tests` values
  join records by stable IDs.
- Delivery state owns current slice status, active work, Human attention, and
  next action. Counts, active agents, blockers, test totals, and progress are
  derived in memory and never copied back into artifacts.

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
