# Slice Verification Contract

## Required evidence classes

Apply each when relevant. If marked not applicable, record why.

- requirement and lifecycle traceability;
- unit, component, contract, integration, and regression tests;
- committed Playwright tests executed through CLI for frontend journeys;
- API/data contract and compatibility evidence;
- migration forward and rollback evidence;
- authentication, authorization, privacy, abuse, and security evidence;
- accessibility evidence;
- observability signals and alert behavior;
- deployment, feature-flag, support, and rollback evidence;
- whole-slice smoke and end-to-end behavior in the target environment.

## Browser rule

Do not open or control a browser. Do not use browser MCP, in-app browser tools,
or an agent to click through the UI. CLI-driven Playwright owns automated UI
execution. The Human owns manual prototype interaction.

If CLI execution cannot reach the required environment, report the exact
environment, access, seed, or configuration blocker. Never substitute an agent
browser session.

## Evidence quality

Evidence names the exact command/check, commit or deployment revision, target
environment, result, and artifact/report path. A narrative claim without
reproducible evidence cannot pass a gate.

## Drift review

Compare implemented behavior and changed paths with the locked slice and
contract. Return:

- code/test defect to Slice Development;
- missing or contradictory acceptance to Slice Planning;
- material goal/scope/security change to Product Manager/Human;
- runtime outcome miss to the next planning cycle.
