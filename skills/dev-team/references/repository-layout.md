# Root with Nested Independent Repositories

Use one root Git repository for canonical product intent, planning, prototype
evidence, delivery control, and cross-repository release evidence. Keep the
frontend and backend Git repositories nested in its working directory for
convenience, but version them independently.

```text
<product>-root/                         # independent Git repository
├── .git/
├── .gitignore
├── CONTEXT.md
├── scrum.md
├── docs/
│   ├── adr/
│   ├── initiatives/<initiative-id>/
│   │   ├── prd.md
│   │   ├── ux-spec.md
│   │   ├── prototype-validation.md
│   │   └── change-management.md
│   ├── vertical-slices/<initiative-id>/
│   │   ├── planning-decisions.md
│   │   ├── vertical-slice-plan.md
│   │   └── slice-0001.md
│   └── dev-team/<delivery-id>/
│       ├── story-map.md
│       ├── stories/US-0001-<slug>.md
│       ├── technical-design.md
│       ├── integration-contract.md
│       ├── test-plan.md
│       └── delivery-report.md
├── prototypes/<initiative-id>/         # React + JSON, non-production
│   ├── src/
│   ├── fixtures/
│   ├── package.json
│   └── README.md
├── <product>-frontend/                 # separate nested Git repository
│   ├── .git/
│   ├── src/
│   ├── tests/
│   └── docs/                           # frontend-local only
└── <product>-backend/                  # separate nested Git repository
    ├── .git/
    ├── src/
    ├── tests/
    ├── migrations/
    ├── openapi.json
    └── docs/                           # backend-local only
```

For WorkApp, use `workapp-root`, `workapp-frontend`, and `workapp-backend`.

## Root isolation

Add exact root-level ignore entries:

```gitignore
/<product>-frontend/
/<product>-backend/
```

Before every root commit, verify:

- both nested directories contain their own `.git`;
- neither directory is tracked by the root repository;
- neither appears as a submodule or gitlink;
- staged root changes contain only canonical documents, prototype files, and
  root-local configuration.

Never use `git add` on a broad parent path without checking the staged file
list. Never force-push root `main`.

## Git and review policy

- Root repository: the active team lead stages, commits, and pushes owned
  canonical documents/prototype changes directly to `main`. Do not create root
  PRs. Restrict root push authority, disallow force-push/deletion, run local
  validation before push, and run post-push CI.
- Frontend repository: use `slice/<slice-key>` and exactly one frontend PR for
  the full fat slice.
- Backend repository: use the same `slice/<slice-key>` and exactly one backend
  PR for the full fat slice.
- Slice key: `<initiative-id>-VS-000N`; use it in branches, PR titles, root
  delivery documents, commits where practical, and test/release evidence.

If a root push is rejected because main advanced, synchronize, re-read
append-only/owned documents, resolve without erasing evidence, revalidate, and
push normally. Do not force.

## Ownership

- Initiative Lead, Planning Lead, and EM own their respective root documents.
  The active lead owns root Git integration for that stage.
- Prototype Engineer edits `prototypes/<initiative-id>/`; the Initiative Lead
  reviews and commits it with the corresponding root documents.
- FE owns product code, UI tests, generated API consumer, and frontend-only
  operating instructions in the frontend repository.
- BE owns services, persistence, migrations, API/provider tests, backend-owned
  OpenAPI, and backend-only operating instructions in the backend repository.

Do not copy canonical PRDs, prototype validation, changes, slices, story maps,
stories, contracts, or delivery reports into code repositories. Link root paths
and root commit SHAs from both PR descriptions.

## Cross-repository release contract

Two PRs cannot merge atomically. Freeze the integration contract in root before
worker launch and choose a compatibility-first sequence:

1. Prefer additive/backward-compatible backend and database changes.
2. Record expand → migrate → switch → contract ordering when schemas change.
3. Record which PR merges/deploys first and why.
4. Use a feature flag when separately deployed components could expose an
   incomplete capability.
5. Keep the flag off until both sides, contract checks, and whole-slice E2E
   evidence pass.
6. Record frontend/backend PR URLs, head and merge SHAs, CI, deployment order,
   root evidence commits, flag state, and rollback evidence.

Merging or deploying one component is integration progress, not a partial
product release. Mark the fat slice `COMPLETE` only after both code PRs and the
full release gate pass.
