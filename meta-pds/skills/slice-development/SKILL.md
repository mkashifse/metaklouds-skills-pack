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
- `references/testing-and-browser-policy.md`;
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

Inspect the repository, freeze or cite the technical contract, then define:

- bounded work packages and explicit owners;
- requirements/stories supported by each package;
- inputs, outputs, owned and forbidden paths;
- dependency DAG, critical path, and parallel waves;
- entry, exit, and required test checks;
- integration, compatibility, migration, merge, deploy, feature-flag,
  observability, and rollback order.

Use the exact structured fields in the execution-plan template. Give every
contract, test case, and work package a stable ID; packages cite stories through
`supports`, dependencies through `depends_on`, and test cases through
`required_tests`. Update package and development-test state in this existing
plan rather than creating status summaries for the dashboard.

Treat the product root as one Git repository. Assign work through isolated
`frontend/` and `backend/` owned paths. Do not create nested repositories or
submodules, and do not introduce direct source-code imports between those
areas. Coordinate cross-area behavior through the recorded integration
contracts.

Run the Meta PDS validator. The Product Manager marks `EXECUTION_READY` only
when the plan has no cycles, unknown dependencies, unowned packages, missing
tests, or unresolved entry blockers.

### Execution

Launch only `READY` packages. Use the minimum applicable worker roles:

- Frontend Engineer;
- Backend/Domain Engineer;
- Database/Migration Engineer;
- Integration Engineer;
- Security Engineer.

Workers report to the Development Lead, never directly to the Human. Each
worker receives one compact context capsule and one bounded package. A package
may support one or several user stories; it is an implementation assignment,
not a release or a substitute user story.

After every result:

1. verify the exact changed paths and local commits;
2. verify acceptance, contract version, ownership, and CLI test evidence;
3. reject scope or path drift;
4. update package status and unblock dependants only when exit checks pass;
5. run combined verification when all required packages finish;
6. return upstream if implementation reveals missing scope or acceptance.

Use:

```text
BLOCKED → READY → IN_PROGRESS → VERIFYING → DONE
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

- workers may create local commits on assigned branches;
- no Development role pushes, opens/merges PRs, tags, deploys, or changes
  production flags;
- the Product Manager validates and performs external integration/release
  actions.

Do not edit upstream initiative or slice content. Return deficiencies or change
requests to their owner.

## Result

Return one of:

```yaml
status: FEASIBLE | NEEDS_UPSTREAM_CLARIFICATION | EXECUTION_PLAN_READY | READY_FOR_QA | REWORK_REQUIRED | HUMAN_DECISION_REQUIRED | BLOCKED
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
recommended_next_action: ""
```
