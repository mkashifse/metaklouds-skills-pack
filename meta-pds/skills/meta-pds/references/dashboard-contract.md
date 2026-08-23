# Dashboard Contract

The Meta PDS dashboard is the Human's concise, read-only delivery cockpit. It
projects canonical artifacts and verified evidence without becoming another
place to manage work.

## Runtime and source

Do not create a dashboard folder, projection file, database, or duplicated
dashboard data inside a product repository. The installed skill owns the
reusable UI, parser, and runtime coordinator. On every Meta PDS invocation,
ensure the project dashboard with:

```text
python3 <installed-meta-pds>/scripts/serve_dashboard.py <product-root> --ensure
```

The command starts one detached local service for the resolved project or
reuses the existing healthy service for that exact project. It prints the URL
and exits; always return that clickable URL to the Human. Runtime coordination
is stored outside the product repository in the operating system's temporary
directory. A lock serializes discovery and launch, stale registry entries are
discarded, and a project identity endpoint prevents one project's dashboard
from being mistaken for another. If `127.0.0.1:8765` belongs to another
service, select an available local port. Never start a second server manually.

The local service reparses canonical files for every dashboard request and
keeps the assembled view only in memory. The Human refreshes the page to see
the current files. Canonical sources are:

- `initiative.md` for purpose, outcomes, and roadmap;
- `decision-log.yaml` for proposed, testing, locked, and superseded decisions;
- optional `drift-log.yaml` for detected, auto-resolved, approval-pending,
  re-verification, and closed drift with confidence and dependency impact;
- optional `task-log.yaml` for every cross-phase actionable instruction,
  Product Manager route, PM Assistant administration, specialist assignment,
  dependencies, result, and evidence;
- `delivery-state.yaml` for current initiative, slice, blocker, and next-action
  state;
- slice files for stories, acceptance, test definitions, dependencies, and
  planning gates;
- execution plans for Scrum Board development tasks: work packages, immutable Lead briefs,
  owners, assignment metadata, waves, dependencies, and required Test ID
  references;
- delivery reports and runtime evidence for QA and release status;
- optional `delivery-events.jsonl` for append-only task and delivery history.

Repository visibility is derived separately from read-only runtime evidence on
each refresh:

- local branch, current branch, upstream, commit, ahead/behind, and working-tree
  state come from the product root's Git repository;
- pull-request state, draft state, review decision, merge state, branches, and
  URL come from authenticated GitHub CLI output when available.

Never infer a PR from a branch name or infer merge readiness from local commits.
When GitHub CLI, authentication, a supported remote, or network access is
unavailable, keep local branch evidence visible and label PR evidence
unavailable with the concise runtime diagnostic. Never expose credentials or
authentication output.

The delivery-event file is append-only JSON Lines. Each event contains an ISO 8601
`at`, concise `kind`, `title`, and evidence-bearing `detail`; the dashboard
joins events that cite a task or work-package ID into that task's status history.
Record durable delivery checkpoints only, not low-value agent or editor
activity. Do not restore a separate generic Activity view.

Before a product has canonical artifacts, the dashboard remains attached to
that real project. It shows live repository and pull-request evidence, empty
delivery collections, and explicit diagnostics for each missing canonical
artifact. Never substitute bundled examples, templates, fixtures, conversation
memory, or another project's files. When canonical artifacts are created, the
same runtime projects them on the next refresh.

An explicit `?demo=1` view may project the bundled regression fixture for
visual inspection. It must use the existing project runtime, display a
persistent demo indicator in the header with a concise tooltip and a
return-to-live link, preserve live repository evidence, and never copy or write
fixture data into the product repository.
The ordinary URL and `/api/dashboard` endpoint remain live-only; demo data is
served only when the Human opens the explicitly labelled demo URL.

