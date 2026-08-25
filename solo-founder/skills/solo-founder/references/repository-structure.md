# Product Repository Structure

Use one implementation-ready structure across Solo Founder products:

```text
.
├── AGENTS.md
├── docs/solo-founder/
│   ├── canonical-truth.yaml
│   ├── product-ledger.yaml
│   ├── research/
│   ├── slices/
│   ├── reports/
│   ├── architecture/
│   └── handoffs/
├── prototypes/
│   ├── frontend/
│   └── mobile/
├── apps/
│   ├── frontend/
│   ├── mobile/
│   └── backend/
├── packages/
│   ├── contracts/
│   ├── domain/
│   ├── ui/
│   ├── shared/
│   └── config/
├── infrastructure/
└── tests/
    ├── e2e/
    └── integration/
```

## Boundaries

- `docs/solo-founder/` contains governed product evidence and decisions.
- `prototypes/` contains production-intent interfaces using local seed adapters.
- `apps/` contains deployable product surfaces and services.
- `packages/contracts/` contains API, event, and frontend service contracts.
- `packages/domain/` contains shared domain language and rules when reuse is
  justified.
- `packages/ui/` contains promoted reusable design-system components.
- `packages/shared/` contains genuinely cross-application utilities, not a
  dumping ground.
- `packages/config/` contains shared build, lint, type, and tooling settings.
- `infrastructure/` contains deployment, database, environment, and
  observability configuration.
- `tests/` contains cross-application verification; unit tests remain beside
  their owning code when the selected stack supports that convention.

The initializer creates the structure additively and never replaces existing
content. Empty leaf directories receive `.gitkeep` so Git can preserve the
shape. Do not generate framework boilerplate, select a monorepo tool, or move
existing code until the relevant `TECHNOLOGY` and `SYSTEM_DESIGN` Truth is
approved.

## Promotion

Prototype work starts in `prototypes/frontend/` or `prototypes/mobile/`.
Promotion moves or copies approved sources into the matching `apps/` surface,
extracts justified reusable UI into `packages/ui/`, preserves navigation and
behavior, replaces the seed adapter with the production adapter, and records a
handoff in `docs/solo-founder/handoffs/`.

Folders for product surfaces that do not apply may remain empty. Remove them
only with Human approval after Product Direction establishes that they are out
of scope.
