# Work Classification, Roles, and Parallelism

Classification describes complexity and risk; it does not determine who writes
code. Assignment describes the actor. Keep them separate.

## Three actors, two specialist roles

| Actor or role | Owns |
| --- | --- |
| PM | All business/product research, canonical documentation, planning, classification, assignment, and verification; performs trivial non-code work directly |
| `PROTOTYPE_ENGINEER` | Production-intent prototype implementation, local seed adapter, approved UI/UX and design system, prototype tests, and promotion handoff |
| `FULL_STACK_ENGINEER` | Production database, backend, contracts, frontend/mobile, tests, infrastructure, release, and operations work |

The Prototype Engineer and Full-Stack Engineer are full-stack capable. Their
role names identify the delivery stage, not a technical permission wall.
`FRONTEND`, `BACKEND`, and `FULL_STACK` are Work Package focus values, never
specialist roles.

No permanent research, finance, legal, data, QA, security, platform, frontend,
or backend specialist role exists. The PM performs and documents research. If
material legal, financial, regulatory, or other professional risk exceeds the
PM's reliable authority, present the limitation and recommend qualified
external help to the Human.

## Trivial and non-trivial

- `TRIVIAL`: bounded, reversible, low-risk, and supported by approved Truth.
- `NON_TRIVIAL`: substantial uncertainty, experimentation, architecture,
  integration, risk, or production impact.

The PM handles trivial non-code work. Any code mutation is assigned to exactly
one Prototype Engineer or Full-Stack Engineer by default—even when the change
is `TRIVIAL`. This preserves the PM identity without splitting a small vertical
change across workers.

One Full-Stack Engineer normally owns the complete change:

```text
database → contract → backend → frontend/mobile → tests → evidence
```

## Role boundaries

Both engineers may update only their assigned Work Package's status, result,
evidence, blocker, and discovered issues. They write only assigned paths and
cannot change Mode, Layer, scope, role, owner, focus, acceptance, dependencies,
initiative state, next action, authority, approved Truth, or another Work
Package. They cannot delegate further or mark work `DONE`.

The Prototype Engineer works in `prototypes/` and produces a promotion handoff.
The Full-Stack Engineer works in production paths. Moving prototype code into
production is Full-Stack Engineer work unless the PM explicitly assigns the
same worker a new production Work Package.

## Parallelism exception

Do not involve a second Full-Stack Engineer merely because a change touches
frontend, backend, and a table. Parallelize only when all are true:

1. two or more Work Packages can genuinely run concurrently;
2. the shared contract is already established;
3. owned paths and integration responsibility are explicit;
4. each package can be independently verified;
5. expected time saved exceeds coordination and integration cost.

Parallel workers share the `FULL_STACK_ENGINEER` role and receive distinct
owner identities, such as `full-stack-1` and `full-stack-2`. `FRONTEND` and
`BACKEND` describe their temporary focus. The PM remains the only coordinator
and Human contact.

## Delegation messages

For one small engineering change:

```text
I am assigning this end-to-end to one Full-Stack Engineer because it changes
code. It is a small cross-stack change, so I will not split it.
```

For non-trivial work:

```text
I am delegating this task because it is non-trivial: {reason}.
Assigned to: {Prototype Engineer or Full-Stack Engineer}. It may take a while.
I will verify the result against: {expected outcome}.
```

For justified parallel work:

```text
I am using {count} Full-Stack Engineers because these bounded Work Packages can
run independently. The shared contract and integration owner are already clear.
```

Keep later updates short and only report meaningful progress, verification,
completion, or a blocker.
