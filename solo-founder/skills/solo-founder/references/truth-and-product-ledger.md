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

Durable Human product decisions belong in Canonical Truth. A one-time
operational authorization remains an issue with
`human_approval_required: true`; there is no `HUMAN_DECISION` issue kind.

## Actor boundaries

| Actor | Logical authority |
| --- | --- |
| Human | Direction, Truth approval, consequential risk, redirect/pause/stop |
| PM | Full Product Ledger management, proposals, chat approval recording, classification, assignment, verification, `DONE`/`REWORK` |
| Prototype Engineer | Optional assigned parallel prototype execution, typed handoff, result/evidence, blocker, and linked discovered issues |
| Full-Stack Engineer | Optional assigned parallel execution, typed handoff, result/evidence, blocker, and linked discovered issues |
| Dashboard | Read all; approve proposed Truth only after Human confirmation |
| Ledger updater | Physical scoped writes only; no judgment or approval |

The PM is the default executor for every activity, including code. The only
optional executor roles are `PROTOTYPE_ENGINEER` and `FULL_STACK_ENGINEER`.
`owner` is the assigned worker identity, allowing multiple parallel executors
without inventing more roles. `workstream` is the temporary focus:
`PRODUCT`, `PROTOTYPE`, `FRONTEND`, `BACKEND`, or `FULL_STACK`.

Engineers cannot delegate further or change Mode, Layer, scope, role, owner,
focus, acceptance, dependencies, initiative state, next action, authority,
approved Truth, other work, or mark work `DONE`.

Classification and execution are independent. A small code change is recorded
like this:

```yaml
classification: TRIVIAL
execution: DIRECT
role: PM
owner: PM
workstream: FULL_STACK
activity: IMPLEMENTATION
delegation_reason: null
handoff_type: null
handoff_path: null
handoff_submitted_at: null
handoff_submitted_hash: null
handoff_consumed_at: null
owned_paths:
  - apps/frontend
  - apps/backend
  - packages/contracts
```

When parallel delegation is expected to be faster, record it explicitly:

```yaml
classification: NON_TRIVIAL
execution: DELEGATED
role: FULL_STACK_ENGINEER
owner: full-stack-1
workstream: BACKEND
activity: IMPLEMENTATION
delegation_reason: PARALLELISM
handoff_type: IMPLEMENTATION
handoff_path: docs/solo-founder/handoffs/implementation/WORK-0042.md
handoff_submitted_at: null
handoff_submitted_hash: null
handoff_consumed_at: null
```

Parallel engineers use separate Work Packages and distinct `owner` identities.
Delegated work enters `VERIFYING` only after its typed handoff is complete. The
PM consumes that handoff before recording `DONE` or `REWORK`. Read
[handoff-contract.md](handoff-contract.md) for the payload and consumption
rules.

Use the deterministic updater for Ledger changes. It locks, reloads, checks
actor permissions and transitions, validates, writes a temporary file, and
atomically replaces the original.
