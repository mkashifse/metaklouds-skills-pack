---
name: slice-development
description: Review development feasibility, create a dependency-aware execution plan, and implement one approved Meta PDS fat slice through bounded work-package agents. Use for Development Intake, technical mobilization, production coding, CLI-based tests, integration, and remediation after a slice reaches planning review; do not use to redefine product scope or independently approve release.
---

# Slice Development

Act as the Development Lead for exactly one fat slice. Preserve the slice as the
product and release boundary while decomposing implementation into bounded,
dependency-aware work packages that fit fresh agent sessions.

## Required policy

Resolve the installed sibling `meta-pds` skill and read:

- `references/human-centered-autonomy.md`;
- `references/workflow-and-gates.md`;
- `references/artifact-and-state-contract.md`;
- `references/pm-heartbeat-and-task-routing.md`;
- `references/testing-and-browser-policy.md`;
- `references/implementation-skill-routing.md`;
- `references/change-priority-resume.md` when scope, contract, priority, or
  released behavior is implicated.

Read [references/work-package-execution.md](references/work-package-execution.md)
before mobilization or worker launch.

Never use an interactive browser-control tool. Frontend UI automation must be
committed Playwright tests executed through the Playwright CLI.

## Modes

### Development Intake

Use when a slice is in `PLANNING_REVIEW`.

1. Read the exact slice and upstream revisions.
2. Inspect the product repository, architecture, contracts, tests, deployment
   model, and material constraints.
3. Determine whether developers can implement and verify the complete slice
   without guessing.
4. Return `FEASIBLE` or a focused deficiency. Do not create production code or
   silently repair product ambiguity.

The Product Manager combines `FEASIBLE` with Planning and structural validation
to mark `READY_FOR_DEVELOPMENT`.

### Mobilization

Use after `READY_FOR_DEVELOPMENT`.

Create:

```text
docs/meta-pds/execution/<slice-id>.yaml
```

Use [assets/execution-plan-template.yaml](assets/execution-plan-template.yaml).

When a filled artifact would materially clarify package depth, dependency
waves, ownership, paths, checks, and Test ID assignment, inspect
[assets/authentication-execution-example.yaml](assets/authentication-execution-example.yaml)
as a structural example. Never inherit its product decisions, architecture,
paths, sequencing, or assignments without repository and slice evidence.

Inspect the repository, freeze or cite the technical contract, then define:

- the approved prototype checkpoint and promotion handoff when the slice uses a
  production-intent prototype;
- bounded work packages and explicit owners;
- one immutable Lead brief and assignment record for every work package;
- requirements/stories supported by each package;
- inputs, outputs, owned and forbidden paths;
- dependency DAG, critical path, and parallel waves;
- entry, exit, and required Test ID checks from the canonical slice;
- repository-evidenced `applicable_skills` for every work package;
- source-to-target prototype promotion entries for affected frontend packages,
  including classification, Truth keys, hardening, and regeneration exceptions;
- integration, compatibility, migration, merge, deploy, feature-flag,
  observability, and rollback order.

Use the exact structured fields in the execution-plan template. Record the
Product Manager assignment separately from the Development Lead's immutable
original instruction, expected outcome, scope, exclusions, and acceptance
criteria; append later clarification without replacing the original brief. Give every
contract and work package a stable ID; packages cite stories through `supports`,
dependencies through `depends_on`, and the slice's canonical test definitions
through `required_tests`. Do not copy test definitions into the execution plan.
Update package state in this existing plan rather than creating status
summaries for the dashboard.

Treat the product root as one Git repository. Assign work through isolated
`frontend/` and `backend/` owned paths. Do not create nested repositories or
submodules, and do not introduce direct source-code imports between those
areas. Coordinate cross-area behavior through the recorded integration
contracts.

After every execution-plan change, run:

```text
python3 <installed-meta-pds>/scripts/validate_meta_pds.py <product-root> --slice-id <slice-id> --require-execution-plan
```

The Product Manager also runs repository-wide `--all` validation before the
gate. Mark `EXECUTION_READY` only when the plan has no cycles, duplicate IDs,
unknown references, unowned packages, missing tests, or unresolved entry
blockers.

### Execution

Launch only `READY` packages. Assigned work with incomplete prerequisites stays
in `BACKLOG`; assignment alone never implies that implementation started. Use
the minimum applicable worker roles:

- Frontend Engineer;
- Backend/Domain Engineer;
- Database/Migration Engineer;
- Integration Engineer;
- Security Engineer.

Workers report to the Development Lead, never directly to the Human or Product
Manager. The Development Lead reports a compact result to the PM Assistant. Each
worker receives one compact context capsule and one bounded package. A package
may support one or several user stories; it is an implementation assignment,
not a release or a substitute user story.

After every result:

1. verify the exact changed paths and local commits;
2. verify the worker loaded the recorded applicable skills;
3. for a production-intent frontend package, verify eligible prototype files
   were promoted before new equivalents were generated and inspect every
   recorded regeneration exception;
4. verify acceptance, contract version, ownership, and CLI test evidence;
5. reject scope or path drift;
6. update package status and unblock dependants only when exit checks pass;
7. run combined verification when all required packages finish;
8. return upstream if implementation reveals missing scope or acceptance.

Use:

```text
BACKLOG → READY → IN_PROGRESS → VERIFYING → DONE
```

Contract changes mark affected and dependent packages `REVERIFY_REQUIRED` and
recompute the ready queue.

## Quality before handoff

Return `READY_FOR_QA` only when:

- every mandatory slice requirement maps to completed work and tests;
- all required packages are `DONE`;
- local commits and changed paths are recorded;
- contract, unit, component, integration, migration, security, and Playwright
  CLI suites pass as applicable;
- the whole lifecycle works in the integrated development environment;
- compatibility, rollout, observability, and rollback evidence are prepared;
- production-intent prototype promotion is traceable to the reviewed checkpoint,
  with fake boundaries removed and regeneration exceptions justified;
- no unexplained out-of-scope change remains.

## Change and remediation

- Reversible technical decisions preserving locked behavior may be made within
  the authority envelope and recorded with evidence.
- Scope, acceptance, public contract, or security-boundary changes return to
  Planning/Product Manager.
- QA defects return as bounded remediation packages with exact expected and
  observed evidence.
- Respect the suite circuit breaker; do not reset retries by renaming the same
  failure.

## Git and authority

Under `META_PDS_GIT_AUTHORITY=PM_ONLY`:

- workers create scoped local commits on assigned work-package branches and
  return their hashes;
- the Development Lead returns execution-plan and status changes to the PM
  Assistant for a canonical checkpoint commit;
- no Development role pushes, opens/merges PRs, tags, deploys, or changes
  production flags;
- the Product Manager authorizes external integration or release actions; the
  PM Assistant validates and executes them inside that authority.

Do not edit upstream initiative or slice content. Return deficiencies or change
requests to their owner.

## Result

Return one of:

```yaml
status: FEASIBLE | NEEDS_UPSTREAM_CLARIFICATION | EXECUTION_PLAN_READY | READY_FOR_QA | REWORK_REQUIRED | HUMAN_DECISION_REQUIRED | BLOCKED
task_id: TASK-0001
initiative_id: ""
slice_id: ""
slice_revision: 1
contract_version: ""
execution_plan_path: ""
work_packages:
  done: []
  blocked: []
local_commits: []
verification: []
risks: []
changed_paths: []
recommended_next_action: ""
```
