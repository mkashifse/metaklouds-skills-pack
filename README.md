# Solo Founder Skills Pack

Solo Founder is a business-first AI product operating system for a founder
building without a conventional product-delivery team.

`solo-founder` is the single proprietary flagship skill and the Human's only
product contact. Its persistent AI Product Manager guides the founder from
business direction through product definition, a production-intent frontend
prototype, approved Fat Slices, implementation, QA, release, and outcome
validation.

```text
Founder
  ↓
Solo Founder Product Manager
  ├── Performs all bounded work directly by default
  ├── May delegate prototype work for parallel speed
  └── May delegate full-stack work for parallel speed
```

There is no PM Assistant, frontend/backend role split, or mandatory lead
hierarchy. Prototype and Full-Stack Engineers are optional parallel capacity,
not mandatory routing stages.

## Why this architecture

The earlier Meta PDS flagship routed every action through several bundled
skills and a PM Assistant. Solo Founder replaces that orchestration chain with:

- one installed proprietary skill;
- a fast, local context restore from two canonical YAML artifacts;
- progressive references loaded only for the current stage;
- only two optional executor roles, loaded only when parallelism will save time;
- the PM remains context-aware before and after direct implementation;
- every delegated result returns through one typed, verifiable handoff;
- conditional upstream implementation skills;
- an optional local dashboard rather than a per-message runtime dependency.

## Product journey

```text
BUSINESS_DIRECTION
→ PRODUCT_DIRECTION
→ PRODUCT_BEHAVIOR
→ EXPERIENCE and approved minimum design system
→ production-intent frontend prototype
→ proposed and approved prototype Truth
→ proposed Fat Slice
→ Human-approved Fat Slice
→ Development Intake
→ IMPLEMENTATION
→ QA, release, and outcome validation
```

No development starts for an unapproved Fat Slice. Approval is per Slice, so
later Slices may remain in Discovery while one approved ready Slice executes.

## Modes, Layers, and work classification

Solo Founder has two Human–PM interaction Modes:

- `DISCOVERY`: research, clarify, compare, prototype, decide, and define;
- `IMPLEMENTATION`: execute a sufficiently defined, Human-approved Fat Slice.

The PM selects one current focus Layer from:

```text
BUSINESS_DIRECTION, PRODUCT_DIRECTION, PRODUCT_BEHAVIOR, EXPERIENCE,
DOMAIN_DATA, SYSTEM_DESIGN, TECHNOLOGY, QUALITY, DELIVERY, OPERATIONS
```

The smallest executable unit is classified independently from assignment:

- `TRIVIAL`: bounded, reversible, and low-risk. The PM performs it directly by
  default, including code.
- `NON_TRIVIAL`: substantial uncertainty, experimentation, architecture,
  integration, risk, or production impact. The PM still performs it directly
  unless parallel delegation has a clear net speed benefit.

Exactly two optional executor roles exist:

- `PROTOTYPE_ENGINEER` for production-intent prototype implementation;
- `FULL_STACK_ENGINEER` for database, backend, contracts, frontend/mobile,
  tests, infrastructure, release, and operations.

`FRONTEND`, `BACKEND`, and `FULL_STACK` are temporary assignment focuses, not
roles. A small field change crossing a table, API, and UI goes to one
executor—normally the PM. Engineers are used only when bounded packages can run
independently and the time saved exceeds coordination cost.

Engineer work follows:

```text
PM: READY → Engineer: ACTIVE → Engineer: VERIFYING → PM: DONE or REWORK
```

Before `VERIFYING`, a delegated engineer must complete the Work Package's typed
handoff. The PM consumes it before `DONE` or `REWORK`.

## Production-intent prototypes

Prototypes are frontend foundations, not disposable demonstrations. For
React/Next.js, the PM—or an optional parallel Prototype Engineer—uses the
frontend design and Vercel support skills to build production-quality pages,
navigation, reusable components, UI states, accessibility, and responsive
behavior.

Local seed data lives behind a stable frontend service interface:

```text
Pages and components
→ stable frontend interface
→ local seed adapter now / backend API adapter later
```

The PM promotes the approved files by default, replaces the seed adapter,
connects database/backend/API/authentication changes, and performs production
hardening end-to-end. A Full-Stack Engineer may take a bounded promotion package
only for justified parallelism and may not silently redesign approved UI/UX.

## Canonical product artifacts

Each governed product uses:

```text
docs/solo-founder/
├── canonical-truth.yaml
├── product-ledger.yaml
├── research/
├── slices/
├── reports/
├── architecture/
└── handoffs/
    ├── research/
    ├── documentation/
    ├── prototype/
    ├── implementation/
    ├── verification/
    └── exception/
prototypes/
├── frontend/
└── mobile/
apps/
├── frontend/
├── mobile/
└── backend/
packages/
├── contracts/
├── domain/
├── ui/
├── shared/
└── config/
infrastructure/
tests/
├── e2e/
└── integration/
```

- **Canonical Truth** stores current `PROPOSED` and Human-`APPROVED` product
  decisions grouped by Layer.
