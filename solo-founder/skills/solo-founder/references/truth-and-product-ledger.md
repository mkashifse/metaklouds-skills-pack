# Canonical Truth and Product Ledger

## Canonical Truth

Store current product authority in:

```text
docs/solo-founder/canonical-truth.yaml
```

Truth is grouped by the ten finalized Layers. IDs use the Layer prefix, such
as `BUSINESS_DIRECTION-001`. Exactly two statuses exist:

- `PROPOSED`: reviewable but non-authoritative;
- `APPROVED`: explicitly Human-authorized and authoritative.

Required fields are `id`, `status`, `title`, `statement`, `evidence`,
`affected_layers`, and `proposed_at`. Approval adds `approved_at`,
`approved_by: HUMAN`, and `approved_via: CHAT | DASHBOARD`. A proposal may use
`replaces` to identify current approved Truth. Git preserves file history; the
artifact contains only current approved Truth and active proposals.

The PM may record explicit chat approval but cannot approve its own proposal.
The dashboard may perform only a Human-confirmed approval transition.

## Product Ledger

Store operational context in:

```text
docs/solo-founder/product-ledger.yaml
```

It contains:

- current Mode, Layer, affected Layers, initiative, active work, next action;
- authority envelope and Human approval boundaries;
- initiatives and linked Truth/Slices/prototype;
- Work Packages, classification, role, owner identity, focus, activity,
  dependencies, acceptance, execution, delegation reason, typed handoff,
  status, evidence, result, and timestamps;
- issues of kind `DRIFT`, `BLOCKER`, `RISK`, or `EXTERNAL_DEPENDENCY`.

Durable Human product decisions belong in Canonical Truth. A pending one-time
operational authorization uses `human_approval_required: true`; after the
decision, it remains in the Issue's `HUMAN_APPROVED` resolution. There is no
`HUMAN_DECISION` issue kind.

### Issue Sidecar and exit sweep

Issues use exactly three statuses:

- `OPEN`: unresolved but not waiting for a Human;
- `AWAITING_HUMAN`: the affected action is skipped pending one Human decision;
- `RESOLVED`: durable resolution action and evidence are recorded.

Resolution method is separate: `AUTO_WITHIN_AUTHORITY`, `HUMAN_APPROVED`, or
`EXTERNAL_RESOLUTION`. Auto-resolution is allowed only when the change follows
approved Truth, is local and reversible, changes no scope or acceptance,
introduces no security, privacy, legal, financial, health, production, or
irreversibility concern, and passes existing verification. If any condition is
uncertain, leave it `OPEN` or use `AWAITING_HUMAN`.

Issue handling must not become a parallel delivery workflow. During work, keep
a small in-memory queue. At the natural exit from a Work Package or checkpoint,
flush all issue events through one `--issue-events-json` updater call and one
atomic Ledger write. A safe issue may be logged directly as resolved. A Human
issue records one recommendation and impact, pauses only affected scope, and
does not receive more investigation while unrelated work remains available.
An `OPEN` issue also remains passive until it reaches the critical path.

Durable Human decisions become proposed Canonical Truth and link back to the
resolved issue. One-time authorization remains in the issue resolution. The
dashboard defaults to active and Human-attention records; resolved history is
available without creating delivery noise.

Pass the queued events together so the updater validates and writes once:

```text
python3 scripts/update_ledger.py <product-root> --actor PM \
  --issue-events-json '[
    {"action":"LOG","id":"ISSUE-0012","kind":"DRIFT","summary":"Spacing token diverged","disposition":"AUTO_RESOLVED","resolution_action":"Restored the approved token","resolution_evidence":["visual test passed"]},
    {"action":"LOG","id":"ISSUE-0013","kind":"RISK","summary":"Calorie target needs direction","disposition":"AWAITING_HUMAN","recommendation":"Skip calorie targets","impact":"Workout delivery continues"}
  ]'
```

Use `action: RESOLVE` with `resolution_method`, `resolution_action`, and
`resolution_evidence` to close an existing issue. `AWAITING_HUMAN` accepts only
`HUMAN_APPROVED`; an `OPEN` issue accepts `AUTO_WITHIN_AUTHORITY` or
`EXTERNAL_RESOLUTION`. The updater rejects the whole batch on any invalid event.

## Actor boundaries

| Actor | Logical authority |
| --- | --- |
| Human | Direction, Truth approval, consequential risk, redirect/pause/stop |
| PM | Product decisions, proposals, chat approval recording, governed documents, Slices, and Work Package definition |
| Prototype Engineer | Direct rapid prototype execution when explicitly invoked by the Human |
| Full-Stack Engineer | Direct production implementation and verification when explicitly invoked by the Human |
| Dashboard | Read all; approve proposed Truth only after Human confirmation |
| Ledger updater | Physical scoped writes only; no judgment or approval |

Role selection belongs to the Human. The PM does not automatically route,
delegate, supervise, or restore context for either engineer. Engineers read
only the task-local inputs needed for their work and do not change Canonical
Truth or approved acceptance.

The execution roles do not write the Product Ledger by default. When the Human
asks for a durable record, update it once at the natural checkpoint using
actual changed paths and verification evidence. Existing repositories may
retain delegated-work and handoff fields for backward compatibility; they are
not required by the thin direct-invocation workflow.

Use the deterministic updater only when a Ledger write is requested. It locks,
reloads, validates, writes a temporary file, and atomically replaces the
original.
