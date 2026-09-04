# Thin Role Architecture

The Solo Founder pack uses three independent, explicitly invoked skills.

## Roles

- `solo-founder`: upstream product management, durable decisions, and governed
  artifacts;
- `prototype-engineer`: rapid reversible prototype implementation and visual
  feedback;
- `full-stack-engineer`: direct verified production delivery.

The founder selects the role. The PM does not automatically delegate execution
and remains out of latency-sensitive prototype and development loops.

## Context policy

No role automatically restores the full product context. Each starts from the
Human's current request and inspects only relevant code and artifacts.

`restore_context.py` is reserved for explicit product-wide status, resumption,
audit, reconciliation, or initialization. Prototype and Full-Stack Engineers do
not invoke it by default.

## Artifact policy

Prototype and production execution do not create Work Packages, handoffs,
Ledger entries, or planning documents unless the Human explicitly requests a
record update. A prototype remains a local experiment until the Human asks the
PM to checkpoint, approve, lock, document, or promote it.

## Execution paths

```text
Rapid prototype:
request → inspect relevant files → edit → run → view → adjust

Production delivery:
request or Work Package → inspect relevant code → establish verification
→ implement → test/build → inspect diff → report evidence

Product governance:
question or finding → PM analysis → Human decision → durable artifact when useful
```
