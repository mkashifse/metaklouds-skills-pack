# Rapid Prototype Loop

## Input quality

Start when one journey or decision is clear enough to make visible. Do not wait
for a complete initiative. If the assignment is contradictory, return one
recommended clarification instead of guessing.

Select the prototype mode before implementation. Use `DISPOSABLE` unless the
target frontend stack is established and the Product Manager explicitly marks
the round as production-intent. Do not introduce React, Next.js, or another
framework solely to make an exploratory prototype appear reusable.

## Seed strategy

Keep fixtures close to the prototype and easy to understand:

```text
prototype/
├── data/ or fixtures/
│   ├── default.json
│   ├── empty.json
│   ├── failure.json
│   └── permission-denied.json
└── state reset or scenario selector
```

When `localStorage` is used:

- namespace keys by initiative or prototype;
- include a seed/schema version;
- provide one reset action;
- avoid retaining secrets or personal data;
- ensure a stale seed can be replaced predictably.

## Production-intent implementation

When the selected mode is `PRODUCTION_INTENT`:

- match the target frontend's framework and dependency versions;
- follow its design tokens, naming, component, accessibility, and composition
  conventions without importing backend application source;
- isolate fixtures, fake adapters, prototype navigation, and reset controls
  from promotable presentation and interaction files;
- prefer small feature-local files that can be copied to a declared target;
- use `vercel-react-best-practices` for React or Next.js and add
  `vercel-composition-patterns` for reusable component APIs;
- maintain `promotion-handoff.md` from the bundled template.

Production-intent does not authorize real credentials, backend connections,
production auth, migrations, deployment, or automated browser control.

## Promotion classifications

Classify material frontend files before the Human review checkpoint:

- `REUSE_AS_IS`: approved implementation can be copied before integration;
- `HARDEN_THEN_REUSE`: approved implementation must be copied, then completed
  through specifically listed production work;
- `REFERENCE_ONLY`: prototype-only shell, fixture, fake service, reset control,
  shortcut, or intentionally disposable experiment.

Do not label a file reusable merely because it renders correctly. Its target
stack, Truth keys, intended destination, fake boundaries, and known hardening
must be explicit. The production worker may regenerate eligible code only when
reuse is unsafe or incompatible and the exception is recorded with evidence.

## Human review packet

Give the PM Assistant a compact packet to validate and reduce to the Product
Manager's Human-facing brief:

```text
Prototype update:
Decisions demonstrated:
How to start:
Routes to open:
Seeded scenarios:
Reset method:
Questions this round should answer:
Known limitations:
Prototype mode:
Promotion handoff, when applicable:
```

Human observations become `LOCKED`, `TESTING`, or `SUPERSEDED` decisions only
when the Product Manager authorizes them and the PM Assistant records them.
Prototype code never becomes authority.