Never infer a successful gate, test, release, or Human approval merely to fill
the display. Show unknown or missing evidence explicitly. The dashboard runs
the same repository-wide contract as the CLI, returns structured diagnostics,
and shows a persistent data-health banner when errors exist. A malformed
downstream slice, execution plan, report, or event is quarantined while valid
unrelated delivery data remains visible. A malformed core initiative or
delivery artifact may block the projection because identity and state can no
longer be established. Never fall back to stale or invented data.

## Parseable conventions

- Markdown artifacts use YAML frontmatter for identity, revision, priority,
  order, state, and dependencies.
- Slice stories use `### US-<id> — <title>` headings, followed by `**Story:**`
  and `**Acceptance criteria:**` with ordinary bullet items.
- Slice tests use `### TC-<id> — <title>` headings and the labelled fields in
  `slice-template.md`. The slice is the sole source of test definitions.
- Initiative roadmap rows use the columns in `initiative-template.md`.
- Task logs contain PM-Assistant-owned cross-phase coordination tasks. Every
  task preserves the original instruction and links rather than copies derived
  execution work packages.
- Execution plans contain structured `integration_contracts` and
  `work_packages`; package `supports`, `depends_on`, and `required_tests` values
  join stories, packages, and slice test definitions by stable IDs.
- Delivery state owns current slice status, active work, Human attention, and
  next action. Counts, active agents, blockers, test totals, and progress are
  derived in memory and never copied back into artifacts. Progress is a derived
  display estimate, not canonical delivery evidence.
- Duplicate YAML keys and duplicate slice, story, test, contract, work-package,
  execution, report, decision-record, or state IDs are errors rather than
  last-write wins. A Truth key may repeat only as a valid append-only revision
  sequence.

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

The application header is one compact horizontal row: the package icon and
`Meta PDS` name followed immediately by the top view tabs. Do not add a product
tagline, initiative title or ID, phase, health, source label, or update time to
the header. At narrower widths, keep the brand stable and let the tabs scroll
horizontally rather than creating a second header row.

Keep the primary toolbar for every populated view sticky immediately beneath
the application header so filters and summary context never leave the viewport
during vertical scrolling. Give sticky toolbars an opaque surface and a lower
stacking layer than the application header so list content passes underneath
without showing through. Preserve horizontal access to dense controls at narrow
widths rather than clipping or wrapping the application header.

Give every Truth, Drift, slice, user-story, and work-package row a quiet copy
control that does not trigger its accordion or detail navigation. Copy a
Codex-ready Markdown packet containing the entity's stable identity, current
status, canonical description or instruction, dependencies, traceability, and
evidence available in the projection, plus a requested-change placeholder.
Prefix the packet with the applicable update guardrail: append-only revision
for locked Truth, durable evidence for Drift, stable traceability for slices and
stories, and immutable Lead brief for work packages. Clipboard actions are
read-only and must show concise success or failure feedback without writing a
canonical artifact.

1. visible canonical data-health diagnostics, with projection source details
   kept in the footer rather than the header;
2. a leftmost `Truth` tab containing one chronological decision stream ordered
   newest first by the latest recorded revision activity for each canonical
   key; undated Truth remains visible after dated Truth and is explicitly
   labelled `Time not recorded`; do not wrap the stream in collapsible group
   sections. Label every Truth item with its layer and keep layer available as
   a group filter alongside status, primary type, and phase; lead each Truth
   item with the brain icon and one clear statement; use the same compact
   three-row document rhythm as Drifts: identity, layer, type, status, and
   recorded-time metadata first, title second, and phased
   dependency/affected-artifact properties third; render each Truth as an
   independently collapsible row that starts collapsed; keep phase, dependency
   keys, and affected artifacts in the persistent Truth title bar beside the
   unique canonical key, record ID, revision, primary and secondary labels, and
   one non-duplicated status label; show explicit contradiction links in the
   expanded body; default the status filter to `Canonical`; keep the current
   locked revision as the displayed Truth while an optional proposed or testing
   revision awaits Human approval, and use that newer candidate's recorded time
   when positioning the canonical key in the stream; show the candidate and
   collapsed append-only revision history inside the expanded Truth item; keep
   interaction mode, canonical count, review count, and contradiction count
   visible in the same compact, single-row toolbar as the status, group, type,
   and phase filters without turning the dashboard into an approval surface;
