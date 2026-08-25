# Production-Intent Prototyping

Solo Founder prototypes are production-intent frontend foundations by default.
A disposable prototype requires explicit Human approval for a bounded
experiment.

## Entry gate

Require enough stable Business Direction, Product Direction, Product Behavior,
and Experience to define what the prototype must validate. Also require:

- a Human-approved minimum design direction;
- an established frontend stack;
- a minimum frontend data/service interface;
- no unresolved decision that makes the result predictably disposable.

If no design system exists, the PM asks only:

```text
1. Do you have brand or design-system assets we must use?
2. If not, what visual character and light/dark preference should guide the product?
```

The PM proposes palette roles, typography, spacing, radius, elevation,
components, responsive behavior, accessibility baseline, and optionally one
lightweight reference image. Record Human approval as `EXPERIENCE` Truth.

## Engineering contract

For React/Next.js, use `frontend-design`, `vercel-react-best-practices`, and
`vercel-composition-patterns` when reusable component boundaries exist.

The PM builds directly by default. An optional Prototype Engineer may build a
bounded part in parallel only when the criteria in
[work-classification.md](work-classification.md) are satisfied. The executor
builds:

- production-quality pages, routes, navigation, components, and interactions;
- responsive behavior and the approved design system;
- loading, empty, error, success, disabled, and permission states;
- accessible semantics, keyboard interaction, focus, and contrast;
- realistic local seed data behind one stable data/service interface;
- a local adapter implementing that interface;
- a promotion map from reusable sources to frontend targets.

Place web prototype sources in `prototypes/frontend/` and mobile prototype
sources in `prototypes/mobile/`. Promotion targets `apps/frontend/` or
`apps/mobile/`; shared approved components may move to `packages/ui/`, and
stable service/API contracts belong in `packages/contracts/`.

Components must not import scattered seed records directly:

```text
Pages and components
→ stable frontend interface
→ local seed adapter now / backend API adapter later
```

During prototyping, report consequential findings to the PM. The PM records
them as `PROPOSED` Truth. Prototype behavior is evidence, never authority.
Delegated prototype work must return a `PROTOTYPE` handoff before
`VERIFYING`; the PM consumes it during prototype review.

## Browser-control restriction during prototyping

Do not use interactive agent or in-app browser control to review a prototype by
default. Do not manually tour routes, click through screens, repeatedly inspect
page state, or capture screenshots. The production-intent nature of the
prototype does not justify this token cost. Only an explicit Human instruction
in the current request authorizes interactive browser control.

Verify through code inspection, type checking, linting, unit/component tests,
and bounded automated Playwright tests with concise text output. Automated
visual-regression comparison may run without opening its images in the agent.
Do not capture or inspect screenshots, videos, or traces unless explicitly
requested. Give the Human the local URL or runnable build when subjective visual
review remains necessary.

## Promotion boundary

The PM promotes or moves the exact approved files end-to-end by default. A
Full-Stack Engineer may own a bounded promotion Work Package only for justified
parallel execution. The executor replaces the seed adapter, connects backend
APIs and authentication, makes any required database/backend/contract change,
adds production configuration and telemetry, and performs hardening and tests.
The executor does not rebuild navigation, pages, components, or approved UI/UX.

Record the source-to-target map and remaining adapter work as implementation
evidence. When promotion is delegated, include both in its `IMPLEMENTATION`
handoff before `VERIFYING`.

A backend constraint requiring a UI or behavior change is drift. Record it and
return the affected decision to the PM and Human; never silently redesign.
