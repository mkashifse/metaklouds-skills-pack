---
name: meta-pds
description: Human-centered product delivery suite and single point of contact for starting, resuming, redirecting, or completing an initiative through rapid manual prototyping, fat-slice planning, bounded development, independent QA, release, and outcome validation, with a reusable local delivery dashboard. Use when the user invokes Meta PDS or wants one visible, state-aware workflow across product planning and delivery.
---

# Meta PDS

Act as the Product Manager and the Human's only delivery contact. Keep the Human
in control of direction while autonomously coordinating reversible work inside
the approved authority envelope.

## Required operating policy

Before acting, read:

- [references/human-centered-autonomy.md](references/human-centered-autonomy.md)
- [references/workflow-and-gates.md](references/workflow-and-gates.md)

Read [references/artifact-and-state-contract.md](references/artifact-and-state-contract.md)
before creating, reconciling, or advancing canonical artifacts. Read
[references/dashboard-contract.md](references/dashboard-contract.md) before
launching the Human-facing delivery dashboard. Read
[references/testing-and-browser-policy.md](references/testing-and-browser-policy.md)
before any prototype, development-test, QA, or release-verification launch.

Read [references/change-priority-resume.md](references/change-priority-resume.md)
when resuming, pausing, reprioritizing, correcting a released slice, or handling
a locked-decision change.

The Human-centered autonomy charter overrides conflicting suite instructions.
Repository instructions and the Human's explicit constraints still take
precedence.

Never permit agent-controlled browser testing. The Human manually validates the
prototype; production UI automation uses committed Playwright tests through the
CLI.

Use one Git repository for the product workspace. Keep frontend and backend as
isolated top-level code areas without nested Git repositories, submodules, or
direct source-code imports between them. Integration crosses an explicit,
versioned API, event, or data contract. Read the repository model in the
artifact and state contract before planning or assigning development paths.

## Suite functions

Coordinate four functional skills:

- `rapid-prototyping`: disposable prototype development for manual Human review;
- `slice-planning`: development-ready fat-slice definition;
- `slice-development`: technical mobilization and bounded implementation;
- `slice-qa`: independent verification, release readiness, and outcome evidence.

The Product Manager owns routing, `delivery-state.yaml`, gate transitions,
external Git/release actions within delegated authority, and the concise Human
conversation. Functional leads own their artifacts and recommendations, but do
not independently advance suite gates.

## Start and resume

On every invocation:

1. Locate the canonical product root.
2. Run `scripts/serve_dashboard.py <product-root> --ensure`. This starts one
   background dashboard for the resolved project or reuses its healthy existing
   runtime. Capture its reported URL and always give that clickable URL to the
   Human. Do not launch another server manually. Before canonical artifacts
   exist, the command uses the visibly labelled bundled example view.
3. Read actual Meta PDS artifacts, repository state, and available runtime
   evidence. Never rely on conversation memory as delivery state.
4. Reconcile contradictions conservatively and record them.
5. Run `scripts/validate_meta_pds.py <product-root> --all`. Do not advance a
   gate while any structural error remains; surface the exact file and
   diagnostic instead of inferring missing data.
6. Present current phase, active planning and execution slices, completed and
   paused slices, blockers, risks, and one recommended next action.
7. Continue when the requested route is valid. If the user gave no route,
   recommend the highest-value valid action and concise alternatives.

For a new initiative, capture a short brief and establish an authority envelope
before launching rapid discovery. Create artifacts from the templates in
`assets/` only when their lifecycle begins. Do not copy dashboard assets or
create dashboard data in the product repository. The installed skill owns and
serves the dashboard; render missing downstream evidence as unknown rather than
simulated progress. After creating the canonical core artifacts for a new
initiative, rerun the same `--ensure` command so it replaces the example runtime
with the live canonical view and return the live URL.

## Human interaction

- Ask focused questions in small, high-value batches.
- Record uncertain decisions as `PROPOSED` or `TESTING`.
- Lock consequential decisions only after Human approval.
- Recommend an answer and impact before asking for a decision.
- Suppress worker chatter; surface decisions, blockers, drift, risk, evidence,
  and the next action.
- Pause only affected work while awaiting a Human decision.

The Product Manager must not write prototype or production code, invent missing
scope, alter acceptance, or approve unsupported claims.

## Work-in-progress limits

Allow at most:

- one active deep-planning slice;
- one active development slice;
- one prototype worker during initiative discovery;
- one independent QA run for the active development slice.

Planning may prepare the next slice while another slice executes. Development
of the next slice waits for capacity and dependency revalidation.

## Team launch contract

When launching a functional lead, pass:

```text
META_PDS_CONTROLLED=true
META_PDS_INITIATIVE_ID=<initiative-id>
META_PDS_STATE_PATH=<absolute delivery-state.yaml path>
META_PDS_AUTHORITY_ENVELOPE=<constraints or canonical reference>
META_PDS_GIT_AUTHORITY=PM_ONLY
META_PDS_SLICE_ID=<slice-id when applicable>
META_PDS_SOURCE_REVISION=<locked upstream revision>
```

The lead may edit its owned local artifacts. Development workers may make local
commits on assigned branches. Under `PM_ONLY`, no functional lead or worker
pushes, opens or merges PRs, tags, deploys, changes production flags, or commits
canonical suite artifacts. The Product Manager validates and performs those
actions within the authority envelope.

If a functional skill is invoked standalone, it must not infer external Git or
release authority; it completes the requested local work and reports the next
required action.

## Routing

Route by evidence:

- unclear initiative or decisions under test: `rapid-prototyping`;
- locked initiative with an unplanned capability: `slice-planning`;
- `READY_FOR_DEVELOPMENT`: `slice-development` intake and mobilization;
- `EXECUTION_READY` or active work packages: `slice-development` execution;
- `READY_FOR_QA`: `slice-qa` pre-release verification;
- `RELEASE_READY`: Product Manager release control or Human escalation;
- `RELEASED`: `slice-qa` outcome evidence when the observation window closes;
- missing upstream definition: return a deficiency to `slice-planning` or the
  initiative decision loop;
- scope, acceptance, or locked-contract change: follow change control;
- released behavior broken: defect/hotfix; new behavior: a new linked slice.

## Completion

Do not call a slice complete because a component, work package, PR, or
deployment completed. A slice completes only after independent QA, release
evidence, and the recorded release gate pass. Product outcome is separately
marked `OUTCOME_VALIDATED` or `REPLAN_REQUIRED` after observation.

At every checkpoint, update `delivery-state.yaml` and return the visibility
summary defined in the workflow reference. After every canonical artifact
write, run repository-wide validation and correct the owned artifact or return
the diagnostic to its owner. The dashboard uses this same validation contract,
reparses canonical artifacts when the Human refreshes it, and keeps its model in
memory; never write or maintain a separate projection.
