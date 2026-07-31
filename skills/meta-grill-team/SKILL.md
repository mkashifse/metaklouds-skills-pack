---
name: meta-grill-team
description: Four-person initiative-definition and React-prototyping team that grills an idea in decision rounds while building a frontend-only JSON-backed prototype, then produces a durable PRD, UX specification, prototype validation, glossary updates, ADRs, and change history. Use before vertical-slice planning when product, business, UX, navigation, and interaction decisions need to be explored and locked together.
---

# Meta Grill Team

Turn an idea into an approved initiative definition while using a throwaway
React prototype to test product and UX decisions. This team does not create
vertical slices or production code.

## Team

Use exactly four roles:

- Initiative Lead / Principal Product Manager (lead)
- Product and UX Designer
- Principal Architect and SRE
- Frontend React Prototype Engineer

The lead owns the user conversation, the PRD's decision ledger, artifacts, and
final approval. The lead is the only editor of the PRD, UX specification,
prototype validation, context terms, and initiative ADRs. The append-only
`change-management.md` is the explicit exception: the active team's lead may
append and lock records under `$change-management`. The Product/UX Designer
owns content review/sign-off for journeys, domain behavior, interaction states,
accessibility, and terminology. The Architect/SRE owns content review/sign-off
for system boundaries, data, security, reliability, rollout, and operational
constraints. The Prototype Engineer edits only the throwaway React prototype
and owns JSON fixtures, navigation, representative states, and prototype run
evidence.

## Entry modes

### Coordinator mode

When no `META_GRILL_ROLE` marker is present:

1. Confirm subagent tools are available.
2. Spawn exactly one lead with `META_GRILL_ROLE=LEAD`.
3. Include the initiative, canonical root repository, root prototype path,
   nested production repository paths, constraints, and this skill path.
4. Instruct the lead to read this file and own the other three workers.
5. Do not spawn the designer, architect, or prototype engineer directly.

### Lead mode

When `META_GRILL_ROLE=LEAD` is present:

1. Inspect the repository, `CONTEXT-MAP.md`, `CONTEXT.md`, existing PRDs,
   `docs/adr/`, `docs/initiatives/<initiative-id>/change-management.md`,
   architecture, existing prototype, and relevant product behavior.
2. Resolve and read `$change-management`. Ensure the initiative change log
   exists before locking runtime changes.
3. Spawn exactly one Product/UX Designer, one Architect/SRE, and one Frontend
   React Prototype Engineer as direct subagents.
4. Run the round/prototype workflow below.
5. Resolve contradictions and secure explicit user approval where required.
6. Produce the deliverables and set the initiative `READY_FOR_SLICE_PLANNING`.

Only the Prototype Engineer may write code, and only in the isolated prototype
workspace. Other workers inspect and advise. No worker writes production code.
If concurrency is limited, keep the Prototype Engineer active while consulting
the Designer and Architect sequentially.

For multi-repository products, use a root repository such as `<product>-root`.
Keep canonical documents and prototype code in that repository. Keep the
independent `<product>-frontend` and `<product>-backend` Git repositories nested
inside the root working directory for convenient access, but ignore their exact
directories from the root repository. Never add them as submodules, gitlinks,
or ordinary root-repository files.

Place prototype code inside the root repository:

```text
<product>-root/prototypes/<initiative-id>/
```

The prototype is committed with initiative documents to root `main`; it is not
a separate repository. The Prototype Engineer edits only the prototype, while
the Initiative Lead owns root staging, commits, and direct pushes. Do not create
a root PR. Before staging, verify the nested frontend/backend directories are
ignored and absent from the root index. Never force-push root `main`.

Reuse a user-provided root prototype path when present. Inspect production
frontend/backend repositories as read-only sources and never duplicate the PRD
or UX specification into them. Do not modify production code during meta-grill
unless the user explicitly authorizes a different workflow.

## Round workflow

Ask questions in batches, not one at a time. Each round contains the most
consequential open questions, normally 5–10, and a decisive recommended answer
for each. Never ask for facts already available in the repository.

Run the domains in this order:

1. Product brief: problem, users, current alternative, value, success,
   boundaries, non-goals.
2. Product and domain design: capability model, journeys, lifecycle, alternate
   and recovery flows, terminology, business rules.
3. UX: information architecture, interaction states, accessibility,
   responsive behavior, and content.
4. Architecture: boundaries, data ownership, contracts, integrations,
   security, privacy, and failure modes.
5. Operations: deployment, observability, rollback, resilience, cost, and
   support.

Use at least one round per domain and add another only when material decisions
remain. Present a progress table at the start of each round. The user can accept
all recommendations or override named questions. Push back once on a dangerous
or contradictory override, then respect the user's decision.

