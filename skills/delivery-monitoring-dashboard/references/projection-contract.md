# Delivery Monitoring Projection Contract

## Truth boundary

`docs/monitoring-dashboard/monitoring-data.json` is a read model. It may
summarize authoritative repository and runtime evidence, but it never becomes
the source of delivery truth.

Use this source precedence when records disagree:

1. Verified release manifests, immutable tags, CI, deployment, and E2E
   evidence.
2. The latest reconciled
   `docs/continuous-delivery/<initiative-id>/delivery-control.md`.
3. Locked decisions, accepted change records, and approved ADRs.
4. Approved vertical-slice plans and story ledgers.
5. Draft PRDs, UX documents, prototypes, and planning notes.

Report contradictions in `warnings`. Do not silently pick a more optimistic
status.

## Required JSON shape

The validator accepts schema version `2.x` with these required fields:

```json
{
  "schemaVersion": "2.0.0",
  "generatedAt": "2026-07-31T13:45:00+05:00",
  "source": {
    "kind": "repository-docs",
    "truthBoundary": "Planning projection; release requires verified evidence.",
    "documents": [{"path": "docs/initiatives/example/prd.md", "sections": []}]
  },
  "initiative": {
    "id": "example",
    "productName": "Example",
    "status": "in_review",
    "currentStage": "Initiative definition",
    "currentSliceId": "VS-01",
    "summary": "Definition remains in progress.",
    "lastDocumentUpdate": "2026-07-31"
  },
  "planning": {
    "pendingDecisions": [],
    "lockedDecisions": [],
    "items": []
  },
  "verticalSlices": [],
  "userStories": []
}
```

Additional top-level fields such as `releases`, `environments`, `warnings`, or
`projectionRevision` are allowed and should be preserved.

## Status vocabulary

Use lower snake case:

- initiative: `draft`, `in_review`, `approved`, `in_progress`, `blocked`,
  `paused`, `complete`, `abandoned`, `unknown`;
- planning item: `pending`, `in_progress`, `blocked`, `completed`, `deferred`,
  `unknown`;
- pending decision: `pending`, `blocked`, `deferred`, `unknown`;
- locked decision: `locked`, `superseded`, `unknown`;
- vertical slice: `pending`, `in_progress`, `blocked`, `validation_ready`,
  `released`, `completed`, `deferred`, `abandoned`, `unknown`;
- user story: `pending`, `in_progress`, `blocked`, `validation_ready`, `done`,
  `released`, `deferred`, `abandoned`, `unknown`.

`completed` means the documented planning/prototype outcome finished.
`released` means the releasable customer capability passed its release gate.
Never convert `completed` to `released` without verified release evidence.

## Stable identity and provenance

- Keep IDs stable across refreshes.
- Every story must reference an existing slice through `sliceId`.
- `initiative.currentSliceId`, when present, must reference an existing slice.
- Keep progress numeric from 0 through 100.
- Give each decision, planning item, slice, and story a repository-relative
  `source`, `evidence`, or structured evidence object.
- Record source document paths under `source.documents`.

## Non-blocking synchronization protocol

CDM starts no more than one auxiliary monitoring worker for an initiative.
Material changes arriving during that run set a dirty flag or produce one
follow-up message. The worker re-reads all sources before writing, validates
the complete candidate, atomically replaces only the JSON projection, and
returns `DELIVERY-MONITORING-SYNC-v1`.

The worker does not:

- count as the active delivery stage team;
- change CDM routing, authority, or checkpoints;
- stage, commit, push, merge, deploy, tag, or release;
- alter source documents;
- start another monitoring worker.

If the worker fails, leave the last valid JSON in place and return the exact
validation or source contradiction. CDM records the warning and continues
unaffected delivery work. Before a final initiative report, CDM must obtain a
validated sync or clearly report the dashboard as stale.
