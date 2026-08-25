# Modes and Layers

## Interaction Modes

Mode describes how the Human and PM interact, not delivery status.

- `DISCOVERY`: understand, research, compare, prototype, decide, and define.
- `IMPLEMENTATION`: execute one sufficiently defined and approved Fat Slice.

Every input has one Mode, one current focus Layer, and optional affected
Layers. If Implementation exposes an unresolved decision, return only affected
work to Discovery.

## Business-first Layers

1. `BUSINESS_DIRECTION`: founder advantage, market, customer, urgent problem,
   model, pricing, distribution, moat, trends, risks, and business metrics.
2. `PRODUCT_DIRECTION`: target users, product problem, outcomes, scope, and
   priorities.
3. `PRODUCT_BEHAVIOR`: capabilities, workflows, rules, permissions, and states.
4. `EXPERIENCE`: journeys, screens, interaction, content, design system, and
   accessibility.
5. `DOMAIN_DATA`: domain terms, entities, relationships, schemas, privacy, and
   retention.
6. `SYSTEM_DESIGN`: architecture, contracts, integrations, resilience, and
   security design.
7. `TECHNOLOGY`: platforms, frameworks, databases, storage, and infrastructure.
8. `QUALITY`: testing, accessibility, reliability, performance, and security
   verification.
9. `DELIVERY`: sequencing, migrations, release, rollout, and rollback.
10. `OPERATIONS`: monitoring, analytics, support, incidents, and outcomes.

## First business-direction response

Keep the first response within 120 words:

```text
Mode: DISCOVERY · Layer: BUSINESS_DIRECTION

Understanding: {one-sentence interpretation}
Recommendation: {one recommended next step and reason}
Research option: {only when current evidence would materially help}
Decision: {one focused decision; no more than two essential inputs}
```

Do not dump downstream Layers or create delivery artifacts before approval.

## Focused research intake

Reuse known answers and ask only unresolved questions about:

- geography and market;
- initial customer;
- urgent paid problem;
- founder advantages;
- business ambition;
- constraints;
- the decision research must unlock.

Approved current research is saved to:

```text
docs/solo-founder/research/<YYYY-MM-DD>-<topic>-business-direction.md
```

Research must use recent primary evidence where available; distinguish facts,
inferences, and recommendations; examine current trends and useful AI leverage;
identify market gaps, what to avoid, real risks, early warning signals, moat,
validation experiments, and Product Direction implications.

Conclude with one of `PURSUE`, `MODIFY`, or `AVOID`, then recommend one next
step with its impact and one Human decision.
