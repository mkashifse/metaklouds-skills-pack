# Fat-Slice Planning Readiness

## Fat-slice invariant

A fat slice is one coherent capability family that delivers independently
usable baseline value. It is not a screen, endpoint, table, layer, technical
task, or arbitrary time box.

It must:

- include every mandatory lifecycle flow needed for its baseline promise;
- cross every relevant UX, client, service, domain, data, integration, and
  operational boundary;
- include alternate, recovery, failure, permission, and security behavior;
- be demonstrable and testable from a real user or system boundary;
- be deployable, observable, supportable, and rollbackable;
- provide value without a mandatory follow-up slice.

If the slice appears too large, first test whether it contains multiple
independently valuable capability families. Do not split mandatory lifecycle
steps merely to make implementation smaller. Development may use many bounded
work packages while the slice remains one release unit.

## `PLANNING_REVIEW` checklist

All must be supported by evidence:

- outcome, target actor, boundary, scope, and non-goals are explicit;
- source initiative and decision revisions are current;
- primary, alternate, failure, recovery, permission, expiry, retry, and
  destructive flows are defined where relevant;
- stories describe observable outcomes across layers;
- acceptance is measurable and testable;
- security, privacy, accessibility, and operations are addressed or explicitly
  justified as not applicable;
- contract expectations and state transitions are unambiguous enough for
  feasibility review;
- dependencies, assumptions, risks, rollout, observability, support, and
  rollback are recorded;
- every requirement maps to a story and acceptance evidence;
- no development-blocking decision or contradiction remains;
- specialist reviews required by material risk are complete.

## Development Intake boundary

Planning validates product completeness. Development Intake independently
checks whether the actual repositories can implement the promise without
guessing. Only the Product Manager may combine both results and mark
`READY_FOR_DEVELOPMENT`.
