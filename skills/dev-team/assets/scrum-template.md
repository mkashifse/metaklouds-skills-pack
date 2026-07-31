# Development Scrum

This file is the persistent delivery ledger for fat vertical slices managed by
the dev team. Preserve completed delivery history and append each new slice.

## DT-<initiative>-VS-0001: <Capability family>

### Source slice

- ID: `VS-0001`
- Slice key: `<initiative-id>-VS-0001`
- Document: `docs/vertical-slices/<initiative-id>/slice-0001.md`
- Admission status: `READY_FOR_DEV_TEAM`

### Outcome

<Describe the user or business outcome.>

### Mandatory capability-family coverage

| Lifecycle area | Required feature/flow | Status | Evidence |
| --- | --- | --- | --- |

### Status

`SPECIFICATION`

### Repositories and branches

- Root repository/worktree/branch: `<product>-root` / `main`
- Root delivery policy: direct push; no PR
- Root launch-package commit:
- Root final-evidence commit:
- Prototype root path/reference:
- Frontend repository/worktree/branch: `slice/<slice-key>`
- Backend repository/worktree/branch: `slice/<slice-key>`
- Root ignore/isolation verified:

### Contract

- Version: 1
- Status: `DRAFT`
- Document: `docs/dev-team/<task-id>/integration-contract.md`

### Story map

- Document: `docs/dev-team/<delivery-id>/story-map.md`

| Story ID | Observable outcome | Status | Acceptance evidence |
| --- | --- | --- | --- |
| `US-0001` | | `DRAFT` | |

### Required supporting skills

- Lead:
  - `change-management`:
- Frontend:
  - `vercel-react-best-practices`:
  - `supabase` when applicable:
- Backend:
  - `fastapi` when applicable:
  - `supabase` when applicable:
  - `supabase-postgres-best-practices` when applicable:
- Architecture constraints overriding generic skill preferences:

### Frontend engineering task bundle

Assigned stories/tasks:

- `US-0001` / `FE-0001`:

Owned paths across stories:

- `<frontend path>`

Forbidden paths:

- `<backend and EM-owned paths>`

Status: `NOT_STARTED`
Commits:
Story/task evidence:
Supporting-skill evidence:

### Backend engineering task bundle

Assigned stories/tasks:

- `US-0001` / `BE-0001`:

Owned paths across stories:

- `<backend path>`

Forbidden paths:

- `<frontend and EM-owned paths>`

Status: `NOT_STARTED`
Commits:
Story/task evidence:
Supporting-skill evidence:

### Integration and verification

- Contract verification:
- Automated checks:
- End-to-end scenarios:
- Slice → story → task → evidence traceability:
- Locked-change impact and synchronization:
- Regression checks:
- Documentation:
- Supporting-skill compliance:

### Remediation

No remediation recorded.

### Pull requests

- Root repository: no PR; direct `main` commits recorded above
- Frontend PR:
  - URL:
  - Head/merge commit:
  - CI status:
- Backend PR:
  - URL:
  - Head/merge commit:
  - CI status:

### Cross-repository release sequence

- Compatibility strategy:
- Database expand/migrate/switch/contract order:
- PR merge order:
- Deployment order:
- Feature flag and initial state:
- Flag enablement gate:
- Cross-repository rollback:

### Release authority

- Repository maintainer(s):
- Deployment operator:
- Target environment:
- Release approver:

### EM sign-off

- Outcome accepted: No
- Contract satisfied: No
- Tests passed: No
- Documentation complete: No
- Supporting-skill evidence accepted: No
- All mandatory slice flows delivered: No
- Whole-slice E2E passed: No
- Independently releasable/rollbackable: No
- Exactly one FE PR and one BE PR accepted: No
- Root evidence synchronized on `main`: No
- Remaining risks:
- Signed off by EM:
- Completed at:
