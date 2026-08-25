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
  dependencies, acceptance, status, evidence, result, and timestamps;
- issues of kind `DRIFT`, `BLOCKER`, `RISK`, or `EXTERNAL_DEPENDENCY`.

Durable Human product decisions belong in Canonical Truth. A one-time
operational authorization remains an issue with
`human_approval_required: true`; there is no `HUMAN_DECISION` issue kind.

## Actor boundaries

| Actor | Logical authority |
| --- | --- |
| Human | Direction, Truth approval, consequential risk, redirect/pause/stop |
| PM | Full Product Ledger management, proposals, chat approval recording, classification, assignment, verification, `DONE`/`REWORK` |
| Prototype Engineer | Assigned prototype execution status, result/evidence, blocker, and linked discovered issues |
| Full-Stack Engineer | Assigned production execution status, result/evidence, blocker, and linked discovered issues |
| Dashboard | Read all; approve proposed Truth only after Human confirmation |
| Ledger updater | Physical scoped writes only; no judgment or approval |

The only specialist roles are `PROTOTYPE_ENGINEER` and
`FULL_STACK_ENGINEER`. `owner` is the assigned worker identity, allowing
multiple Full-Stack Engineers without inventing more roles. `workstream` is the
temporary focus: `PROTOTYPE`, `FRONTEND`, `BACKEND`, or `FULL_STACK`.

Engineers cannot delegate further or change Mode, Layer, scope, role, owner,
focus, acceptance, dependencies, initiative state, next action, authority,
approved Truth, other work, or mark work `DONE`.

Classification and execution are independent. A small code change is recorded
like this:

```yaml
classification: TRIVIAL
execution: DELEGATED
role: FULL_STACK_ENGINEER
owner: full-stack-1
workstream: FULL_STACK
activity: IMPLEMENTATION
owned_paths:
  - apps/frontend
  - apps/backend
  - packages/contracts
```

Parallel Full-Stack Engineers use separate Work Packages and distinct `owner`
identities. Their `workstream` values may be `FRONTEND` and `BACKEND`, but both
retain `role: FULL_STACK_ENGINEER`.

Use the deterministic updater for Ledger changes. It locks, reloads, checks
actor permissions and transitions, validates, writes a temporary file, and
atomically replaces the original.
