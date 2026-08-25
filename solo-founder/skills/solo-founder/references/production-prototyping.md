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

The Prototype Engineer builds:

- production-quality pages, routes, navigation, components, and interactions;
- responsive behavior and the approved design system;
- loading, empty, error, success, disabled, and permission states;
- accessible semantics, keyboard interaction, focus, and contrast;
- realistic local seed data behind one stable data/service interface;
- a local adapter implementing that interface;
- a promotion handoff mapping reusable sources to frontend targets.

Components must not import scattered seed records directly:

```text
Pages and components
→ stable frontend interface
→ local seed adapter now / backend API adapter later
```

During prototyping, report consequential findings to the PM. The PM records
them as `PROPOSED` Truth. Prototype behavior is evidence, never authority.

## Promotion boundary

Frontend implementation promotes or moves exact approved files. It replaces
the seed adapter, connects backend APIs and authentication, adds production
configuration and telemetry, and performs hardening and tests. It does not
rebuild navigation, pages, components, or approved UI/UX.

A backend constraint requiring a UI or behavior change is drift. Record it and
return the affected decision to the PM and Human; never silently redesign.
