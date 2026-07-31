---
name: vertical-slice-team
description: Three-person planning-only team that converts an approved initiative into fat, coherent, end-to-end vertical slices and a dev-team-ready handoff. Use after initiative definition and before implementation.
---

# Vertical Slice Team

Convert approved initiative documents into fat, independently releasable
capability-family slices. This team plans; it never implements application code.

## Team

Use exactly three roles:

- Planning Lead / Delivery Manager (lead)
- Product and Domain Analyst
- Solution Architect and QA Planner

The lead owns scope, sequence, decisions, artifacts, and readiness. The analyst
owns capability completeness, journeys, rules, and user value. The
Architect/QA Planner owns cross-layer feasibility, contracts, security,
operations, dependencies, and end-to-end acceptance.

## Entry modes

### Coordinator mode

When no `VERTICAL_SLICE_ROLE` marker is present:

1. Confirm subagent tools are available.
2. Spawn exactly one lead with `VERTICAL_SLICE_ROLE=LEAD`.
3. Include the initiative, repository paths, constraints, and this skill path.
4. Instruct the lead to read this file and own the other two workers.
5. Do not spawn the analyst or architect directly.

### Lead mode

When `VERTICAL_SLICE_ROLE=LEAD` is present:

1. Read `CONTEXT-MAP.md` when present, then the relevant PRD, UX specification,
   prototype validation, `change-management.md`, `CONTEXT.md`, ADRs,
   architecture, prototype/code, tests, and prior slice history.
2. Resolve and read `$change-management`; create the initiative change log if
   it is missing.
3. Spawn exactly one Product/Domain Analyst and one Architect/QA Planner as
   direct subagents.
4. Resolve planning decisions and capability boundaries.
5. Write the planning artifacts below.
6. Run the fat-slice readiness review and approve only complete slices.

Workers may inspect code and tests but must not modify application code, create
implementation branches, commit product changes, or execute the dev-team
workflow.

For multi-repository products, create planning artifacts only in the canonical
`<product>-root` repository. The root also contains
`prototypes/<initiative-id>/`. Treat nested, independently versioned frontend
and backend repositories as read-only planning inputs; never copy slice
documents into them or stage them in the root repository. Treat the root
prototype as behavioral evidence, not production architecture.

## The fat vertical-slice invariant

A vertical slice is one complete, coherent capability family, not one screen,
endpoint, table, happy path, or engineering layer.

Every slice must:

- deliver usable baseline value through every relevant layer: UX, client, API,
  domain logic, data, authorization, integrations, and operations;
- include the capability's essential lifecycle, alternate, recovery, failure,
  permission, and security flows;
- be independently deployable, releasable, observable, supportable, and
  rollbackable;
- be fully testable end to end from a real user or system boundary;
- require no mandatory follow-up slice before the capability's baseline promise
  is usable.

Screens, endpoints, migrations, and test suites are features inside a slice.
They are never slices by themselves. Do not split a capability merely to make
implementation smaller. Reduce optional depth, advanced variants, scale, or
adjacent capabilities while keeping the baseline lifecycle whole.

Authentication example: signup, verification/OTP, login, session handling,
logout, forgot password, reset password, expiry/retry/error states, and required
security controls form one authentication slice. “Build login” is not a valid
slice.

A slice need not be the whole product. It is bounded by one capability family
whose complete lifecycle can be released and evaluated independently.

## Planning workflow

1. Preserve unrelated work and establish authoritative inputs.
2. Record conflicts, assumptions, dependencies, package/platform constraints,
   and user decisions in `planning-decisions.md`.
3. Build a capability-family map from the PRD and UX journeys.
4. Group mandatory lifecycle features into fat slices.
5. Sequence slices by user value and dependency without breaking a lifecycle.
6. Define contracts, security, data, operations, rollout, and whole-journey
   acceptance for each slice.
7. Run the readiness checklist with both specialist workers.
8. Define the shared slice key, required frontend/backend repositories,
   compatibility strategy, merge/deploy order, and feature-flag expectation.
