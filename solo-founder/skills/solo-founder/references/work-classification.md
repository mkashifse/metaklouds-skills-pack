# Work Classification and Delegation

Classification depends on expertise, uncertainty, risk, and scope—not minutes.
Classify the smallest executable unit. Split mixed Work Packages.

| Layer | PM handles directly when trivial | Delegate when non-trivial | Default specialists |
| --- | --- | --- | --- |
| `BUSINESS_DIRECTION` | Quick trends, competitors, pricing, synthesis, recommendations | Financial modelling, legal/regulatory analysis, rigorous market validation | Finance, Market Research, Legal/Compliance |
| `PRODUCT_DIRECTION` | Users, problem, outcomes, scope, priorities, roadmap | Regulated-domain validation, advanced analytics, safety-critical strategy | Domain Expert, Product/Data Analyst |
| `PRODUCT_BEHAVIOR` | Capabilities, workflows, rules, permissions, ordinary edge cases | Algorithms, rule engines, complex state, experimental behavior | Prototype, Backend, Domain Expert |
| `EXPERIENCE` | Journeys, screen structure, content, simple wireframes, design proposal | Production prototype, complex UI, motion, formal accessibility | Prototype, Frontend, UX/Accessibility |
| `DOMAIN_DATA` | Terminology, conceptual entities, fields, relationships | Schemas, migrations, pipelines, privacy, retention, integrity | Backend, Data, Security |
| `SYSTEM_DESIGN` | Components, constraints, straightforward integrations | Distributed architecture, contracts, concurrency, scale, security | Backend, Platform, Security |
| `TECHNOLOGY` | Current documentation, versions, familiar comparisons | Benchmarks, spikes, infrastructure/database experiments | Frontend, Backend, Platform |
| `QUALITY` | Acceptance, scenarios, checklists, evidence inspection | Automated, integration, performance, security, accessibility QA | QA, Security, Frontend, Backend |
| `DELIVERY` | Slices, sequencing, priorities, dependencies, release plan | CI/CD, deployments, migrations, rollback, release execution | Platform, Backend, QA |
| `OPERATIONS` | Metrics, alerts, support process, evidence review | Observability, incidents, recovery automation, tuning | Platform/SRE, Backend, Security, Data |

## Work structures

- The PM owns final User Stories and Fat Slices. Specialists investigate
  bounded uncertainty but cannot redefine or approve them.
- The Work Package is the normal delegation boundary and is exactly `TRIVIAL`
  or `NON_TRIVIAL`.
- The PM owns canonical research and product documentation. Specialists own
  code-coupled documentation and return evidence for deep technical findings.
- A simple text flow or design suggestion may be trivial; runnable prototype
  implementation is non-trivial.
- Production frontend, backend, database, infrastructure, security, automated
  testing, deployment, and incident work is normally non-trivial.

## Transparent updates

Before delegation:

```text
I am delegating this task because it is non-trivial: {reason}.
Assigned to: {role}. It may take a while.
I will verify the result against: {expected outcome}.
```

Meaningful later updates:

```text
The {role} is still working on this. No decision is needed from you right now.
The specialist has finished. I am verifying the result against the acceptance criteria.
Verified and completed. The result meets the acceptance criteria.
The specialist found a blocker: {explanation}. I need your decision on {decision}.
```

Do not expose worker chatter or emit repetitive status messages.
