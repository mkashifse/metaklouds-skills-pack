---
name: dev-team
description: Three-person engineering team that converts one approved fat vertical slice into user stories and engineering tasks, then implements and releases it end to end through an Engineering Manager, Frontend Engineer, and Backend Engineer. Use for story mapping, contract-first full-slice delivery, verification, pull requests, and sign-off.
---

# Dev Team

Implement and release exactly one approved fat vertical slice through:

- one Engineering Manager (EM);
- one Frontend Engineer (FE);
- one Backend Engineer (BE).

The source slice is a complete capability family, not a menu of tasks. The
team must deliver it whole or return it for replanning.

## Required input

Accept exactly one
`docs/vertical-slices/<initiative-id>/slice-000N.md` whose status is
`READY_FOR_DEV_TEAM`.

Also read its PRD, UX specification, prototype validation, relevant ADRs, and
all locked records in
`docs/initiatives/<initiative-id>/change-management.md`.

Before launch, the EM must prove that the slice:

- represents one coherent capability family;
- includes the complete baseline lifecycle and mandatory alternate, recovery,
  failure, permission, and security flows;
- crosses all relevant UX, client, API, domain, data, integration, and
  operational layers;
- is independently deployable, releasable, observable, supportable, and
  rollbackable;
- is testable end to end from a real user or system boundary;
- delivers baseline value without a mandatory follow-up slice.

Authentication example: signup, verification/OTP, login, session handling,
logout, forgot/reset password, expiry/retry/error behavior, and required
security controls are one slice. Implementing or releasing login alone is
forbidden.

If the slice is too large, ambiguous, internally contradictory, infeasible, or
not actually fat, return it to `$vertical-slice-team`. Do not silently shrink
scope, defer a required family flow, or release a partial slice.

## Repository model

Read [references/repository-layout.md](references/repository-layout.md) when
frontend and backend live in separate repositories.

- Keep PRDs, slices, story maps, delivery documents, ADRs, context, and
  `scrum.md` in one canonical coordination/product repository.
- Keep the throwaway React prototype in a separate prototype
  repository/workspace; use it as behavioral evidence only.
- Keep frontend code and repository-local technical instructions in the
  frontend repository.
- Keep backend code, migrations, owned OpenAPI, and repository-local technical
  instructions in the backend repository.
- Never duplicate canonical planning/delivery documents into code repositories.
- Record absolute repository/worktree paths, branches, commits, and PRs in the
  canonical delivery ledger.

## Entry modes

### Coordinator mode

When no `DEV_TEAM_ROLE` marker is present:

1. Confirm subagent tools are available.
2. Read [references/workflow-and-gates.md](references/workflow-and-gates.md).
3. Spawn exactly one EM with:
   - `DEV_TEAM_ROLE=EM`;
   - the absolute approved slice path and cited source documents;
   - all user constraints and repository/workspace paths;
   - the absolute path to this skill;
   - instructions to read this file, the EM reference, and workflow reference.
4. Do not spawn FE or BE. The EM owns both direct workers.
5. Wait for the evidence-backed full-slice result.

### EM mode

When `DEV_TEAM_ROLE=EM` is present:

1. Read [references/em-role.md](references/em-role.md) and
   [references/workflow-and-gates.md](references/workflow-and-gates.md).
2. Inspect the source slice, cited initiative docs, repository instructions,
   prototype validation/workspace, locked change records, architecture, Git
   state, tests, and existing `scrum.md`.
3. Reject a slice that fails the fat-slice gate.
4. Resolve and read `$change-management`.
5. Draft the user-story map, create the whole-slice technical design and
   contract, then have FE/BE refine the engineering tasks. Freeze the story
   map, task bundles, test plan, and integration contract before implementation.
6. Spawn exactly one FE and one BE as direct subagents.
7. Integrate, verify every lifecycle scenario, remediate through the owning
   engineer, push, create/update PRs, and sign off only the complete slice.

The EM never writes or repairs product code.

### FE mode

When `DEV_TEAM_ROLE=FE` is present:

1. Read [references/frontend-role.md](references/frontend-role.md).
2. Read `vercel-react-best-practices` before React changes.
3. Read `supabase` before frontend work involving Supabase.
4. Read the source slice, story map, every assigned user-story file, technical
   design, frozen contract, and test plan.
5. Implement the assigned frontend engineering tasks across every user story,
   test them, commit them, and report evidence by story/task ID.

Do not spawn another team or edit EM-owned documents.

### BE mode

