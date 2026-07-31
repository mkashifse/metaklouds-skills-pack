# Integration Contract: <Vertical Slice>

## Metadata

- Delivery ID:
- Source slice:
- Version: 1
- Status: `DRAFT`
- Owner: Engineering Manager
- Consumers: Frontend Engineer, Backend Engineer
- Frozen at:

## Boundary overview

<Describe how the complete capability family integrates across all relevant
layers.>

## Lifecycle coverage

| Lifecycle area | Story ID(s) | Operations and states | Contract owner |
| --- | --- | --- | --- |

## Authentication and authorization

- Authentication mechanism:
- Required permissions:
- Unauthorized behavior:
- Forbidden behavior:

## Operations

### <Operation name>

- Story ID(s):
- Transport/method:
- Path/topic:
- Purpose:
- Idempotency:
- Concurrency behavior:

Request:

```json
{}
```

Success response:

```json
{}
```

Errors:

| Condition | Status/code | Payload | Frontend behavior |
| --- | --- | --- | --- |
| <Condition> | <Code> | <Shape> | <Expected behavior> |

## Shared types and schemas

<Define fields, types, required/optional rules, formats, nullability, and examples.>

## Validation rules

- <Rule and error behavior>

## State transitions and invariants

- <Allowed transition>
- <Invariant>

## Collection behavior

- Pagination:
- Filtering:
- Sorting:
- Empty results:

## Compatibility and rollout

- Contract versioning:
- Backward compatibility:
- Additive/expand changes:
- Data migration/backfill:
- Consumer switch:
- Contract/cleanup:
- Frontend PR and merge SHA:
- Backend PR and merge SHA:
- PR merge order:
- Deployment order:
- Feature flag and initial state:
- Flag enablement gate:
- Coordinated rollback:
- Deprecation:

## Fixtures

<Provide canonical success, empty, validation-error, forbidden, and failure examples.>

## Contract verification

- Frontend mock/consumer verification:
- Backend provider/contract verification:
- Integrated verification:
- Whole-slice post-deploy E2E:

## Change log

| Version | Status | Change / CHG reference | FE notified | BE notified |
| --- | --- | --- | --- | --- |
| 1 | `DRAFT` | Initial contract | No | No |
