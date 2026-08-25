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
  ├── Performs TRIVIAL work directly
  └── Delegates NON_TRIVIAL work directly to specialists
```

There is no PM Assistant and no mandatory lead hierarchy.

## Why this architecture

The earlier Meta PDS flagship routed every action through several bundled
skills and a PM Assistant. Solo Founder replaces that orchestration chain with:

- one installed proprietary skill;
- a fast, local context restore from two canonical YAML artifacts;
- progressive references loaded only for the current stage;
- direct specialist delegation only for bounded non-trivial work;
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

The smallest executable unit is classified as:

- `TRIVIAL`: PM performs it directly;
- `NON_TRIVIAL`: PM gives the Human a short reason, delegates directly to the
  appropriate specialist, then verifies the evidence.

Specialist work follows:

```text
PM: READY → Specialist: ACTIVE → Specialist: VERIFYING → PM: DONE or REWORK
```

## Production-intent prototypes

Prototypes are frontend foundations, not disposable demonstrations. For
React/Next.js, the Prototype Engineer uses the frontend design and Vercel
support skills to build production-quality pages, navigation, reusable
components, UI states, accessibility, and responsive behavior.

Local seed data lives behind a stable frontend service interface:

```text
Pages and components
→ stable frontend interface
→ local seed adapter now / backend API adapter later
```

Frontend implementation promotes the approved files, replaces the seed adapter,
connects backend APIs and authentication, and performs production hardening. It
does not silently redesign approved UI/UX.

## Canonical product artifacts

Each governed product uses:

```text
docs/solo-founder/
├── canonical-truth.yaml
├── product-ledger.yaml
├── research/
├── slices/
└── reports/
prototypes/
```

- **Canonical Truth** stores current `PROPOSED` and Human-`APPROVED` product
  decisions grouped by Layer.
- **Product Ledger** stores current Mode/Layer, initiatives, Work Packages,
  issues, results, evidence, and lifecycle timestamps.
- Git preserves artifact history; the files contain current state.

The PM and assigned specialists have scoped logical write authority. A
deterministic updater is the Product Ledger's sole physical writer.

## Context persistence

Initialization adds a managed block to the product's `AGENTS.md`. On each
governed interaction, the PM restores its identity and compact context locally:

```bash
python3 ~/.codex/skills/solo-founder/scripts/restore_context.py /absolute/product/root
```

This read does not launch the dashboard, query GitHub, call the network, run a
repository-wide validation, or delegate work.

## Dashboard

The optional local dashboard displays Canonical Truth and Product Ledger state:

```bash
python3 ~/.codex/skills/solo-founder/scripts/serve_dashboard.py /absolute/product/root --ensure
```

It binds to `127.0.0.1` and is read-only except for explicit Human-confirmed
approval of one proposed Truth item. Concurrent changes reject the approval and
require refresh.

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
| `playwright-best-practices` | Upstream | Browser, E2E, visual, and accessibility testing |

Support skills are loaded only for relevant bounded assignments. They never
control Solo Founder Mode, Layers, Truth, Ledger, Slice approval, or Human
authority. The disposable-oriented upstream `prototype` skill is intentionally
not installed.

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
