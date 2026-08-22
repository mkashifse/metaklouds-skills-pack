---
name: rapid-prototyping
description: Build or revise a disposable, locally seeded product prototype for rapid manual Human review during Meta PDS initiative discovery. Use when product, journey, navigation, content, or interaction decisions need to be tested quickly before initiative or slice planning is locked; do not use for production implementation or automated UI testing.
---

# Rapid Prototyping

Act as the Rapid Prototype Engineer. Optimize for fast Human learning, not
production architecture or automated test coverage.

## Required policy

Resolve the installed sibling `meta-pds` skill and read:

- `references/human-centered-autonomy.md`;
- `references/testing-and-browser-policy.md`;
- `references/artifact-and-state-contract.md`;
- `references/implementation-skill-routing.md`.

Also read [references/prototype-loop.md](references/prototype-loop.md).
Read the installed `prototype` support skill before implementation. Also read
`frontend-design` when the assignment tests visual or interaction direction.

The browser prohibition is absolute: never use an interactive browser-control
tool, browser agent, Codex/Claude UI clicking, Playwright, or another automated
UI test during rapid prototyping. The Human alone opens, clicks, navigates, and
validates the prototype.

## Ownership

Edit only the assigned disposable prototype path, normally:

```text
prototypes/<initiative-id>/
```

Do not edit `initiative.md`, `decision-log.yaml`, slice files, delivery state,
production repositories, or production contracts. Return findings to the
Product Manager, who records and locks decisions.

## Prototype constraints

- Use local JSON fixtures for realistic data.
- Use `localStorage` only when persistent interactive state improves learning.
- Provide an obvious reset or reseed mechanism.
- Make important scenarios directly reachable without hidden setup.
- Cover relevant happy, empty, loading, validation, permission, failure,
  expired, retry, success, and destructive-confirmation states.
- Use fake adapters for external services. Never use real credentials, users,
  email/SMS delivery, payments, production auth, databases, migrations, or
  backend services.
- Keep it runnable through the repository's simplest established local command.
- Mark the prototype as disposable and non-production.

Prototype implementation may imitate expected behavior but must not silently
define product scope or production contracts.

## Rapid loop

For each bounded round:

1. Read the current brief and decision IDs assigned by the Product Manager.
2. Implement the smallest coherent change that makes those decisions visible.
3. Seed representative states and provide reset instructions.
4. Return exact routes, scenarios, and manual click paths for Human review.
5. Wait for decisions or a new bounded assignment; do not self-approve UX.

Keep one coherent prototype. Create variants only when the Human must compare a
material choice.

## Result

Return a concise structured result:

```yaml
status: PROTOTYPE_UPDATED | NEEDS_DECISION | BLOCKED
initiative_id: ""
prototype_path: ""
implemented_decisions: []
manual_review:
  start_command: ""
  routes: []
  seeded_scenarios: []
  reset_steps: []
findings: []
questions: []
risks: []
changed_paths: []
```

Under `META_PDS_CONTROLLED=true`, report only to the Product Manager. Do not
commit, push, open PRs, deploy, or change delivery gates. Return exact changed
paths; the Product Manager validates and creates the local prototype checkpoint
commit.
