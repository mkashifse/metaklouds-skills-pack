# Work Package and Release Planning

The Human invokes `$full-stack-engineer` directly to implement and verify a
Work Package or bounded production change. The PM does not act as a mandatory
execution intermediary and does not create handoffs for ordinary direct work.

## Work Package contract

Create a Work Package only when durable coordination is useful. Keep it
implementation-ready and concise:

- exact outcome and non-goals;
- linked approved decisions only when material;
- relevant repositories and paths;
- dependencies and acceptance criteria;
- required verification and observable evidence;
- security, migration, rollout, or rollback constraints when applicable.

Do not prescribe an implementation plan that the codebase can answer more
reliably. Do not split frontend, backend, and database work merely to create
more packages; prefer one coherent end-to-end result.

## Completion and release

Implementation evidence should come from changed files and executed checks,
not status claims. Whole-Slice completion may require integrated behavior,
permissions, accessibility, migrations, reliability, observability, rollout,
and rollback evidence, but include only what is material to that Slice.

Production release requires Human approval unless release authority was
explicitly delegated. If implementation reveals a consequential product
decision, return only that decision to the PM; unrelated engineering can
continue.
