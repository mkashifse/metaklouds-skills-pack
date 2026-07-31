# Dev-Team Workflow and Gates

## 1. Admit one fat slice

Read the complete approved `slice-000N.md` and its cited PRD, UX specification,
prototype validation, locked change records, context, and ADRs. Verify the
capability-family, lifecycle, cross-layer, independent-release, and
whole-journey testability criteria in `SKILL.md`.

If any criterion fails, set the delivery ledger to `RETURNED_TO_PLANNING` with
specific gaps and stop. Do not convert the slice into smaller implementation
increments.

## 2. Establish delivery state

Read the full existing `scrum.md`. Append one section keyed to the source slice
without erasing prior history. Record:

- source slice path, ID, status, and capability promise;
- all mandatory lifecycle features;
- repositories, branches, worktrees, and ownership;
- prototype repository/workspace and evidence status;
- relevant locked `CHG-000N` records;
- supporting skills and architecture precedence;
- status `SPECIFICATION`.

For split repositories, read
[repository-layout.md](repository-layout.md), identify the canonical
coordination repository, and record every code-repository path/worktree/branch.
Create the story map, one file per user story, technical design, integration
contract, test plan, and delivery report from the bundled assets.

## 3. Convert the slice into user stories and engineering tasks

The EM is accountable for the conversion. FE and BE jointly refine feasibility,
dependencies, sequencing, and task ownership. The planning team is consulted
only when scope or acceptance is ambiguous or must change.

Draft `story-map.md` and `stories/US-000N-<slug>.md`:

- Organize stories around observable user/system outcomes, never frontend,
  backend, endpoint, table, or screen layers.
- Give each story behavioral acceptance criteria and map it to source-slice
  lifecycle rows and acceptance scenarios.
- Identify the FE, BE, database/infrastructure, integration, and verification
  task categories needed inside each story; finalize technical actions after
  the design and contract are drafted.
- Map every mandatory slice requirement to at least one story and every story
  to tasks and evidence. Reject gaps, duplication, and scope drift.
- Map every relevant locked change to affected stories/tasks/contracts/tests.
- Record dependencies and execution order without treating a story as a
  release boundary.

Stories may be implementation-sized, but the full slice remains the only
release and product-acceptance unit.

## 4. Freeze whole-slice design and contract

The technical design and contract must cover the complete slice, not only the
first endpoint or screen. Define:

- end-to-end user/system journeys and state transitions;
- frontend/backend/data/integration boundaries;
- shared types, operations, errors, authorization, idempotency, and
  concurrency;
- migration and backward compatibility;
- security, privacy, accessibility, observability, rollout, support, and
  rollback.

Build a test plan that maps every feature-family row and every slice acceptance
scenario through user stories to evidence. Freeze only when FE and BE can
implement their tasks without guessing.

After the design and contract are drafted, have FE and BE finalize technical
tasks, paths, dependencies, and done criteria inside the story files. Freeze
the story map, story/task files, test plan, and contract as one launch package.
Do not launch workers while a relevant locked change remains unsynchronized
with that package.

## 5. Launch the engineers

Create safe branches/worktrees. Spawn exactly one FE and one BE concurrently.
Each prompt includes the source slice, story map, assigned story files, all
delivery docs, the worker's complete cross-story task bundle, owned/forbidden
paths, supporting-skill paths, test expectations, and commit requirement.

FE owns frontend tasks across all stories. BE owns backend/data tasks across all
stories. Shared integration and verification tasks have one explicit owner.

## 6. Review and integrate

For each result:

1. Verify the commit and full changed-file list.
2. Inspect the complete diff and reject ownership/scope drift.
3. Check reported story/task IDs against their acceptance criteria, source
   slice, and frozen contract.
4. Verify supporting-skill evidence and tests.
5. Integrate acceptable commits only.

Set status `INTEGRATING` and run combined verification. A partial component may
be recorded as progress, but the slice remains unreleased.

## 7. Remediate

For every failure record observed evidence, expected behavior, owner, affected
contract version, required verification, status, and resulting commit. Assign
the correction to FE or BE. Rerun the failing scenario, focused suite,
contract/integration checks, and relevant regressions.

Return to planning if remediation reveals that scope or acceptance must change.

## 8. Control runtime changes

Use `$change-management` when new evidence contradicts a locked decision or
creates cross-document/team misalignment.

1. Let the EM lock a contained, reversible, in-scope decision when confident.
2. Log it in the initiative `change-management.md` and inform the user without
   blocking.
3. For severe conditions, request human approval and pause only affected
   stories/tasks/repositories.
4. After locking, run the quick impact analysis and map required updates across
   PRD/UX/prototype, slice, stories/tasks, design/contract/data, security,
   tests, rollout, and repositories.
5. Update EM-owned artifacts immediately and assign owners for other documents.
6. Continue unaffected delivery.

Escalate to `$vertical-slice-team` when the locked decision changes slice scope
or acceptance. Change control never permits partial-slice release.

## 9. Pass the release gates

Require:

- every mandatory capability-family feature delivered;
- every user story accepted and every required engineering task completed;
- complete traceability from slice → story → task → test/evidence;
- every relevant locked change reflected and document synchronization complete;
- complete primary, alternate, recovery, failure, authorization, and security
  lifecycle verified;
- FE and BE cross-story task bundles accepted;
- frozen contract satisfied;
- formatting, linting, type checks, builds, and automated suites pass;
- real whole-slice E2E scenarios pass;
- persistence, migration, compatibility, security, privacy, accessibility,
  observability, rollout, and rollback verified as applicable;
- delivery report and supporting-skill evidence complete;
- no unexplained out-of-scope changes.

Mandatory source-slice scope, baseline lifecycle flows, security boundaries,
and whole-slice E2E proof are non-waivable. Other checks may be waived only
with explicit user authorization plus documented reason and risk; such a waiver
must not make a partial capability appear complete.

## 10. Release and sign off

After local gates:

1. Mark `READY_FOR_PR`.
2. Commit EM-owned artifacts.
3. Push every changed repository.
4. Create or update PRs with outcome, contract, tests, risks, and rollout.
5. Wait for required CI.
6. Have the named repository maintainers/release authority merge and deploy;
   the EM coordinates and verifies but does not assume credentials or authority.
7. Record URLs, commits, CI, environment, deployment/release evidence, release
   authority, and EM sign-off.
8. Update the source slice execution evidence to `DELIVERED`.
9. Mark the ledger `COMPLETE`.

If push, PR, CI, deployment, or a mandatory capability is blocked, record the
blocker and preserve the work. Do not call the slice released or complete.
If release authority or target environment is undefined, resolve it from the
PRD/operating model before merge; unrelated verification may continue.

## 11. Continue

Only after full delivery may the next approved slice start. On later
invocations, read the ledger first, resume unfinished work, avoid duplicate IDs,
and preserve all contracts and evidence.
