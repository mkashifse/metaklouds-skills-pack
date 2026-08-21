---
schema_version: 2
initiative_id: INIT-0042
initiative_revision: 3
slice_id: SLICE-AUTH-001
title: Authentication
slice_revision: 1
status: READY_FOR_DEVELOPMENT
order: 1
priority: P0
dependencies: []
capability_family: Authentication and account access
source_commit: sample
---

# Authentication

## Capability outcome

A new or returning learner can create an email-and-password account, verify
ownership, sign in securely, remain signed in across normal navigation, recover
from an expired or forgotten credential state, and sign out without staff
assistance.

The slice is valuable when the complete account-access lifecycle is usable,
secure, accessible, observable, and independently releasable—not when an
individual screen or endpoint is complete.

## Scope and non-goals

### In scope

- learner self-registration using email and password;
- email ownership verification and safe resend behavior;
- verified-account sign-in and privacy-safe failure states;
- short-lived access sessions with rotated refresh sessions;
- safe return to an intended permitted destination after reauthentication;
- forgotten-password recovery using an expiring single-use email link;
- current-session and all-session sign-out;
- rate limiting, security audit events, accessible UI states, operational
  metrics, feature-flag rollout, and rollback behavior.

### Non-goals

- social login, enterprise SSO, passkeys, or passwordless sign-in;
- multi-factor authentication;
- administrator-created or invite-only accounts;
- role and permission management beyond applying the locked default learner
  role;
- profile editing, account deletion, or email-address change;
- production selection or commercial approval of an email provider.

## Authoritative sources and locked decisions

| Source | Revision/commit | Relevance |
| --- | --- | --- |
| `docs/meta-pds/initiative.md` | INIT-0042 r3 | Target users, V1 outcome, scope and non-goals |
| `docs/meta-pds/decision-log.yaml#DEC-003` | r2 LOCKED | Email and password are the initial sign-in methods |
| `docs/meta-pds/decision-log.yaml#DEC-006` | r1 LOCKED | Learner and instructor roles remain explicit |
| `docs/meta-pds/decision-log.yaml#DEC-009` | r2 LOCKED | Safe intended destinations survive reauthentication |
| `prototypes/INIT-0042/auth/` | checkpoint 07 | Manually reviewed registration, sign-in, expiry and recovery journeys |

## Lifecycle and journeys

| Flow | Actor | Starting state | Outcome | Failure/recovery |
| --- | --- | --- | --- | --- |
| Register | Guest | No account | Unverified learner account created; verification sent | Existing email receives the same privacy-safe response; rate limits explain when retry is allowed |
| Verify email | Unverified learner | Valid verification link | Account becomes verified and can sign in | Expired or replayed link is rejected; learner can request a replacement |
| Sign in | Verified learner | Signed out | Authenticated session created and safe destination restored | Invalid credentials reveal no account-existence information; throttling applies after repeated failures |
| Continue session | Signed-in learner | Valid refresh session | Access session rotates without interrupting navigation | Invalid or revoked refresh session returns to sign-in without corrupting local state |
| Reauthenticate | Learner with expired session | Protected journey interrupted | Learner signs in and returns to the permitted intended destination | Unsafe or unauthorized destinations fall back to the learner home page |
| Recover password | Verified learner | Password forgotten | Single-use recovery link sets a new password and revokes previous sessions | Unknown email gets the same response; expired/replayed links require a fresh request |
| Sign out | Signed-in learner | One or more sessions | Current session or all sessions are revoked as selected | Local credentials are cleared even if server revocation temporarily fails; retry is observable |

## User stories and acceptance

### US-AUTH-01 — Register an account

**Story:** As a new learner, I can register with an email and compliant password
so that I can begin account verification without staff assistance.

**Acceptance criteria:**

- Given a valid email and compliant password, submitting registration creates
  one unverified learner account and queues one verification message.
- Known and unknown email addresses receive privacy-safe responses that do not
  expose whether an account exists.
- Password requirements are visible before submission and validation errors are
  associated with their fields for keyboard and screen-reader users.
- Repeated requests are rate-limited and communicate a safe retry time.

### US-AUTH-02 — Verify email ownership

**Story:** As a registered learner, I can verify ownership of my email so that
my account becomes eligible to sign in.

**Acceptance criteria:**

- A valid, unexpired verification link activates exactly one account.
- Reusing a consumed link is safe and does not create duplicate verification
  events.
- An expired link explains the problem and provides a rate-limited resend path.
- Verification success and failure emit auditable security events without
  recording raw tokens.

### US-AUTH-03 — Sign in securely

**Story:** As a verified learner, I can sign in with email and password so that
I can access protected learning journeys.

**Acceptance criteria:**

- Correct credentials for a verified active account create an access session
  and a rotated refresh session.
- Incorrect credentials, unknown accounts, and unverified accounts use
  privacy-safe failure responses.
- Repeated failures trigger the locked throttling policy without permanently
  denying a legitimate learner.
- Loading, success, failure, and disabled states meet keyboard, focus, contrast,
  and screen-reader requirements.

### US-AUTH-04 — Continue or restore an authenticated journey

**Story:** As a signed-in learner, I can continue a normal session or
reauthenticate after expiry without losing my intended safe destination.

**Acceptance criteria:**

- A valid refresh session rotates and issues a new access session atomically.
- Expired, revoked, or replayed refresh sessions cannot create access sessions.
- Reauthentication restores only a same-origin destination the learner is
  authorized to access; otherwise it uses the learner home page.
- Concurrent refresh attempts do not create multiple valid refresh-session
  chains.

