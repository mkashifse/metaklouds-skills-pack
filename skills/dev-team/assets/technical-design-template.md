# Technical Design: <Vertical Slice>

## Metadata

- Delivery ID:
- Source slice:
- Status: `DRAFT`
- Owner: Engineering Manager
- Last updated:

## Outcome

<State the complete capability-family and release outcome.>

## Scope

### In scope

- <Every mandatory lifecycle feature in the source slice>

### Out of scope

- <Explicit non-goal>

## Existing system

<Describe relevant architecture, behavior, constraints, and repository locations.>

## Repository map

- Root repository/worktree/branch: `<product>-root` / `main`
- Root prototype path/reference:
- Root launch-package commit:
- Frontend repository/worktree/branch: `slice/<slice-key>`
- Backend repository/worktree/branch: `slice/<slice-key>`
- Root ignore/isolation verification:
- Backend-owned OpenAPI location:
- Frontend generated-client location:

## Cross-repository delivery design

- Exactly one frontend PR and one backend PR:
- Backward-compatibility strategy:
- Database expand/migrate/switch/contract sequence:
- PR merge order:
- Deployment order:
- Feature flag and activation gate:
- Coordinated rollback:

## Story traceability

| Story ID | Observable outcome | Relevant components/data/contracts |
| --- | --- | --- |

## Locked-change traceability

| Change ID | Design/contract impact | Required synchronization |
| --- | --- | --- |

## Supporting-skill policy

- Frontend required skills:
- Backend required skills:
- Existing architecture choices that override generic skill preferences:
- Approved skill deviations:

## Proposed design

<Describe the whole-slice components, journeys, data flow, state transitions,
and important decisions.>

## Capability-family coverage

| Source-slice feature/lifecycle area | Frontend | Backend | Integrated evidence |
| --- | --- | --- | --- |

## Frontend responsibility

<Describe the complete frontend outcome without prescribing microtasks.>

## Backend responsibility

<Describe the complete backend outcome without prescribing microtasks.>

## Cross-cutting concerns

- Security and authorization:
- Privacy:
- Accessibility:
- Performance:
- Observability:
- Compatibility:
- Migration and rollout:
- Feature flags:

## Risks and decisions

| Item | Decision or mitigation |
| --- | --- |
| <Risk> | <Decision> |

## Acceptance criteria

- <Map every source-slice acceptance scenario>

## Partial-release prohibition

State that no component, screen, endpoint, or subset may be released as the
slice. Missing mandatory flow returns the delivery to implementation or
planning.

## Open questions

- <Resolve before freezing the integration contract>
