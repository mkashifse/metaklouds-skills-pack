---
name: delivery-monitoring-dashboard
description: Maintains a docs-only delivery monitoring dashboard by projecting authoritative initiative, decision, slice, story, and release evidence into monitoring-data.json. Use when creating or refreshing a delivery dashboard, reconciling its JSON with repository documents, or when Continuous Delivery Manager needs a non-blocking monitoring projection worker.
---

# Delivery Monitoring Dashboard

Maintain a truthful, read-only delivery projection under
`docs/monitoring-dashboard/`. Treat repository documents and verified delivery
evidence as authoritative; the dashboard JSON is a replaceable projection.

Read [references/projection-contract.md](references/projection-contract.md)
before updating data. Run
`scripts/validate-monitoring-data.mjs` after every update.

## Ownership and safety

- Write only dashboard-owned files unless the user explicitly broadens scope.
- Never edit initiative, planning, release, or code artifacts to make the
  projection look consistent.
- Never include credentials, tokens, private keys, connection strings, or
  invented environment URLs.
- Preserve unknown JSON fields and existing dashboard UI files.
- Do not claim a slice or story is released from plans, prototypes, open PRs,
  or partial deployments.
- Use `unknown` or an explicit warning when evidence is missing or
  contradictory.

## Projection workflow

1. Resolve the canonical product root and dashboard directory.
2. Read the current JSON, its declared source documents, CDM control files,
   change records, slice plans, story ledgers, and release manifests that
   actually exist.
3. Reconcile in this precedence order: verified release evidence, current CDM
   control state, locked decisions/change records, approved plans, then draft
   planning documents.
4. Project pending and locked decisions, planning items, vertical slices, user
   stories, current work, blockers, and completed releases.
5. Keep stable IDs. Add provenance to every item with a repository-relative
   `source` or structured evidence reference.
6. Update `generatedAt` only after a complete successful projection.
7. Validate:

   ```bash
   node <skill-directory>/scripts/validate-monitoring-data.mjs \
     <root>/docs/monitoring-dashboard/monitoring-data.json <root>
   ```

8. Re-read the written JSON and report counts, warnings, changed/no-change,
   source paths, and validation evidence.

When no dashboard exists, create only the minimal docs-only shell requested by
the user plus `monitoring-data.json`. Do not attach it to a frontend, backend,
or prototype application.

## Non-blocking worker mode

When invoked by Continuous Delivery Manager, act as an auxiliary projection
worker, not a stage team:

- allow at most one monitoring worker in flight per initiative;
- read source artifacts without locking or modifying them;
- accept material transition notices while running and coalesce them into one
  final reconciliation;
- never own route selection, Git integration, releases, or delivery state;
- never delay the active stage team merely to improve dashboard freshness;
- return promptly with `SYNCED`, `UNCHANGED`, or `SYNC_FAILED`;
- a failed sync warns CDM but does not rewrite or roll back authoritative work.

CDM may continue useful delivery work while this worker runs. It should
reconcile the worker result at the next checkpoint and require one final
validated sync before its final initiative report.

Return:

```yaml
contract_version: "DELIVERY-MONITORING-SYNC-v1"
initiative_id: "<id>"
status: "SYNCED | UNCHANGED | SYNC_FAILED"
json_path: "<absolute path>"
source_paths: []
counts: { pending_decisions: 0, locked_decisions: 0, slices: 0, stories: 0 }
validation: { result: "passed | failed", evidence: "<command/output>" }
warnings: []
```

## Refresh triggers

Refresh after a decision locks or reopens, a planning item changes, a slice or
story changes status, a blocker changes, or release/deployment evidence is
verified. Multiple changes during one active sync become one follow-up
reconciliation, not duplicate workers.

## Example prompts

- “Use delivery-monitoring-dashboard to rebuild the JSON from current docs.”
- “Run a non-blocking monitoring sync while CDM continues this slice.”
