# CDM Team Execution Contract v1

Use contract identifier `CDM-TEAM-CONTRACT-v1`.

## Launch envelope

Pass these markers to every team lead and preserve them in worker prompts:

```text
CDM_CONTROLLED=true
CDM_RUN_ID=<unique-run-id>
CDM_INITIATIVE_ID=<initiative-id>
CDM_CONTROL_PATH=<absolute-delivery-control-path>
CDM_TEAM_CONTRACT_PATH=<absolute-path-to-this-file>
CDM_GIT_AUTHORITY=CDM_ONLY
CDM_AUTHORITY_ENVELOPE=<constraints-or-canonical-reference>
CDM_SLICE_KEY=<initiative-id>-VS-000N   # when applicable
```

CDM launches the selected lead directly. The lead owns its normal specialist
workers and must pass the markers unchanged.

## Communication

- Treat CDM as the only user contact.
- Return questions to CDM; never ask the user directly.
- Put one recommendation first and provide concise alternatives.
- Continue autonomously for reversible, in-scope decisions permitted by the
  authority envelope.
- Return `HUMAN_DECISION_REQUIRED` for a human-authority boundary.

## Git authority

Under this contract:

- Teams may edit only their owned artifacts.
- Meta Grill and Vertical Slice workers do not stage or commit root files.
- Dev Team FE and BE may create local commits on assigned slice branches.
- No team member pushes, creates or updates PRs, merges, versions, tags,
  deploys, enables a release flag, or stages/commits/pushes root changes.
- CDM validates and performs every integration and release action.

## Inner loop

Each team must:

1. Load authoritative inputs and the latest checkpoint.
2. Select one bounded unresolved action.
3. Execute through the owning specialist.
4. Observe actual artifact, test, or runtime evidence.
5. Evaluate the stage gate.
6. Update owned artifacts.
7. Repeat only while evidence changes.
8. Return control on pass, upstream defect, human gate, or exhausted retry.

Stop after the same failure appears twice without new evidence or three
remediation cycles fail.

## Allowed statuses

- `PASSED`
- `READY_FOR_CDM_INTEGRATION`
- `REMEDIATION_REQUIRED`
- `RETURN_TO_META_GRILL`
- `RETURN_TO_SLICE_PLANNING`
- `HUMAN_DECISION_REQUIRED`
- `BLOCKED`

Use `PASSED` for Meta Grill and Vertical Slice readiness gates. Use
`READY_FOR_CDM_INTEGRATION` for Dev Team after all local implementation and
verification gates pass. Only CDM may mark a slice or initiative `COMPLETE`.

## Required result

Return one YAML object:

```yaml
contract_version: "CDM-TEAM-CONTRACT-v1"
run_id: "<CDM_RUN_ID>"
team: "meta-grill-team | vertical-slice-team | dev-team"
initiative_id: "<initiative-id>"
slice_key: "<slice-key-or-empty>"
status: "PASSED"
gate: "READY_FOR_SLICE_PLANNING | READY_FOR_DEV_TEAM | READY_FOR_CDM_INTEGRATION"
summary:
  - "<concise outcome>"
artifacts:
  - path: "<absolute-or-root-relative-path>"
    owner: "<team role>"
    validation: "<evidence>"
local_commits:
  root: []
  frontend: []
  backend: []
verification:
  - command_or_check: "<exact check>"
    result: "passed | failed | not-run"
    evidence: "<concise evidence>"
questions:
  - recommendation: "<recommended option>"
    options:
      - "<option and impact>"
risks:
  - "<material risk>"
retry:
  fingerprint: "<stable failure fingerprint or empty>"
  unchanged_observations: 0
  remediation_cycles: 0
recommended_next_action: "<one CDM action>"
```

Use empty lists rather than omitting fields. A pass result must name the exact
gate and include enough evidence for CDM to verify it independently.

## Status rules

### `PASSED`

Return only when the team's complete stage gate passes. Do not launch the next
team.

### `READY_FOR_CDM_INTEGRATION`

Return only when one Dev Team slice has complete local implementation, local
commits, clean ownership, frozen-contract compliance, required automated tests,
and local whole-slice evidence. Include merge/deploy constraints and remaining
external checks.

### `REMEDIATION_REQUIRED`

Name the failed check, expected result, observed result, owner, affected
artifacts, verification to rerun, and failure fingerprint.

### Upstream returns

Use `RETURN_TO_META_GRILL` only for initiative intent, scope, or acceptance
ambiguity. Use `RETURN_TO_SLICE_PLANNING` only for slice completeness,
feasibility, or acceptance defects.

### `HUMAN_DECISION_REQUIRED`

Return one recommendation and two or three options. State which work can
continue and which work must pause.

### `BLOCKED`

Return only after bounded retries or when no safe in-scope action remains.
Include preserved state and the smallest action that could unblock delivery.