9. Mark a slice `READY_FOR_DEV_TEAM` only when all checks pass.
10. Commit and push the planning artifacts directly to root `main`; do not
    create a root PR.

Ask only unresolved high-impact questions. Do not re-ask facts answered by
source documents or code. Return contradictions in initiative scope to
`$meta-grill-team`; do not silently redefine the product.

When runtime evidence reveals a misalignment after decisions are locked, use
`$change-management`. The Planning Lead may lock a contained, reversible,
in-scope decision when confident, append it to
`docs/initiatives/<initiative-id>/change-management.md`, run the quick impact
analysis, inform the user, and continue. Human approval is required only for
the severe conditions defined by that skill; pause affected planning only.
Update vertical-slice artifacts owned by this team and assign owners for every
upstream/downstream synchronization action.

Precedence:

- If the existing initiative outcome already implies the correction and scope
  remains unchanged, the Planning Lead may lock first and assign the Initiative
  Lead to synchronize upstream documents.
- If product intent is ambiguous or the decision materially changes initiative
  scope/acceptance, do not lock it as a lead decision; return it to the
  Initiative Lead and use human approval when required.
- A temporary change-record overlay may keep planning moving, but no slice may
  become `READY_FOR_DEV_TEAM` until all affected PRD, UX, prototype-validation,
  context/ADR, planning, and slice documents are synchronized.

## Deliverables

Create only planning artifacts:

```text
docs/vertical-slices/<initiative-id>/planning-decisions.md
docs/vertical-slices/<initiative-id>/vertical-slice-plan.md
docs/vertical-slices/<initiative-id>/slice-0001.md
docs/vertical-slices/<initiative-id>/slice-0002.md  # only another distinct capability family
```

Use:

- [assets/planning-decisions-template.md](assets/planning-decisions-template.md)
- [assets/vertical-slice-plan-template.md](assets/vertical-slice-plan-template.md)
- [assets/slice-template.md](assets/slice-template.md)

Use IDs `VS-0001`, `VS-0002`, and so on within an initiative. The plan maps
capability families and release order. Each slice file is the binding dev-team
input. Keep implementation mechanics at the level needed to remove ambiguity;
do not produce user stories, engineering task lists, or worker reports.

Define the cross-repository slice key as `<initiative-id>-VS-0001`. Require the
dev team to use `slice/<slice-key>` in both code repositories, create exactly
one frontend PR and one backend PR, and create no root PR. Planning specifies
compatibility and release constraints without dictating engineering microtasks.

Default to one slice file for one capability family. Create another numbered
slice only when it is a genuinely different capability family that independently
passes every fat-slice invariant. Never use another file to defer a mandatory
lifecycle feature from the current family.

## Readiness gate

Reject or return a slice when any answer is no:

- Is this one recognizable capability family?
- Does it include the complete baseline lifecycle and mandatory recovery,
  failure, authorization, and security paths?
- Does it cross all relevant product and technical layers?
- Is the whole journey demonstrable and testable end to end?
- Can it be deployed, released, observed, supported, and rolled back on its own?
- Does it deliver value without a mandatory follow-up slice?
- Are scope, non-goals, contracts, data, dependencies, rollout, and acceptance
  unambiguous?
- Are prototype evidence and all locked change records reflected or explicitly
  dispositioned?
- Are all affected upstream and planning documents synchronized, with no
  temporary overlay crossing the readiness gate?
- Are the root, frontend, and backend repositories identified, with nested code
  repositories ignored by the root and a shared slice key defined?
- Are compatibility, merge/deploy order, feature flags, and whole-slice release
  coordination explicit enough for implementation planning?
- Can the dev team deliver the full slice without silently shrinking it?

Approved output status: `READY_FOR_DEV_TEAM`.

The handoff is exactly one approved `slice-000N.md` plus its cited source
documents, root prototype validation/reference, relevant locked change records,
and the root `main` commit containing them. The slice stays product-complete
but implementation-high-level: dev-team's EM owns
conversion into user stories, and FE/BE own refinement into engineering tasks.
Recommend `$dev-team` for implementation. The next slice remains locked until
the current slice is fully released or explicitly abandoned and replanned.