3. a primary slice list with a single view toolbar that keeps the slice totals
   beside the status filters rather than in the application header, followed
   by separate compact document-style collapsible cards that place icon, ID,
   status, progress, and counts in one metadata row, the
   slice title beneath it, and outcome plus properties behind hairline rules;
   cards contain outcome,
   revision, priority, dependency, gate, progress, story, task, test, and
   contract summaries; keep one persistent header summary for status, progress,
   story, task, test, and blocker counts so those metrics do not move when the
   card expands or collapses; keep status dot, slice ID, and title together as
   a persistent, vertically centered first-row identity aligned with the slice
   icon, analytics, and collapse control, with unchanged typography; a
   collapsed card becomes one row showing the summary beside that identity;
   align the expanded description area to the same content edge as the
   work-package panel, with outcome copy on the left and a compact priority,
   revision, and dependency property column on the right; use the same Layers entity
   icon for a slice in its card and detail header; show progress everywhere as
   ten small vertical segments with exact partial fill plus the numeric percent;
   clicking the card header toggles the card while clicking its title opens
   full slice detail;
4. currently active or blocked work packages and assigned agents directly under
   each slice, rendered seamlessly on the card surface without a nested panel
   fill, enclosing border, or rounded container;
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
9. a separate `Drifts Detected` tab showing every durable drift, status,
   severity, ambiguity and confidence, recommendation, resolution, evidence,
   Human approval state, affected Truth/slices/work packages, and the explicit
   split between paused and continuing work; render each drift as a quiet,
   document-style accordion in one seamless list surface with hairline row
   separators only—never separate cards or gaps; retain a subtle left-edge
   emphasis for Human-approval rows; use one compact
   ID/severity/status/confidence row, a clear title and recommendation using the
   dashboard's shared type scale, then aligned affected-work properties
   and evidence separated by hairline rules; provide compact status and severity
   filters, and never make the dashboard itself an approval surface;
10. separate top tabs ordered Truth, Slices, Drifts Detected, Branches, and
   Scrum Board, plus the prototype utility; keep compact totals integrated into
   the relevant tabs. Scrum Board is a compact, filterable vertical Task List
   projected from canonical cross-phase tasks plus development work packages,
   not a writable Kanban database. Keep phase visible and filterable so
   discovery, prototype, planning, development, QA, release, and operations
   assignments share one delivery record.
   Every collapsible row keeps `Task ID : Task title` left-aligned and
   `Assignee | Status` right-aligned; its expanded body renders the package as
   Markdown, leading with the locked original Lead instruction and then the
   expected outcome, scope, exclusions, acceptance criteria, dependencies,
   Truth/story/test traceability, development evidence, and task-specific
   status history. Map the normal flow to Backlog, Ready, In Progress, Review,
   and Done filters while preserving explicit blocked and drift states in the
   row itself.
11. a separate Branches tab showing the current and default branches, dirty-path
    count, every local branch's head, upstream and ahead/behind state, associated
    PR when verified, plus a pull-request list with live state, draft/review/merge
    evidence, head/base branches, update time, and clickable GitHub URL. Keep
    Git/PR diagnostics inside this tab rather than treating unavailable remote
    evidence as a canonical artifact error.

Hide or label unavailable downstream views during early discovery; do not create
fake progress.

## Interaction and browser boundary

Dashboard controls may filter, reveal, or copy projected information, but must
not change canonical artifacts, gates, or approvals. The Human opens and
navigates the page manually. Agents may edit the underlying files and use CLI
validation, but must never take control of an interactive browser to test the
dashboard.
