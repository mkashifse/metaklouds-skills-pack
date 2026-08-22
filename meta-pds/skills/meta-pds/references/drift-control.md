# Drift Control

Drift is any observed mismatch between current work or evidence and canonical
Truth, an approved slice, its frozen execution contract, or verified runtime
behavior. Detect it early without turning every file change into a ceremony.

## Responsibility

- Every functional lead and worker checks the boundary it owns and reports
  evidence-backed drift immediately.
- The Development Lead triages implementation and integration drift, computes
  dependency impact, and keeps independent ready work moving.
- Independent QA detects whole-slice, release, and runtime drift without
  repairing the implementation it verifies.
- The Product Manager owns `drift-log.yaml`, routes Human decisions, updates
  canonical state, and closes or reopens drift from evidence.
- The Human approves consequential or uncertain resolution. The Human is not
  asked to diagnose raw evidence; always provide a recommendation and impact.

## Checkpoints

Check incrementally at planning review, development intake, work-package entry
and exit, contract integration, QA handoff, release readiness, and resume.
Also check when a test, migration, generated contract, or runtime observation
contradicts a locked source. Use focused checks during work and the complete
cross-artifact validator at gates so drift control does not serialize ordinary
development.

## Classification and confidence

Record severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), ambiguity (`LOW`,
`MEDIUM`, `HIGH`), detection confidence, and resolution confidence from 0–100.
Classify type as `SCOPE`, `ACCEPTANCE`, `UI_UX`, `SCHEMA`, `API_CONTRACT`,
`ARCHITECTURE`, `SECURITY_PRIVACY`, `DEPENDENCY`, `TESTING`, `IMPLEMENTATION`,
or `OPERATIONS`.

Auto-resolution is permitted only when all are true:

- severity is `LOW` or `MEDIUM`;
- ambiguity is not `HIGH`;
- resolution confidence is at least 85;
- the fix is reversible and stays inside approved scope, acceptance, locked
  public contracts, security boundaries, and delegated authority;
- resolution and verification evidence are recorded.

Otherwise use `HUMAN_APPROVAL_NEEDED`. A scope, acceptance, public-contract,
security-boundary, destructive-data, or irreversible release choice always
requires Human approval regardless of confidence.

## Lifecycle and logging

Create `docs/meta-pds/drift-log.yaml` from the template when the first drift is
detected. Use stable `DRIFT-*` IDs and one of:

```text
DETECTED → TRIAGED → AUTO_RESOLVED → CLOSED
                  ↘ HUMAN_APPROVAL_NEEDED → REVERIFY_REQUIRED → CLOSED
```

Do not delete resolved drift. Increment `occurrence_count` when the same cause
and boundary recur; create a new ID when cause, scope, or resolution changes.
Append meaningful transitions to `delivery-events.jsonl`: detection,
auto-resolution, Human approval request and decision, re-verification, closure,
or recurrence. Never log chat or file-save noise.

Every drift records evidence, affected Truth keys, slices and work packages,
owner, recommendation, impact, resolution, approval record, and the split
between blocked and continuing work.

## Non-blocking scheduling

Pause only the affected dependency closure. Mark affected packages
`BLOCKED_BY_DRIFT` or `REVERIFY_REQUIRED` with the Drift ID in their blocker.
Recompute the ready queue and continue packages whose dependencies and entry
checks remain valid. Never start integration or release work that consumes the
unapproved boundary. An initiative-wide stop is reserved for a critical drift
whose dependency closure covers every safe path.

Human approval remains pending while independent work continues. When the
Human decides, record the decision, revise affected canonical artifacts when
required, mark dependants for re-verification, and close only after evidence
confirms alignment.
