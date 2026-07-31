# CDM Monitoring Sync Protocol

Use `$delivery-monitoring-dashboard` as an auxiliary projection worker whenever
`docs/monitoring-dashboard/monitoring-data.json` exists or the user requests
delivery monitoring.

## Dispatch

After loading and reconciling durable state, dispatch one monitoring worker in
parallel with the next useful delivery action when a worker slot is available.
The stage team has priority when concurrency is constrained. The monitoring
worker is not a stage team, does not own a slice, and does not change CDM
routing or release authority.

Pass:

```text
MONITORING_SYNC_CONTRACT=DELIVERY-MONITORING-SYNC-v1
CDM_INITIATIVE_ID=<initiative-id>
CDM_CONTROL_PATH=<absolute path>
MONITORING_JSON_PATH=<absolute path>
MONITORING_SOURCE_ROOT=<absolute root repository>
MONITORING_WRITE_SCOPE=<absolute monitoring-data.json path>
```

Tell the worker to read the complete
`delivery-monitoring-dashboard` skill and projection contract, preserve
unrelated changes, write only the JSON projection, validate it, and return its
structured result to CDM.

## Coalescing and checkpoints

- Maintain at most one in-flight monitoring worker per initiative.
- Record worker identity, source revision, sync status, pending-refresh flag,
  validation, and warnings in `delivery-control.md`.
- When a decision, planning item, blocker, slice, story, release, deployment,
  or rollback status changes during a sync, set `pending refresh`.
- Send one follow-up reconciliation to the existing worker when supported;
  otherwise start one new sync only after the existing worker returns.
- Do not wait before starting or continuing the owning stage team.
- Reconcile completed worker output at the next normal CDM checkpoint.
- Verify the JSON exists, parses, passes the skill validator, and reports only
  evidence CDM can independently trace.

## Failure policy

`SYNC_FAILED` is an observability warning, not authority to roll back delivery
state. Keep the last valid JSON, persist the error, and continue unaffected
work. Retry only after source evidence or the diagnosed failure changes; do not
busy-loop.

Before the final initiative report, require one final worker reconciliation. If
it still fails after bounded remediation, finish delivery only when all normal
delivery gates pass and prominently report the dashboard as stale with the last
validated time and exact failure.
