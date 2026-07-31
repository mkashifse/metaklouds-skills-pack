# Test Plan: <Vertical Slice>

## Metadata

- Delivery ID:
- Source slice:
- Contract version:
- Owner: Engineering Manager
- Status: `DRAFT`

## Verification environments

- Frontend:
- Backend:
- Integrated application:
- Required fixtures:

## Scenario matrix

| ID | Story ID(s) | Level | Scenario | Preconditions | Expected outcome | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TS-01 | All | E2E | Complete baseline lifecycle | <State> | <Whole capability promise succeeds> | EM | |
| TS-02 | <US> | E2E | Recovery lifecycle | <State> | <User recovers without bypassing contract> | EM | |
| TS-03 | <US> | FE | UI state family | <States> | <All applicable states work accessibly> | FE | |
| TS-04 | <US> | BE | Authorization/security matrix | <Identities> | <Allowed/denied behavior matches contract> | BE | |
| TS-05 | <US> | Integration | Failure and retry | <Dependency failure> | <Safe observable recovery> | EM | |
| TS-06 | All | Regression | Existing behavior | <State> | <No regression> | EM | |

## Required coverage

- Complete end-to-end lifecycle
- Alternate and recovery flows
- Loading and empty states
- Client and server validation
- Authentication and authorization
- Contract errors and unexpected failures
- Boundary values and concurrency
- Accessibility and responsive behavior
- Persistence, migration, and compatibility
- Observability and operational behavior
- Relevant regressions
- Release, observability, support, and rollback evidence

## Locked-change verification

| Change ID | Affected scenarios | Required regression/impact evidence | Status |
| --- | --- | --- | --- |

## Quality commands

### Frontend

- Format:
- Lint:
- Type check:
- Tests:
- Build:

### Backend

- Format:
- Lint:
- Type check:
- Tests:
- Build:

### Integrated

- Contract tests:
- Integration tests:
- End-to-end tests:

## Final results

- Passed:
- Failed:
- Skipped or waived (never mandatory scope, security, or whole-slice E2E):
- Remaining risks:
