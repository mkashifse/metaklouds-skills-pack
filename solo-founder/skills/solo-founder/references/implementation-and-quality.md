# Implementation, Quality, Release, and Operations

Implementation begins only for a Human-approved, development-ready Fat Slice.
The PM creates bounded Work Packages and classifies each as `TRIVIAL` or
`NON_TRIVIAL`. Classification does not select the actor: the PM executes each
production change end-to-end by default, including code.

Do not split database, backend, and frontend portions merely because all are
present. Delegate to a Full-Stack Engineer only when the parallelism criteria
in [work-classification.md](work-classification.md) are satisfied. Multiple
engineers require independent Work Packages and a clear PM integration owner.

## Work Package contract

Each package records:

- immutable instruction and expected outcome;
- role, owner identity, focus/workstream, activity, owned paths, and exclusions;
- direct or delegated execution, delegation reason, and typed handoff when
  delegated;
- linked approved Truth and Slice IDs;
- dependencies and acceptance criteria;
- required tests and evidence;
- result, changed paths, timestamps, and blockers.

Use the Product Ledger lifecycle:

```text
PENDING → READY → ACTIVE → VERIFYING → DONE
                         ↘ BLOCKED
VERIFYING → REWORK → ACTIVE
```

For direct work, the PM verifies the result and records completion. For
delegated work, the engineer submits the integrated result, durable evidence,
and complete typed handoff at `VERIFYING`. Only the PM may mark `DONE` or
`REWORK` after consuming the handoff and reviewing acceptance.

## Quality and release

Do not declare a Slice complete because a component, package, commit, PR, or
deployment finished. Require whole-Slice evidence for:

- all acceptance criteria and test expectations;
- integrated frontend/backend behavior and contracts;
- permissions, security, privacy, accessibility, and migrations;
- performance and reliability where material;
- observability, deployment order, rollback, and remaining risks.

Production release requires Human approval unless already delegated in the
authority envelope. Record exact commits, deployments, test commands/results,
and release evidence.

## Outcome validation

After the observation window, compare adoption, task completion, errors,
latency, support incidents, user feedback, and operating findings with approved
business and product outcomes. Recommend continue, modify, rollback, or replan.

## Drift

Drift is any mismatch between implementation evidence and approved Truth,
Slice acceptance, prototype behavior, contracts, or authority. Pause only the
affected dependency closure. Safe reversible implementation details may be
resolved within authority and logged as `RESOLVED` during the next exit sweep;
do not interrupt the work merely to write the Issue. Consequential drift becomes
`AWAITING_HUMAN` with one recommendation and impact. Skip only that action and
continue unrelated work. Durable Human decisions become `PROPOSED` Truth;
one-time authorization remains in the Issue resolution.
