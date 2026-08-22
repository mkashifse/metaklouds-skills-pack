# Implementation Skill Routing

Meta PDS is the only Human-facing delivery entrypoint. Its four functional
skills own delivery phases; supporting skills provide stack-specific guidance
inside bounded prototype, development, and QA assignments.

## Selection rule

Inspect the actual repository and assigned paths before selecting support
skills. Use only skills supported by the detected stack and work-package scope.
Record the selected names in each execution plan's `applicable_skills` field
and pass the same names in the worker context capsule. A missing applicable
skill blocks only the affected assignment; it does not block dashboard access,
state reconstruction, or unrelated work.

## Routing matrix

| Evidence or assignment | Required support skills |
| --- | --- |
| Disposable product prototype | `prototype`; add `frontend-design` when visual or interaction direction is being tested |
| Production visual interface or UX implementation | `frontend-design` |
| React or Next.js production code | `vercel-react-best-practices` |
| Reusable React component APIs or component composition | `vercel-composition-patterns` plus `vercel-react-best-practices` |
| FastAPI or Pydantic backend | `fastapi` |
| Node.js or TypeScript backend | `nodejs-backend-patterns` |
| Any Supabase product or client work | `supabase` |
| Postgres schema, migration, RLS, query, or database performance work | `supabase-postgres-best-practices`; also use `supabase` when the database is hosted by Supabase |
| Python unit, integration, API, async, or database tests | `python-testing-patterns` |
| Vitest configuration or TypeScript/JavaScript unit and component tests | `vitest` |
| Playwright E2E, component, API, visual, accessibility, CI, or flake work | `playwright-best-practices` |

Do not select both backend stack skills unless the bounded package genuinely
changes both stacks. Do not introduce a framework merely because its support
skill is installed.

## Phase enforcement

- Rapid Prototyping uses `prototype` and, when applicable, `frontend-design`.
  It never uses Playwright or automated browser validation.
- Slice Planning defines required evidence and test classes without choosing
  implementation frameworks that repository evidence has not established.
- Slice Development records and passes the applicable skills for every work
  package before it becomes `READY`.
- Slice QA applies the testing skill matching each committed suite. QA never
  modifies production tests and never substitutes interactive browser control
  for Playwright CLI evidence.

The functional lead must read each selected support skill before launching or
performing the assignment. Support-skill instructions cannot override the
Human authority envelope, Meta PDS gates, repository instructions, path
ownership, or the browser prohibition.
