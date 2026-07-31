# Multi-Repository Layout

Use one canonical coordination/product repository as the durable source of
product intent, planning, delivery control, and cross-repository evidence.

```text
product-coordination/                    # e.g. workapp
├── CONTEXT.md
├── scrum.md
└── docs/
    ├── adr/
    ├── initiatives/<initiative-id>/
    │   ├── prd.md
    │   ├── ux-spec.md
    │   ├── prototype-validation.md
    │   └── change-management.md
    ├── vertical-slices/<initiative-id>/
    │   ├── planning-decisions.md
    │   ├── vertical-slice-plan.md
    │   └── slice-0001.md
    └── dev-team/<delivery-id>/
        ├── story-map.md
        ├── stories/US-0001-<slug>.md
        ├── technical-design.md
        ├── integration-contract.md
        ├── test-plan.md
        └── delivery-report.md

product-prototypes/
└── <initiative-id>/                  # throwaway React + JSON prototype
    ├── src/
    ├── fixtures/
    ├── package.json
    └── README.md                     # one-command run and non-production warning

product-frontend/
├── src/
├── tests/
├── package.json
├── generated API client
└── docs/                              # frontend-local architecture/runbooks only

product-backend/
├── src/
├── tests/
├── migrations/
├── openapi.json                       # backend-owned contract artifact
└── docs/                              # backend-local architecture/runbooks only
```

## Ownership

- Coordination repository: Initiative Lead, Planning Lead, and EM own their
  respective canonical documents. It contains cross-repository commit/PR/CI and
  release evidence.
- Prototype repository: Meta-team Prototype Engineer owns throwaway React code,
  JSON fixtures, and local run instructions. It is behavioral evidence, not
  production architecture or a production-code source.
- Frontend repository: FE owns product code, UI tests, generated API consumer,
  and frontend-only operating instructions.
- Backend repository: BE owns services, persistence, migrations, API/provider
  tests, backend-owned OpenAPI, and backend-only operating instructions.

Do not copy the PRD, prototype validation, change log, slice, story map, stories,
contract, or delivery report into frontend/backend repositories. Link to
canonical paths from worker prompts and PR descriptions. Create one PR per
changed production/coordination repository and record all PRs in the canonical
`scrum.md` and `delivery-report.md`.