- **Product Ledger** stores current Mode/Layer, initiatives, Work Packages,
  issues, results, evidence, delegation, handoff consumption, and lifecycle
  timestamps.
- **Issue Sidecar** batches safe auto-resolutions, passive open issues, and
  Human-required decisions into one exit-sweep Ledger write so only affected
  scope pauses and unrelated delivery continues.
- **Typed handoffs** return delegated research, documentation, prototype,
  implementation, verification, or exception evidence to the PM. Direct PM
  work does not create them.
- Git preserves artifact history; the files contain current state.

The initializer creates this structure additively without overwriting existing
content. It preserves empty leaf directories with `.gitkeep`, but does not
choose frameworks or generate stack-specific boilerplate until the relevant
Technology and System Design Truth is approved.

The PM owns product authority and the complete Ledger. Assigned Prototype or
Full-Stack Engineers have scoped write authority only for their Work Package
execution fields and typed handoff. A deterministic updater is the Product
Ledger's sole physical writer.

## Context persistence

Initialization adds a managed block to the product's `AGENTS.md`. On each
governed interaction, the PM restores its identity and compact context locally:

```bash
python3 ~/.codex/skills/solo-founder/scripts/restore_context.py /absolute/product/root
```

This read does not launch the dashboard, query GitHub, call the network, run a
repository-wide validation, or delegate work.

## Dashboard

The optional local dashboard reuses the compact Meta PDS dark cockpit design
while projecting only current Solo Founder data:

```bash
python3 ~/.codex/skills/solo-founder/scripts/serve_dashboard.py /absolute/product/root --ensure
```

It binds to `127.0.0.1` and is read-only except for explicit Human-confirmed
approval of one proposed Truth item. Concurrent changes reject the approval and
require refresh. Its four views are Truth, Slices, Work, and Issues; a compact
context strip keeps Mode, Layer, initiative, and next action visible. Selecting
a Slice opens its full User Stories, acceptance, Test Cases, and related Work
Packages in the restored Meta PDS detail modal.
Opening the bundled `index.html` directly shows a labelled, read-only gym and
diet product demo; the managed server always projects repository artifacts.

## Proprietary and upstream skills

The complete profile installs 11 skills:

| Skill | Ownership | Purpose |
| --- | --- | --- |
| `solo-founder` | Metaklouds | Business-first PM workflow, Truth, Ledger, prototyping, Fat Slices, dashboard, and gates |
| `frontend-design` | Upstream | Production interface design |
| `vercel-react-best-practices` | Upstream | React and Next.js implementation |
| `vercel-composition-patterns` | Upstream | Reusable React composition |
| `fastapi` | Upstream | FastAPI and Pydantic implementation |
| `nodejs-backend-patterns` | Upstream | Node.js and TypeScript backends |
| `supabase` | Upstream | Supabase implementation and security |
| `supabase-postgres-best-practices` | Upstream | Postgres schema, migration, RLS, and performance |
| `python-testing-patterns` | Upstream | Python testing |
| `vitest` | Upstream | TypeScript and frontend testing |
| `playwright-best-practices` | Upstream | Automated browser, E2E, visual, and accessibility testing |

Support skills are loaded only for relevant bounded assignments. They never
control Solo Founder Mode, Layers, Truth, Ledger, Slice approval, or Human
authority. The disposable-oriented upstream `prototype` skill is intentionally
not installed.

During prototyping and frontend/mobile development, Solo Founder prohibits
interactive agent browser control, repeated clicking, page inspection, and
screenshots unless the Human explicitly requests them. Compact CLI-driven
automated tests remain available without feeding browser imagery through the
agent.

See [THIRD_PARTY.md](THIRD_PARTY.md) for pinned sources and license status.

## Install

```bash
git clone https://github.com/mkashifse/metaklouds-skills-pack.git
cd metaklouds-skills-pack
./scripts/install.sh codex
```

Force a migration from an earlier pack:

```bash
./scripts/install.sh codex --force --only solo-founder
```

The installer backs up and retires installed `meta-pds`,
`rapid-prototyping`, `slice-planning`, `slice-development`, and `slice-qa`
directories when installing the complete Solo Founder profile.

Start a new Codex task after installation, then invoke:

```text
Use $solo-founder to start or resume this product.
```

For Claude Code:

```bash
./scripts/install.sh claude
```

## Validate and test

Validate the skill package:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py solo-founder/skills/solo-founder
```

Run the dependency-free behavior tests:

```bash
python3 solo-founder/skills/solo-founder/scripts/test_solo_founder.py
```

Test installation into an isolated destination:

```bash
./scripts/install.sh codex --dest /absolute/temp/skills --only solo-founder
```

## Repository structure

```text
.
├── README.md
├── THIRD_PARTY.md
├── manifest.json
├── scripts/install.sh
├── solo-founder-planning.md
└── solo-founder/
    ├── manifest.json
    ├── scripts/install.sh
    └── skills/solo-founder/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/
        ├── scripts/
        └── assets/
```

## License

Metaklouds-owned files are available under [LICENSE](LICENSE). Upstream skills
remain governed by their respective licenses and repositories.
