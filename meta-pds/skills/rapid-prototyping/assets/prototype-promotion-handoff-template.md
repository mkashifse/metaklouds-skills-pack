# Prototype Promotion Handoff

## Status and source

- Prototype mode: `PRODUCTION_INTENT`
- Prototype path:
- Target frontend area:
- Target framework and version evidence:
- Relevant locked Truth keys:
- Human review status:

The immutable source revision is the Product Manager checkpoint commit that
contains this handoff and the reviewed prototype files.

## File promotion map

| Prototype source | Intended production target | Classification | Truth keys | Required hardening |
| --- | --- | --- | --- | --- |
| `prototypes/<initiative-id>/src/...` | `frontend/src/...` | `REUSE_AS_IS` |  | None |

Allowed classifications:

- `REUSE_AS_IS`: copy the reviewed file first; ordinary integration edits and
  production tests may follow.
- `HARDEN_THEN_REUSE`: copy the reviewed file, then complete the listed
  accessibility, state, error, performance, security, or integration work.
- `REFERENCE_ONLY`: do not copy into production; use only as behavior or visual
  evidence.

## Fake and disposable boundaries

- Fixtures:
- Fake adapters:
- `localStorage` or prototype-only state:
- Prototype routing or shell:
- Other files that must never be promoted:

## Production integration gaps

- API or generated-client integration:
- Authentication and authorization:
- Accessibility hardening:
- Error, loading, empty, retry, and recovery behavior:
- Responsive and performance work:
- Unit, component, and Playwright CLI coverage:

## Regeneration exceptions

List a file only when promotion is unsafe. Record the source path, reason,
affected Truth keys, and the replacement owner. Absence from this section means
the Frontend Engineer must promote eligible code before considering a rewrite.