After each accepted round, update the `Decision ledger` section of `prd.md` and
the relevant deliverables before continuing. If new evidence contradicts a
locked decision, `$change-management` takes precedence: identify the dependency,
classify lead versus human authority, lock the result, run the impact analysis,
and synchronize affected artifacts.

Evaluate accepted decisions for ADR eligibility after every round, not only
during the architecture round. Keep ordinary product, business, UX,
architecture, and operational decisions in the PRD decision ledger. Create an
ADR only when the stricter qualification test under Deliverables is satisfied.

## Concurrent prototype workflow

Start the Prototype Engineer after the first product/domain decisions are
stable enough to create a useful flow. Require the engineer to:

- read the `prototype` and `vercel-react-best-practices` skills before coding;
- build a throwaway React frontend with JSON/in-memory fixtures only;
- cover navigation and representative happy, loading, empty, validation,
  permission, failure, retry/expiry, success, and destructive states;
- use realistic sample data and expose state transitions visibly;
- remain runnable with one command and clearly marked non-production;
- avoid backend services, production auth, databases, migrations, real secrets,
  and external integrations.

The prototype and grilling run as a feedback loop:

1. Lock a product/UX decision.
2. Reflect it in the prototype and durable documents.
3. Review the runnable flow with the user.
4. Feed prototype findings into the next decision round.
5. Reconcile prototype and documents before readiness.

Use the generic `prototype` skill's throwaway, no-persistence, one-command
principles. For this workflow, prefer one coherent navigable product prototype;
create multiple variants only when a decision genuinely needs comparison.

Prototype code is evidence, not a production architecture, API contract, or
implementation starting point. Preserve validated findings in
`prototype-validation.md`; downstream teams may inspect the code but must not
copy it blindly.

Normal round decisions go in the PRD decision ledger. When new evidence
contradicts an already locked decision or creates cross-team misalignment, use
`$change-management`: let the lead lock contained/reversible decisions and
inform the user, but obtain human approval for severe changes. Always record the
post-lock quick impact analysis.

## Deliverables

Create:

```text
docs/initiatives/<initiative-id>/prd.md
docs/initiatives/<initiative-id>/ux-spec.md
docs/initiatives/<initiative-id>/prototype-validation.md
docs/initiatives/<initiative-id>/change-management.md
prototypes/<initiative-id>/                      # React + JSON prototype
CONTEXT.md                                        # glossary terms only
docs/adr/NNNN-<slug>.md                           # qualifying decisions only
```

Use [assets/prd-template.md](assets/prd-template.md) and
[assets/ux-spec-template.md](assets/ux-spec-template.md). Use
[assets/prototype-validation-template.md](assets/prototype-validation-template.md)
for the prototype handoff. Create `change-management.md` from the
`$change-management` template.

- The PRD is mandatory and is the initiative contract.
- The UX specification and prototype validation are mandatory for this
  user-facing prototype workflow.
- `CONTEXT.md` contains stable domain language, not implementation detail.
- Evaluate ADR eligibility in every decision round. Create one ADR file per
  qualifying decision only when it is hard to reverse, surprising without
  context, and the result of a real trade-off. Do not use a combined
  architecture-decisions document or duplicate ordinary PRD ledger entries as
  ADRs. Cross-reference the PRD decision when both records are useful. Follow
  [references/ADR-FORMAT.md](references/ADR-FORMAT.md).
- Follow `CONTEXT-MAP.md` in multi-context repositories and
  [references/CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md).
- Do not create a separate BRD. Put business context, value, constraints, and
  measurable outcomes in the PRD.

## Readiness gate

Set `READY_FOR_SLICE_PLANNING` only when:

- the problem, target users, value, success measures, scope, and non-goals are
  explicit;
- primary, alternate, recovery, permission, and failure journeys are defined;
- product terminology and business rules are unambiguous;
- UX states and accessibility are covered when applicable;
- architecture, security, privacy, data, operations, rollout, and rollback
  constraints are documented;
- material open questions are resolved or named as explicit planning gates;
- prototype navigation, fixtures, and representative state coverage match the
  PRD and UX specification;
- prototype findings, limitations, discarded alternatives, and unresolved
  risks are captured durably;
- every locked runtime change has an impact analysis and synchronized artifact
  owners;
- every change affecting initiative documents is fully synchronized; a
  temporary change-record overlay cannot cross this readiness gate;
- root documents and prototype are committed and pushed directly to root
  `main`, with no root PR and no nested code-repository content tracked;
- the user approves the initiative definition.

The handoff is the PRD, UX specification, prototype validation, prototype
root path/commit, change history, context terms, and ADRs. Recommend
`$vertical-slice-team` next. Do not create slice files, user stories,
engineering tasks, production branches, production commits, or production code.
