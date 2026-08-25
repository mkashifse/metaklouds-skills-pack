# Implementation, Quality, Release, and Operations

Implementation begins only for a Human-approved, development-ready Fat Slice.
The PM creates bounded Work Packages and classifies each as `TRIVIAL` or
`NON_TRIVIAL`. Production implementation is normally non-trivial and directly
assigned to the relevant specialist.

## Work Package contract

Each package records:

- immutable instruction and expected outcome;
- owner, workstream, activity, owned paths, and exclusions;
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

The specialist submits result and durable evidence at `VERIFYING`. Only the PM
may mark `DONE` or `REWORK` after acceptance review.

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
resolved within authority; consequential drift becomes `PROPOSED` Truth or a
Human decision with one recommendation and impact.