### US-AUTH-05 — Recover a forgotten password

**Story:** As a verified learner who forgot a password, I can set a new password
through an expiring email link so that I can regain access independently.

**Acceptance criteria:**

- Recovery requests return an identical response for known and unknown emails.
- The stored recovery token is hashed, single-use, scoped to one account, and
  expires at the locked duration.
- A valid recovery link accepts a compliant new password, consumes the token,
  and revokes all existing sessions in one recoverable operation.
- Expired or replayed links cannot change credentials and provide a fresh
  request path.
- Successful recovery sends a notification containing no password or token.

### US-AUTH-06 — Sign out safely

**Story:** As a signed-in learner, I can sign out of this session or all sessions
so that I control access to my account.

**Acceptance criteria:**

- Current-session sign-out revokes its refresh-session chain and clears local
  authentication state.
- All-session sign-out revokes every active refresh-session chain for the
  account.
- A revoked session cannot be refreshed after sign-out.
- If server revocation is temporarily unavailable, local credentials are still
  removed and the failed revocation is observable for bounded retry.

## Security, accessibility, and operations

- Store passwords only through the approved adaptive password-hashing policy;
  never log credentials, raw verification tokens, raw recovery tokens, access
  tokens, or refresh tokens.
- Store verification and recovery tokens as hashes with purpose, account,
  creation, expiry, consumption, and audit metadata.
- Rotate refresh sessions and detect replay; revocation must be idempotent.
- Apply per-IP and per-account throttling to registration, verification resend,
  sign-in, refresh, and recovery without creating account-enumeration signals.
- Protect browser sessions according to the locked transport, cookie, CSRF,
  origin, and content-security policies.
- All flows must be fully keyboard operable, preserve logical focus, expose
  programmatic names and errors, avoid color-only meaning, and satisfy the
  product contrast target.
- Support staff may inspect event IDs, delivery status, throttling state, and
  revocation state but cannot view credentials or raw tokens.

## Contracts and dependencies

### Contract expectations

| Contract | Version | Owner | Required behavior |
| --- | --- | --- | --- |
| Authentication HTTP API | v1 | Backend | Register, verify, resend, sign in, refresh, recover, reset, sign out and sign out all with stable privacy-safe errors |
| Session lifecycle | v1 | Security/Backend | Access expiry, refresh rotation, replay detection, revocation and intended-destination rules |
| Authentication data schema | v1 | Database | Accounts, password credentials, verification/recovery challenges, refresh sessions and security audit events |
| Transactional email adapter | v1 | Integration | Verification, recovery and recovery-complete messages with provider-neutral delivery results |

### Upstream and cross-slice dependencies

- Initiative revision 3 and decisions DEC-003, DEC-006, and DEC-009 must remain
  locked.
- The product shell must provide the same-origin intended-destination handoff.
- Course and progress slices may depend on authenticated learner identity, but
  Authentication does not depend on those slices.
- Production email-provider approval is a release-environment dependency, not
  permission to change the locked adapter contract.

### Assumptions and risks

- Email delivery delay or failure could strand verification and recovery;
  delivery state and resend limits must be visible to operations.
- Session rotation and retry races are a high-risk concurrency boundary and
  require integration evidence.
- Privacy-safe errors may reduce troubleshooting detail; support evidence must
  use correlation IDs rather than revealing account state.
- Automated credential attacks require measurable throttling and alerting
  before public rollout.

## Observability, rollout, and rollback

- Emit structured events for registration requested, verification sent,
  verification completed/failed, sign-in succeeded/failed/throttled, refresh
  rotated/replayed, recovery requested/completed/failed, and session revoked.
- Dashboard measures include registration completion, verification delivery and
  completion, sign-in success/failure/throttle rate, refresh replay, recovery
  completion, email-delivery failure, and revocation failure.
- Alert on sustained delivery failure, abnormal sign-in failure or throttling,
  refresh replay, and revocation failure without exposing personal data.
- Roll out behind `authentication-v1` to internal accounts, then an approved
  cohort, then all eligible users after Slice QA evidence.
- Rollback disables new entry points and session issuance while preserving
  account, audit, and revocation records. Schema rollback must not destroy
  credentials or security evidence.

## Requirement traceability

| Requirement | Story | Acceptance evidence |
| --- | --- | --- |
| Registration and privacy-safe duplicate handling | US-AUTH-01 | Component, API contract, rate-limit integration and Playwright CLI journeys |
| Email verification and resend | US-AUTH-02 | Token lifecycle integration, email-adapter contract and Playwright CLI journeys |
| Verified-account sign-in | US-AUTH-03 | Unit, API contract, security, accessibility and Playwright CLI journeys |
| Refresh, expiry and safe destination restoration | US-AUTH-04 | Concurrency integration, security and Playwright CLI journeys |
| Forgotten-password recovery | US-AUTH-05 | Token lifecycle, revocation, notification and Playwright CLI journeys |
| Current/all-session sign-out | US-AUTH-06 | API contract, revocation integration and Playwright CLI journeys |

## Planning validation

- Structural validation: passed against Meta PDS slice headings and traceability
- Planning Lead sign-off: passed; coherent end-to-end capability family
- Risk-triggered reviews: security, accessibility, data and operations passed
  for planning; implementation evidence remains downstream
- Development Intake review: FEASIBLE using the single-repository frontend and
  backend boundaries
- Open blockers: none for development; production email-provider approval is a
  release-environment dependency

## Human decisions required

None. Scope, sign-in method, role behavior and destination restoration are
locked. Production release still follows the recorded authority envelope.
