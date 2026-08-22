# Testing and Browser Policy

## Absolute browser-control prohibition

Agents must never use an interactive browser-control tool for testing or
validation. This includes in-app browser control, browser MCP tools, Codex or
Claude browser agents, and ad-hoc agent clicking or navigation.

This rule applies across Meta PDS, including prototyping, development, QA,
release verification, and remediation. Do not treat browser automation by an
agent as a convenient fallback.

## Rapid prototype phase

- Prototype UI validation is entirely manual by the Human.
- The Prototype Engineer runs the app and provides clear paths and seeded
  scenarios for the Human to open, click, and navigate.
- Use local JSON and, when persistence helps, `localStorage` with resettable
  seeds.
- Do not create or run automated UI tests during rapid prototyping.
- Record Human observations as decisions or prototype findings.

## Production development and QA

- Frontend UI automation uses committed Playwright tests executed through the
  Playwright CLI.
- Run tests non-interactively from the terminal or CI.
- QA may inspect CLI output, machine-readable reports, traces, screenshots, and
  videos as files. It must not open an interactive browser to reproduce a flow.
- Add or correct Playwright tests in the owning development work package; QA
  reports missing coverage back to Development.
- Use unit, component, contract, integration, migration, security, and other
  repository-native tests where appropriate.

If Playwright CLI or the required test environment is unavailable, record the
exact blocker and required action. Never replace it with agent-driven browser
testing.