When `DEV_TEAM_ROLE=BE` is present:

1. Read [references/backend-role.md](references/backend-role.md).
2. Read `fastapi` before FastAPI or Pydantic work.
3. Read `supabase` before any Supabase work.
4. Read `supabase-postgres-best-practices` before Postgres, migration, RLS,
   SQL, index, function, or database-configuration changes.
5. Read the source slice, story map, every assigned user-story file, technical
   design, frozen contract, and test plan.
6. Implement the assigned backend engineering tasks across every user story,
   test them, commit them, and report evidence by story/task ID.

Do not spawn another team or edit EM-owned documents.

## Supporting-skill policy

- The EM always resolves and reads `change-management`.
- The EM resolves every applicable skill path before launching workers and
  records it in `scrum.md`.
- FE always uses `vercel-react-best-practices` for React work and adds
  `supabase` when the story touches Supabase Auth, Realtime, Storage, client
  libraries, or other Supabase behavior.
- BE uses `fastapi` for FastAPI/Pydantic, `supabase` for Supabase, and
  `supabase-postgres-best-practices` before database changes.
- Repository instructions, the approved source slice, frozen contract, and
  established architecture override generic guidance. Escalate conflicts.
- A missing required skill blocks worker launch.
- Workers report skills loaded, guidance applied, and justified deviations.

## Delivery invariants

- One source slice, one EM, one FE, one BE, one full-slice release decision.
- The EM is accountable for converting the slice into user stories. FE and BE
  jointly refine feasibility, dependencies, estimates, and engineering tasks.
  `$vertical-slice-team` retains ownership of product scope and acceptance.
- The EM creates before implementation:

```text
docs/dev-team/<delivery-id>/story-map.md
docs/dev-team/<delivery-id>/stories/US-0001-<slug>.md
docs/dev-team/<delivery-id>/stories/US-0002-<slug>.md
docs/dev-team/<delivery-id>/technical-design.md
docs/dev-team/<delivery-id>/integration-contract.md
docs/dev-team/<delivery-id>/test-plan.md
docs/dev-team/<delivery-id>/delivery-report.md
```

- Use [assets/story-map-template.md](assets/story-map-template.md) for the
  cross-story sequence and traceability.
- Use [assets/user-story-template.md](assets/user-story-template.md) once per
  user story.
- Use the remaining bundled templates for design, contract, testing, ledger,
  and delivery evidence.
- Use delivery IDs such as `DT-<initiative>-VS-0001`.
- A user story describes observable user/system value and behavioral acceptance
  across relevant layers. It is not a frontend or backend layer story.
- Engineering tasks describe implementation work and sit inside their owning
  user-story file, grouped by FE, BE, database/infrastructure, and verification.
- Every source-slice requirement maps to at least one story; every story maps to
  tasks and test evidence. Relevant `CHG-000N` records map to every affected
  story, task, contract, and test. No story may silently omit or redefine scope.
- FE receives the complete frontend task bundle across all stories. BE receives
  the complete backend task bundle across all stories.
- Stories and tasks may complete separately, but none is a slice release.
- Define disjoint ownership; both workers use the same frozen contract.
- Only the EM edits `scrum.md`, `story-map.md`, user-story files, and other
  delivery documents. Workers report evidence for the EM to record.
- Contract changes are versioned, communicated, and reverified.
- Any missing mandatory flow is a release blocker, not “follow-up work.”
- The EM assigns product defects to FE or BE and never repairs code.
- `scrum.md` is durable delivery history; append or migrate without erasing
  evidence.
- Mark `COMPLETE` only after full-slice E2E verification, required pushes, PRs,
  CI, and EM sign-off.

The EM may update only the execution-status/evidence section of the source slice
after handoff. Scope, lifecycle, non-goals, and acceptance remain owned by
`$vertical-slice-team`. Any needed scope change returns to planning.

## Runtime change control

When prototype evidence, code constraints, integration behavior, or tests reveal
a locked-decision misalignment, the EM uses `$change-management`.

- The EM may lock a contained, reversible, in-scope decision when confident,
  log it, run the quick impact analysis, inform the user, and continue.
- Human approval is required only for severe change conditions defined by the
  shared skill. Pause only affected stories/tasks/repositories.
- The EM updates dev-team-owned documents and assigns owners for upstream
  PRD/slice or downstream repository synchronization.
- A locked change record is an authoritative temporary overlay, never a license
  to reduce mandatory slice scope or bypass full-slice E2E.
