/*
 * Demonstration projection for the Meta PDS dashboard.
 * Replace this object from canonical artifacts; never treat it as authority.
 */
window.META_PDS_DASHBOARD_DATA = {
  schemaVersion: 1,
  projection: {
    kind: "seed-demonstration",
    generatedAt: "2026-08-21T22:42:00+05:00",
    source: "Meta PDS seed artifacts",
    staleAfterMinutes: 90
  },
  initiative: {
    id: "INIT-0042",
    name: "Learning Platform V1",
    shortName: "Learning Platform",
    phase: "PROTOTYPING",
    health: "ON_TRACK",
    progress: 62,
    objective: "A focused learning experience from secure access to measurable progress.",
    humanOwner: "Human Product Owner",
    currentRevision: 3,
    nextAction: {
      title: "Review the Authentication slice hierarchy",
      detail: "Open Authentication to inspect its six stories, nested work packages, contracts, and tests.",
      owner: "Human review",
      impact: "Validates the dashboard projection"
    }
  },
  attention: [
    {
      id: "ATT-01",
      kind: "decision",
      title: "Choose the account recovery route",
      detail: "Email link and one-time-code variants are ready for manual review.",
      age: "12 min",
      affects: ["SLICE-02"]
    },
    {
      id: "ATT-02",
      kind: "review",
      title: "Validate the expired-session experience",
      detail: "Manual navigation is required before the prototype checkpoint can close.",
      age: "24 min",
      affects: ["DEC-009"]
    },
    {
      id: "ATT-03",
      kind: "blocker",
      title: "Confirm transactional email provider",
      detail: "Development can continue locally, but production recovery cannot release.",
      age: "1 hr",
      affects: ["WP-BE-12"]
    }
  ],
  prototype: {
    id: "PROTO-0042-AUTH",
    name: "Authentication journeys",
    description: "Testing recovery, validation, and expired-session states with local fixtures.",
    status: "HUMAN_REVIEW",
    checkpoint: "Checkpoint 07",
    checkpointAt: "2026-08-21T22:36:00+05:00",
    route: "/prototype/auth",
    persistence: "localStorage",
    seedProfiles: 4,
    journeys: {
      reviewed: 5,
      total: 7
    },
    assumptionsTested: 6,
    openQuestions: 2,
    manualReview: "Awaiting Human"
  },
  decisions: [
    {
      id: "DEC-003",
      title: "Email and password are the initial sign-in methods",
      summary: "Social sign-in stays outside V1 scope until adoption evidence exists.",
      status: "LOCKED",
      revision: 2,
      updatedAt: "2026-08-21T20:05:00+05:00",
      affects: ["SLICE-AUTH-001", "SLICE-02"]
    },
    {
      id: "DEC-006",
      title: "Learner and instructor roles stay explicit",
      summary: "Role switching is not allowed within one active session.",
      status: "LOCKED",
      revision: 1,
      updatedAt: "2026-08-21T20:48:00+05:00",
      affects: ["SLICE-AUTH-001", "SLICE-03"]
    },
    {
      id: "DEC-008",
      title: "Recovery uses a single-use email link",
      summary: "The prototype is comparing link-only and link-plus-code recovery.",
      status: "TESTING",
      revision: 3,
      updatedAt: "2026-08-21T22:30:00+05:00",
      affects: ["SLICE-02"]
    },
    {
      id: "DEC-009",
      title: "Expired sessions preserve the intended destination",
      summary: "After sign-in, the learner returns to the page that required access.",
      status: "PROPOSED",
      revision: 1,
      updatedAt: "2026-08-21T22:18:00+05:00",
      affects: ["SLICE-AUTH-001"]
    },
    {
      id: "DEC-010",
      title: "Prototype stores fixtures in localStorage",
      summary: "Local persistence supports manual review without a temporary backend.",
      status: "LOCKED",
      revision: 1,
      updatedAt: "2026-08-21T19:40:00+05:00",
      affects: ["PROTO-0042-AUTH"]
    },
    {
      id: "DEC-002",
      title: "Invite-only learner onboarding",
      summary: "Replaced by controlled self-registration with email verification.",
      status: "SUPERSEDED",
      revision: 2,
      updatedAt: "2026-08-20T17:15:00+05:00",
      affects: ["SLICE-AUTH-001"]
    }
  ],
  slices: [
    {
      id: "SLICE-AUTH-001",
      order: 1,
      title: "Authentication",
      outcome: "A learner can register, verify, sign in, continue or restore a session, recover a forgotten password, and sign out without staff assistance.",
      status: "IN_PROGRESS",
      progress: 64,
      revision: 1,
      priority: "P0",
      dependencies: [],
      stories: 6,
      active: true,
      artifactPath: "skills/slice-planning/assets/authentication-slice-example.md"
    },
    {
      id: "SLICE-02",
      order: 2,
      title: "Account recovery",
      outcome: "A learner can recover access without support intervention.",
      status: "IN_PROGRESS",
      progress: 58,
      revision: 2,
      priority: "P0",
      dependencies: ["SLICE-AUTH-001"],
      stories: 4,
      active: false
    },
    {
      id: "SLICE-03",
      order: 3,
      title: "Course discovery and enrolment",
      outcome: "A learner can find an eligible course and begin learning.",
      status: "READY_FOR_DEVELOPMENT",
      progress: 26,
      revision: 3,
      priority: "P1",
      dependencies: ["SLICE-AUTH-001"],
      stories: 6,
      active: false
    },
    {
      id: "SLICE-04",
      order: 4,
      title: "Learning progress",
      outcome: "A learner can resume and understand progress across lessons.",
      status: "DRAFT",
      progress: 9,
      revision: 1,
      priority: "P1",
      dependencies: ["SLICE-03"],
      stories: 5,
      active: false
    },
    {
      id: "SLICE-05",
      order: 5,
      title: "Instructor reporting",
      outcome: "An instructor can identify engagement and completion risks.",
      status: "PROPOSED",
      progress: 0,
      revision: 0,
      priority: "P2",
      dependencies: ["SLICE-04"],
      stories: 0,
      active: false
    }
  ],
  workPackages: [
    {
      id: "WP-AUTH-01",
      sliceId: "SLICE-AUTH-001",
      title: "Freeze authentication contracts and threat boundaries",
      description: "Lock HTTP errors, session rotation, token purposes, destination safety, rate limits, and audit events.",
      status: "DONE",
      area: "integration",
      owner: "Development Lead",
      ownerInitials: "DL",
      storyIds: ["US-AUTH-01", "US-AUTH-02", "US-AUTH-03", "US-AUTH-04", "US-AUTH-05", "US-AUTH-06"],
      dependsOn: [],
      tests: { passed: 12, total: 12 },
      critical: true
    },
    {
      id: "WP-AUTH-02",
      sliceId: "SLICE-AUTH-001",
      title: "Authentication persistence and migrations",
      description: "Create account, credential, challenge, refresh-session, revocation, and security-event persistence.",
      status: "DONE",
      area: "database",
      owner: "Database Engineer",
      ownerInitials: "DB",
      storyIds: ["US-AUTH-01", "US-AUTH-02", "US-AUTH-04", "US-AUTH-05", "US-AUTH-06"],
      dependsOn: ["WP-AUTH-01"],
      tests: { passed: 19, total: 19 },
      critical: true
    },
    {
      id: "WP-AUTH-03",
      sliceId: "SLICE-AUTH-001",
      title: "Registration and email verification services",
      description: "Implement privacy-safe registration, verification, resend, throttling, and audit behavior.",
      status: "VERIFYING",
      area: "backend",
      owner: "Backend Engineer",
      ownerInitials: "BE",
      storyIds: ["US-AUTH-01", "US-AUTH-02"],
      dependsOn: ["WP-AUTH-01", "WP-AUTH-02"],
      tests: { passed: 21, total: 23 },
      critical: true
    },
    {
      id: "WP-AUTH-04",
      sliceId: "SLICE-AUTH-001",
      title: "Accessible authentication journeys",
      description: "Build registration, verification, sign-in, recovery, expiry, and sign-out states in the frontend.",
      status: "IN_PROGRESS",
      area: "frontend",
      owner: "Frontend Engineer",
      ownerInitials: "FE",
      storyIds: ["US-AUTH-01", "US-AUTH-02", "US-AUTH-03", "US-AUTH-04", "US-AUTH-05", "US-AUTH-06"],
      dependsOn: ["WP-AUTH-01"],
      tests: { passed: 16, total: 24 },
      critical: false
    },
    {
      id: "WP-AUTH-05",
      sliceId: "SLICE-AUTH-001",
      title: "Sign-in, refresh rotation, and revocation",
      description: "Implement verified-account sign-in, refresh rotation, replay detection, safe destination restoration, and sign-out.",
      status: "IN_PROGRESS",
      area: "backend",
      owner: "Security Engineer",
      ownerInitials: "SE",
      storyIds: ["US-AUTH-03", "US-AUTH-04", "US-AUTH-06"],
      dependsOn: ["WP-AUTH-01", "WP-AUTH-02"],
      tests: { passed: 27, total: 34 },
      critical: true
    },
    {
      id: "WP-AUTH-06",
      sliceId: "SLICE-AUTH-001",
      title: "Forgotten-password recovery lifecycle",
      description: "Implement privacy-safe requests, hashed single-use tokens, password reset, session revocation, and notification.",
      status: "BLOCKED",
      area: "backend",
      owner: "Backend Engineer",
      ownerInitials: "BE",
      storyIds: ["US-AUTH-05"],
      dependsOn: ["WP-AUTH-01", "WP-AUTH-02"],
      tests: { passed: 11, total: 18 },
      critical: true,
      blocker: "Local email-adapter fixture is awaiting contract verification"
    },
    {
      id: "WP-AUTH-07",
      sliceId: "SLICE-AUTH-001",
      title: "Authentication lifecycle integration and Playwright CLI suite",
      description: "Verify the complete registration-to-sign-out lifecycle, failure recovery, accessibility, security, and rollback evidence.",
      status: "BLOCKED",
      area: "integration",
      owner: "Integration Engineer",
      ownerInitials: "IE",
      storyIds: ["US-AUTH-01", "US-AUTH-02", "US-AUTH-03", "US-AUTH-04", "US-AUTH-05", "US-AUTH-06"],
      dependsOn: ["WP-AUTH-03", "WP-AUTH-04", "WP-AUTH-05", "WP-AUTH-06"],
      tests: { passed: 8, total: 31 },
      critical: true,
      blocker: "Dependent authentication packages are incomplete"
    },
    {
      id: "WP-DB-11",
      sliceId: "SLICE-02",
      title: "Recovery token persistence",
      description: "Store hashed single-use tokens with expiry and audit metadata.",
      status: "VERIFYING",
      area: "database",
      owner: "Database Engineer",
      ownerInitials: "DB",
      storyIds: ["US-201", "US-203"],
      dependsOn: [],
      tests: { passed: 8, total: 8 },
      critical: true
    },
    {
      id: "WP-BE-12",
      sliceId: "SLICE-02",
      title: "Recovery request and redemption API",
      description: "Create rate-limited recovery requests and redeem valid tokens.",
      status: "BLOCKED",
      area: "backend",
      owner: "Backend Engineer",
      ownerInitials: "BE",
      storyIds: ["US-201", "US-202"],
      dependsOn: ["WP-DB-11"],
      tests: { passed: 9, total: 13 },
      critical: true,
      blocker: "Transactional email provider decision"
    },
    {
      id: "WP-FE-13",
      sliceId: "SLICE-02",
      title: "Recovery request interface",
      description: "Collect account email and show privacy-safe confirmation states.",
      status: "IN_PROGRESS",
      area: "frontend",
      owner: "Frontend Engineer",
      ownerInitials: "FE",
      storyIds: ["US-201"],
      dependsOn: [],
      tests: { passed: 5, total: 8 },
      critical: false
    },
    {
      id: "WP-FE-14",
      sliceId: "SLICE-02",
      title: "Set-new-password interface",
      description: "Validate an active recovery session and set a compliant password.",
      status: "READY",
      area: "frontend",
      owner: "Frontend Engineer",
      ownerInitials: "FE",
      storyIds: ["US-202", "US-203"],
      dependsOn: ["WP-DB-11"],
      tests: { passed: 0, total: 7 },
      critical: true
    },
    {
      id: "WP-INT-15",
      sliceId: "SLICE-02",
      title: "Recovery lifecycle integration",
      description: "Verify expiry, replay prevention, notification, and session invalidation.",
      status: "BLOCKED",
      area: "integration",
      owner: "Integration Engineer",
      ownerInitials: "IE",
      storyIds: ["US-201", "US-202", "US-203", "US-204"],
      dependsOn: ["WP-BE-12", "WP-FE-13", "WP-FE-14"],
      tests: { passed: 0, total: 12 },
      critical: true,
      blocker: "Upstream packages incomplete"
    },
    {
      id: "WP-CT-16",
      sliceId: "SLICE-03",
      title: "Course catalogue contract",
      description: "Freeze browse, eligibility, enrolment, and error payloads.",
      status: "READY",
      area: "integration",
      owner: "Development Lead",
      ownerInitials: "DL",
      storyIds: ["US-301"],
      dependsOn: [],
      tests: { passed: 0, total: 5 },
      critical: false
    }
  ],
  stories: [
    {
      id: "US-AUTH-01",
      sliceId: "SLICE-AUTH-001",
      title: "Register an account",
      status: "VERIFYING",
      workPackageIds: ["WP-AUTH-01", "WP-AUTH-02", "WP-AUTH-03", "WP-AUTH-04", "WP-AUTH-07"],
      acceptance: { passed: 3, total: 4 },
      acceptanceCriteria: [
        "A valid email and compliant password create one unverified learner account.",
        "Known and unknown emails receive privacy-safe responses.",
        "Password requirements and field errors are accessible.",
        "Repeated requests are rate-limited with a safe retry time."
      ]
    },
    {
      id: "US-AUTH-02",
      sliceId: "SLICE-AUTH-001",
      title: "Verify email ownership",
      status: "VERIFYING",
      workPackageIds: ["WP-AUTH-01", "WP-AUTH-02", "WP-AUTH-03", "WP-AUTH-04", "WP-AUTH-07"],
      acceptance: { passed: 3, total: 4 },
      acceptanceCriteria: [
        "A valid unexpired link activates exactly one account.",
        "A consumed link cannot create duplicate verification events.",
        "An expired link offers a rate-limited resend path.",
        "Audit events contain no raw verification token."
      ]
    },
    {
      id: "US-AUTH-03",
      sliceId: "SLICE-AUTH-001",
      title: "Sign in securely",
      status: "IN_PROGRESS",
      workPackageIds: ["WP-AUTH-01", "WP-AUTH-04", "WP-AUTH-05", "WP-AUTH-07"],
      acceptance: { passed: 2, total: 4 },
      acceptanceCriteria: [
        "Verified credentials create an access and rotated refresh session.",
        "Invalid, unknown, and unverified accounts use privacy-safe failures.",
        "Repeated failures trigger the locked throttling policy.",
        "Loading, failure, focus, keyboard, and screen-reader states are accessible."
      ]
    },
    {
      id: "US-AUTH-04",
      sliceId: "SLICE-AUTH-001",
      title: "Continue or restore an authenticated journey",
      status: "IN_PROGRESS",
      workPackageIds: ["WP-AUTH-01", "WP-AUTH-02", "WP-AUTH-04", "WP-AUTH-05", "WP-AUTH-07"],
      acceptance: { passed: 2, total: 4 },
      acceptanceCriteria: [
        "A valid refresh session rotates atomically.",
        "Expired, revoked, or replayed sessions cannot create access.",
        "Reauthentication restores only a permitted same-origin destination.",
        "Concurrent refreshes cannot create multiple valid chains."
      ]
    },
    {
      id: "US-AUTH-05",
      sliceId: "SLICE-AUTH-001",
      title: "Recover a forgotten password",
      status: "BLOCKED",
      workPackageIds: ["WP-AUTH-01", "WP-AUTH-02", "WP-AUTH-04", "WP-AUTH-06", "WP-AUTH-07"],
      acceptance: { passed: 1, total: 5 },
      acceptanceCriteria: [
        "Known and unknown emails receive the same recovery response.",
        "Recovery tokens are hashed, scoped, expiring, and single-use.",
        "A valid link sets a compliant password and consumes the token.",
        "Successful recovery revokes all existing sessions.",
        "The completion notification contains no credential or token."
      ]
    },
    {
      id: "US-AUTH-06",
      sliceId: "SLICE-AUTH-001",
      title: "Sign out safely",
      status: "READY",
      workPackageIds: ["WP-AUTH-01", "WP-AUTH-02", "WP-AUTH-04", "WP-AUTH-05", "WP-AUTH-07"],
      acceptance: { passed: 1, total: 4 },
      acceptanceCriteria: [
        "Current-session sign-out revokes its refresh chain.",
        "All-session sign-out revokes every account session.",
        "Revoked sessions cannot refresh after sign-out.",
        "Local credentials clear even if server revocation temporarily fails."
      ]
    },
    {
      id: "US-201",
      sliceId: "SLICE-02",
      title: "Request account recovery safely",
      status: "IN_PROGRESS",
      workPackageIds: ["WP-DB-11", "WP-BE-12", "WP-FE-13", "WP-INT-15"],
      acceptance: { passed: 4, total: 7 },
      acceptanceCriteria: [
        "The response is identical for known and unknown email addresses.",
        "Requests are rate-limited without exposing private account state.",
        "A valid request creates one expiring single-use recovery token."
      ]
    },
    {
      id: "US-202",
      sliceId: "SLICE-02",
      title: "Set a new password from a valid link",
      status: "READY",
      workPackageIds: ["WP-BE-12", "WP-FE-14", "WP-INT-15"],
      acceptance: { passed: 2, total: 6 },
      acceptanceCriteria: [
        "A valid recovery link opens the set-password journey.",
        "The new password must satisfy the locked password policy.",
        "Successful recovery invalidates existing authenticated sessions."
      ]
    },
    {
      id: "US-203",
      sliceId: "SLICE-02",
      title: "Reject expired or replayed recovery links",
      status: "VERIFYING",
      workPackageIds: ["WP-DB-11", "WP-FE-14", "WP-INT-15"],
      acceptance: { passed: 4, total: 6 },
      acceptanceCriteria: [
        "Expired recovery tokens cannot update credentials.",
        "A redeemed token cannot be used again.",
        "Failure states direct the learner to request a fresh link."
      ]
    },
    {
      id: "US-204",
      sliceId: "SLICE-02",
      title: "Notify the account owner after recovery",
      status: "BLOCKED",
      workPackageIds: ["WP-BE-12", "WP-INT-15"],
      acceptance: { passed: 0, total: 4 },
      acceptanceCriteria: [
        "The account owner receives a recovery-complete notification.",
        "The notification contains no credential or token value."
      ]
    },
    {
      id: "US-301",
      sliceId: "SLICE-03",
      title: "Browse courses available for enrolment",
      status: "READY",
      workPackageIds: ["WP-CT-16"],
      acceptance: { passed: 0, total: 5 },
      acceptanceCriteria: [
        "Only published and eligible courses appear in the catalogue.",
        "Course cards expose enough information to make an enrolment decision."
      ]
    }
  ],
  contracts: [
    {
      id: "CON-AUTH-API",
      sliceId: "SLICE-AUTH-001",
      name: "Authentication HTTP contract",
      type: "OpenAPI",
      version: "v1.0",
      status: "LOCKED",
      owner: "Backend Engineer",
      path: "backend/contracts/auth.openapi.yaml"
    },
    {
      id: "CON-SESSION",
      sliceId: "SLICE-AUTH-001",
      name: "Session lifecycle contract",
      type: "Security contract",
      version: "v1.0",
      status: "LOCKED",
      owner: "Security Engineer",
      path: "backend/contracts/session-lifecycle.md"
    },
    {
      id: "CON-AUTH-DATA",
      sliceId: "SLICE-AUTH-001",
      name: "Authentication data schema",
      type: "Database contract",
      version: "v1.0",
      status: "LOCKED",
      owner: "Database Engineer",
      path: "backend/migrations/041_authentication.sql"
    },
    {
      id: "CON-AUTH-EMAIL",
      sliceId: "SLICE-AUTH-001",
      name: "Transactional authentication email adapter",
      type: "Integration contract",
      version: "v1.0",
      status: "VERIFYING",
      owner: "Integration Engineer",
      path: "backend/contracts/auth-email-adapter.md"
    },
    {
      id: "CON-RECOVERY-API",
      sliceId: "SLICE-02",
      name: "Account recovery API",
      type: "OpenAPI",
      version: "v2.1",
      status: "LOCKED",
      owner: "Backend Engineer",
      path: "backend/contracts/recovery.openapi.yaml"
    },
    {
      id: "CON-TOKEN-SCHEMA",
      sliceId: "SLICE-02",
      name: "Recovery token persistence",
      type: "Database schema",
      version: "v1.0",
      status: "LOCKED",
      owner: "Database Engineer",
      path: "backend/migrations/042_recovery_tokens.sql"
    },
    {
      id: "CON-EMAIL-ADAPTER",
      sliceId: "SLICE-02",
      name: "Transactional email adapter",
      type: "Integration contract",
      version: "v0.3",
      status: "PROPOSED",
      owner: "Integration Engineer",
      path: "backend/contracts/email-adapter.md"
    },
    {
      id: "CON-COURSE-CATALOGUE",
      sliceId: "SLICE-03",
      name: "Course catalogue and eligibility",
      type: "OpenAPI",
      version: "v0.8",
      status: "DRAFT",
      owner: "Development Lead",
      path: "backend/contracts/catalogue.openapi.yaml"
    },
    {
      id: "CON-PROGRESS-EVENT",
      sliceId: "SLICE-04",
      name: "Learning progress event",
      type: "Event schema",
      version: "v0.1",
      status: "DRAFT",
      owner: "Planning Lead",
      path: "docs/meta-pds/contracts/progress-event.md"
    }
  ],
  testCases: [
    { id: "TC-AUTH-01", sliceId: "SLICE-AUTH-001", title: "Registration and duplicate-email privacy", type: "API contract", status: "PASSED", owner: "Backend Engineer", evidence: "reports/auth-registration.xml" },
    { id: "TC-AUTH-02", sliceId: "SLICE-AUTH-001", title: "Verification expiry, replay, and resend", type: "Integration", status: "VERIFYING", owner: "Integration Engineer", evidence: "reports/auth-verification.xml" },
    { id: "TC-AUTH-03", sliceId: "SLICE-AUTH-001", title: "Verified sign-in and privacy-safe failures", type: "Playwright CLI", status: "IN_PROGRESS", owner: "Frontend Engineer", evidence: "reports/auth-sign-in.html" },
    { id: "TC-AUTH-04", sliceId: "SLICE-AUTH-001", title: "Refresh rotation, replay, and concurrent requests", type: "Security integration", status: "IN_PROGRESS", owner: "Security Engineer", evidence: "reports/auth-refresh.xml" },
    { id: "TC-AUTH-05", sliceId: "SLICE-AUTH-001", title: "Expired session restores a safe destination", type: "Playwright CLI", status: "READY", owner: "Slice QA", evidence: "Pending WP-AUTH-07" },
    { id: "TC-AUTH-06", sliceId: "SLICE-AUTH-001", title: "Forgotten-password token and revocation lifecycle", type: "Integration", status: "BLOCKED", owner: "Backend Engineer", evidence: "Blocked by WP-AUTH-06" },
    { id: "TC-AUTH-07", sliceId: "SLICE-AUTH-001", title: "Current and all-session sign-out", type: "API integration", status: "READY", owner: "Security Engineer", evidence: "Pending WP-AUTH-05" },
    { id: "TC-AUTH-08", sliceId: "SLICE-AUTH-001", title: "Complete authentication lifecycle", type: "Playwright CLI", status: "BLOCKED", owner: "Slice QA", evidence: "Blocked by dependent packages" },
    { id: "TC-REC-01", sliceId: "SLICE-02", title: "Recovery request hides account existence", type: "API contract", status: "PASSED", owner: "Backend Engineer", evidence: "reports/recovery-contract.xml" },
    { id: "TC-REC-02", sliceId: "SLICE-02", title: "Recovery request UI states", type: "Component", status: "IN_PROGRESS", owner: "Frontend Engineer", evidence: "Pending WP-FE-13" },
    { id: "TC-REC-03", sliceId: "SLICE-02", title: "Expired token cannot reset password", type: "Integration", status: "PASSED", owner: "Database Engineer", evidence: "reports/token-expiry.xml" },
    { id: "TC-REC-04", sliceId: "SLICE-02", title: "Redeemed token rejects replay", type: "Integration", status: "VERIFYING", owner: "Database Engineer", evidence: "reports/token-replay.xml" },
    { id: "TC-REC-05", sliceId: "SLICE-02", title: "Recovery lifecycle end to end", type: "Playwright CLI", status: "BLOCKED", owner: "Slice QA", evidence: "Blocked by WP-BE-12" },
    { id: "TC-CAT-01", sliceId: "SLICE-03", title: "Catalogue contract examples", type: "Contract", status: "READY", owner: "Development Lead", evidence: "Pending WP-CT-16" },
    { id: "TC-PROG-01", sliceId: "SLICE-04", title: "Progress event schema examples", type: "Schema", status: "DRAFT", owner: "Planning Lead", evidence: "Planning evidence only" }
  ],
  dependencies: {
    criticalPath: ["WP-AUTH-01", "WP-AUTH-02", "WP-AUTH-06", "WP-AUTH-07"],
    currentNode: "WP-AUTH-06",
    risk: "MEDIUM",
    readyPackages: 0,
    blockedPackages: 2,
    executionWave: "Wave 3 of 4",
    nextUnblock: "Verify the provider-neutral local email adapter contract"
  },
  quality: {
    evidenceCoverage: 74,
    suites: [
      { name: "Unit and component", passed: 54, total: 58 },
      { name: "API contract", passed: 17, total: 21 },
      { name: "Playwright CLI", passed: 11, total: 16 },
      { name: "Security checks", passed: 8, total: 10 }
    ],
    openDefects: 2,
    criticalDefects: 0,
    lastVerifiedAt: "2026-08-21T22:11:00+05:00"
  },
  release: {
    status: "NOT_READY",
    target: "Local integration",
    gates: [
      { name: "Planning revision locked", status: "PASSED" },
      { name: "Execution packages complete", status: "IN_PROGRESS" },
      { name: "Independent QA evidence", status: "NOT_READY" },
      { name: "Rollout and rollback prepared", status: "READY" }
    ],
    featureFlag: "authentication-v1",
    rollback: "Disable new entry points and session issuance; retain account and security records"
  },
  drift: [
    {
      id: "DRIFT-01",
      severity: "medium",
      title: "Provider choice is outside the locked execution contract",
      detail: "The affected backend package is paused; independent frontend work continues.",
      affects: "WP-BE-12"
    },
    {
      id: "DRIFT-02",
      severity: "info",
      title: "Slice 03 contract package is ready early",
      detail: "Planning may continue without consuming the active development WIP slot.",
      affects: "SLICE-03"
    },
    {
      id: "DRIFT-03",
      severity: "low",
      title: "One proposed decision has no Human response",
      detail: "Expired-session destination remains proposed and cannot be treated as locked.",
      affects: "DEC-009"
    }
  ],
  activity: [
    {
      at: "2026-08-21T22:42:00+05:00",
      kind: "prototype",
      title: "Prototype checkpoint recorded",
      detail: "Recovery and expired-session variants prepared for manual review."
    },
    {
      at: "2026-08-21T22:30:00+05:00",
      kind: "decision",
      title: "DEC-008 moved to TESTING",
      detail: "Two recovery variants remain visible; no product behavior was locked."
    },
    {
      at: "2026-08-21T22:11:00+05:00",
      kind: "completed",
      title: "WP-DB-11 entered VERIFYING",
      detail: "Migration and token replay tests passed locally."
    },
    {
      at: "2026-08-21T21:54:00+05:00",
      kind: "blocked",
      title: "WP-BE-12 paused safely",
      detail: "External provider decision escalated; unrelated work remained active."
    },
    {
      at: "2026-08-21T20:48:00+05:00",
      kind: "decision",
      title: "DEC-006 locked by Human",
      detail: "Learner and instructor sessions keep explicit roles."
    },
    {
      at: "2026-08-21T19:32:00+05:00",
      kind: "completed",
      title: "SLICE-AUTH-001 entered development",
      detail: "The Authentication planning artifact passed Development Intake and seven bounded work packages were mobilized."
    }
  ]
};
