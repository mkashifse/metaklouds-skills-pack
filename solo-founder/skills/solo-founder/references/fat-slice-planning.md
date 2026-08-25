# Fat Slice Planning

A Fat Slice is one coherent capability family delivering independently usable
baseline value. It is not a screen, endpoint, table, Layer, technical task, or
arbitrary time box. It crosses every relevant UX, client, service, domain,
data, integration, security, and operational boundary.

## Entry

Require:

- sufficient production-intent prototype evidence;
- current `APPROVED` Truth for the proposed scope;
- an approved prototype checkpoint and promotion map when applicable;
- one exact capability outcome and Slice ID.

If product intent is unclear or a proposal contains multiple independently
valuable capability families, return it to Discovery instead of drafting
around ambiguity.

## Slice contents

Write `docs/solo-founder/slices/<slice-id>.md` from the bundled template. Cover:

- outcome, target actor, scope, boundary, and non-goals;
- primary, alternate, failure, recovery, permission, expiry, retry, and
  destructive flows when relevant;
- observable User Stories and measurable acceptance criteria;
- stable test expectations owned by the Slice;
- security, privacy, accessibility, and operations;
- contract expectations, state transitions, dependencies, assumptions, risks;
- observability, support, rollout, and rollback;
- requirement-to-story-to-test-to-evidence traceability;
- prototype source checkpoint and promotion map.

The PM owns and writes the Slice. It handles feasibility directly by default.
Delegate only an independently bounded feasibility question whose parallel
execution is expected to be net faster, then consume its typed handoff and
incorporate verified evidence without transferring ownership.

## Development gate

Development may begin only when the specific Slice:

1. is explicitly Human-approved;
2. depends only on `APPROVED` Truth;
3. has no blocking contradiction or decision;
4. is structurally complete and traceable;
5. passes Development Intake against the actual repositories;
6. has bounded Work Packages, dependencies, owners, paths, and verification.

Approval is per Slice. One approved ready Slice may execute while later Slices
remain proposed or in Discovery.
