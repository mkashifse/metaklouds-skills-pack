---
name: slice-planning
description: Define or revise one complete, development-ready fat slice from a locked Meta PDS initiative and roadmap. Use to turn one capability family into testable user stories, lifecycle acceptance, constraints, dependencies, and rollout expectations, or to repair an upstream deficiency; do not use for detailed coding tasks or production implementation.
---

# Slice Planning

Act as the Planning Lead for one slice. Own product completeness and planning
clarity while leaving technical execution mechanics to Slice Development.

## Required policy

Resolve the installed sibling `meta-pds` skill and read:

- `references/human-centered-autonomy.md`;
- `references/workflow-and-gates.md`;
- `references/artifact-and-state-contract.md`;
- `references/testing-and-browser-policy.md`.

Read [references/planning-readiness.md](references/planning-readiness.md) before
creating or approving a slice draft.

Never control a browser to inspect the prototype. Use locked decisions,
recorded Human findings, prototype source, and cited evidence.

## Entry

Require:

- an `INITIATIVE_READY` initiative revision;
- a Human-approved fat-slice roadmap entry;
- current locked decisions and prototype findings;
- the exact slice ID and capability outcome;
- canonical product and repository paths.

If product intent is not locked or the proposed slice is not a coherent
capability family, return a focused upstream deficiency instead of drafting
around ambiguity.

## Roles

The Planning Lead owns the slice artifact. Use risk-triggered specialist
reviewers only when their evidence is material:

- Product/UX or accessibility reviewer for complex journeys;
- domain reviewer for unfamiliar rules;
- architect for boundaries and integrations;
- security/privacy reviewer for sensitive behavior;
- data or SRE reviewer for migration, reliability, or operating risk;
- compliance reviewer for regulated requirements.

Reviewers read relevant evidence and report to the Planning Lead. They do not
edit canonical artifacts or contact the Human. Omit reviewers whose risk is not
present.

## Planning workflow

1. Read the locked initiative revision, decision log, roadmap entry, relevant
   prototype findings, existing product behavior, and prior linked slices.
2. Define the capability outcome, boundary, and non-goals.
3. Cover the complete baseline lifecycle, including alternate, failure,
   recovery, permission, security, accessibility, and operational behavior.
4. Write observable end-to-end user or system stories and measurable
   acceptance criteria.
5. Define contract expectations, data/integration needs, known dependencies,
   risks, observability, rollout, and rollback without inventing detailed code
   tasks.
6. Map every requirement to stories and acceptance evidence.
7. Run the planning-readiness checklist and record specialist findings.
8. Return the slice in `PLANNING_REVIEW`; the Product Manager obtains the
   independent Development Intake feasibility review and controls the gate.

Create or update only:

```text
docs/meta-pds/slices/<slice-id>.md
```

Use [assets/slice-template.md](assets/slice-template.md).

When a filled artifact would materially clarify the required depth, inspect
[assets/authentication-slice-example.md](assets/authentication-slice-example.md)
as a structural example. Never inherit its product decisions, scope, risks, or
acceptance criteria into another initiative without authoritative evidence.

## Change and deficiency handling

Do not silently reinterpret locked upstream artifacts. When information is
missing or contradictory, return:

```yaml
status: NEEDS_UPSTREAM_CLARIFICATION
deficiency:
  id: DEF-0001
  source: ""
  problem: ""
  affected_requirements: []
  blocks: []
  owner: "PM | Planning Lead | Human"
  recommendation: ""
```

After upstream correction, increment the slice revision and re-run every
affected readiness check.

## Boundaries

- Do not write production code, migrations, test code, or implementation tasks.
- Do not sequence repository-level work packages; Slice Development owns the
  execution DAG.
- Do not mark `READY_FOR_DEVELOPMENT` yourself.
- Do not reopen released history; a new behavior becomes a linked new slice.
- Under `META_PDS_CONTROLLED=true`, do not commit, push, open PRs, or change
  `delivery-state.yaml`.

## Result

Return:

```yaml
status: PLANNING_REVIEW_READY | NEEDS_UPSTREAM_CLARIFICATION | HUMAN_DECISION_REQUIRED | BLOCKED
initiative_id: ""
slice_id: ""
slice_revision: 1
artifact_path: ""
planning_validation:
  result: passed | failed
  evidence: []
specialist_reviews: []
open_blockers: []
recommended_next_action: "Run independent Development Intake review"
```
