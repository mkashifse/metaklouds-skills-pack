---
name: meta-brand-guideline
description: Discover, create, refine, standardize, and lock a complete brand identity system from a user brief and repository evidence. Use for brand research, identity direction, brand guidelines, colors, typography, voice, UI styling, visual language, HTML brand showcases, SVG logo masters, mascot or logo refinement, and production PNG exports.
---

# Meta Brand Guideline

Build a production-ready brand system from the user's intent, existing repository
evidence, and professional recommendations. Deliver a locked Markdown guideline,
an interactive HTML showcase, individually approved SVG logo masters, and PNG
exports generated only from locked masters.

## Non-negotiable rules

- Deeply inspect the repository before recommending a direction.
- Detect whether the user wants to create, document, refine, unify, modernize, or
  replace the identity; do not assume every request is a rebrand.
- Treat archived material as historical evidence, never current authority by
  default.
- Ask exactly ten intake questions in one batch after discovery.
- Give one contextual recommendation, its evidence, and an override field for
  every question.
- Treat an unanswered recommendation as accepted. Apply only explicit overrides.
- Recommend one primary brand color unless the user explicitly overrides it.
- Lock the written system before producing logo masters.
- Create, review, and lock SVG logo variations one at a time.
- Generate production PNGs only after every required SVG master is locked.
- Never silently redraw, replace, archive, or delete an approved brand asset.

## Workflow

### 1. Capture the brief and detect intent

Use the supplied brief. If no brief exists, ask once for the brand name, business,
audience, desired position, intended applications, existing assets, and liked or
disliked styles. Do not ask for information already present in the request.

Extract explicit changes and exclusions, elements to preserve, disliked patterns,
target applications, and whether the request concerns a new or existing identity.
Classify the likely intent:

- `CREATE`: no established identity exists;
- `DOCUMENT`: formalize the current identity without redesigning it;
- `REFINE`: improve selected elements while preserving recognition;
- `UNIFY`: resolve inconsistency across active materials;
- `MODERNIZE`: update the system without replacing its identity;
- `REBRAND`: intentionally replace the existing identity.

Treat this classification as a hypothesis until repository discovery confirms it.

### 2. Perform read-only repository discovery

Scan before asking the intake questions. Do not modify files during discovery.

Map active projects, assets, generated material, websites, applications,
documentation, marketing and course material, prototypes, and archives. Ignore
dependency, cache, build, and temporary directories unless they contain the only
relevant evidence.

Search filenames and contents for terms such as `brand`, `identity`, `logo`,
`mascot`, `guideline`, `palette`, `color`, `font`, `typography`, `theme`, `token`,
`component`, `illustration`, `icon`, `voice`, `marketing`, `landing`, `proposal`,
and `brochure`.

Inspect relevant Markdown, HTML, CSS, JavaScript, JSON, SVG, raster images, PDFs,
presentations, font files, and design-token files. Inspect rendered HTML and visual
assets when possible; do not infer the full visual direction from code alone.

Extract:

- brand names, taglines, positioning, audiences, and repeated messages;
- logo and mascot variations, geometry, spacing, and recognizable features;
- repeated HEX/RGB/HSL values, CSS variables, and light/dark theme tokens;
- font families, weights, local font files, and type roles;
- spacing, radii, borders, shadows, surfaces, and component patterns;
- icons, illustrations, photography, backgrounds, mascot gestures, and motion;
- explicit do/don't rules and prior approval or lock statements.

Classify important sources as `CURRENT_LOCKED`, `CURRENT_APPROVED`, `ACTIVE`,
`EXPERIMENTAL`, `GENERATED`, `HISTORICAL`, `ARCHIVED`, or `UNCERTAIN`.

Use this authority order:

1. current explicit user instruction;
2. current locked guideline;
3. approved current assets;
4. current production website or product;
5. recent approved internal prototypes and proposals;
6. repeated tokens across active files;
7. recent marketing material;
8. archives and legacy material;
9. professional recommendation.

Use repository history and modification context when sources conflict. Prefer the
more recent approved source. Explain conflicts instead of blending incompatible
styles.

### 3. Report the detected direction

Before the questionnaire, report:

```markdown
## Detected Direction

Intent: CREATE | DOCUMENT | REFINE | UNIFY | MODERNIZE | REBRAND
Confidence: High | Medium | Low

Preserve:
- ...

Change:
- ...

Missing:
- ...

Evidence:
- [path]: what it establishes
```

Continue with recommendations when the brief is incomplete. Cite the strongest
local evidence paths so the user can challenge the inference.

### 4. Ask exactly ten intake questions in one batch

State:

> These recommendations are based on your brief and the repository. Reply only
> with the question numbers you want to change. Every recommendation you do not
> override will be treated as approved.

For every question provide `Recommended`, `Evidence`, `Why`, and `Override`.

1. **Intent and scope** — Recommend the change mode, preserved recognition,
   permitted changes, exclusions, and applications. Allow an override of scope.
2. **Positioning and audience** — Recommend a positioning statement, primary
   audience, up to two secondary audiences, and customer transformation. Allow an
   override of the statement or audiences.
3. **Personality and voice** — Recommend three to five traits, tone, vocabulary,
   sentence style, preferred/avoided language, and one sample hook. Allow an
   override of individual voice rules.
4. **Primary color** — Recommend one named primary HEX plus hover, active, soft,
   dark-theme, and focus values. Explain recognition and contrast. Allow one
   replacement primary HEX.
5. **Neutrals and functional colors** — Recommend light/dark backgrounds,
   elevated surfaces, primary/secondary text, subtle border, success, warning, and
   error values. Allow role-specific overrides.
6. **Typography** — Recommend display/heading, body/interface, and expressive
   accent roles. Prefer licensed local fonts and assess readability, print,
   performance, and language coverage. Never use the accent face for paragraphs,
   forms, or small UI text. Allow role-specific overrides.
7. **Logo architecture** — Recommend preserve, clean up, refine, reconstruct, or
   redesign; list required primary, compact, stacked, and mark/mascot variations;
   identify features to preserve and geometry to correct. Allow a direction or
   variation override.
8. **Layout and UI** — Recommend grid, spacing, card/button radius, subtle border,
   shadow, surface hierarchy, and light/dark behavior. Prefer tonal separation and
   purposeful containers over excessive boxes. Allow property-specific overrides.
9. **Icons, imagery, illustration, and mascot** — Recommend one coherent icon
   family, photography treatment, illustration language, background treatment,
   mascot construction, and gesture vocabulary. Allow category-specific overrides.
10. **Motion, applications, and governance** — Recommend durations, easing,
    hover/entrance behavior, mascot motion, reduced motion, application priorities,
    ownership, and change control. Allow rule-specific overrides.

Do not ask the questions piecemeal. Later logo approval gates are production
reviews, not additional intake questions.

### 5. Apply overrides and lock the system

Apply only numbered overrides. Preserve all other recommendations. Record each
decision's source as `EVIDENCE`, `USER_INSTRUCTION`, `RECOMMENDATION`, or
`USER_OVERRIDE`. Warn about accessibility or licensing risks, but never silently
replace a selected choice.

Summarize final decisions and ask for one explicit system lock. Treat “lock,”
“approved,” or “proceed” as authorization to write the outputs and begin logo
production.

## Locked guideline

Follow repository conventions or create:

```text
Assets/Brand/<brand-slug>-brand-guidelines.md
```

Include status, semantic version, lock date, owner, evidence, intent, foundation,
positioning, audiences, voice, logo rules, color values in HEX/RGB/CMYK,
typography, tokens, layout, spacing, radii, borders, shadows, components, icons,
photography, illustration, mascot, motion, accessibility, applications, asset
inventory, decision register, and change control.

End with:

> This is the locked source of truth. Unrecorded visual changes are not approved
> brand changes. Future revisions must record the version, date, reason, affected
> rules, regenerated assets, and approval status.

## HTML showcase

Follow repository conventions or create:

```text
Generated/Brand/<brand-slug>-brand-guideline-showcase.html
```

Make the locked decisions visible through a responsive, self-contained showcase
containing foundation, evidence, colors, typography, voice, logos, buttons, cards,
badges, forms, icons, imagery, illustration, backgrounds, mascot gestures, motion,
accessibility, do/don't examples, asset inventory, and lock state.

Use CSS custom properties, local assets/fonts, semantic HTML, keyboard support,
resolved local paths, and `prefers-reduced-motion`. Add a persistent light/dark
switch when both themes are approved. Avoid external dependencies, emoji icons,
unnecessary cards, hard borders, and placeholder logos once masters exist.

## SVG logo production

Start only after the written system is locked. Preserve approved recognition and
compare geometry against the strongest source asset. Do not loosely reinterpret a
raster reference.

Use this dependency order unless the identity requires another:

1. core mark or mascot;
2. primary horizontal logo;
3. compact horizontal logo;
4. stacked logo.

For each variation:

1. Create only the current master SVG.
2. Use true vector geometry, transparent background, a tight intentional
   `viewBox`, approved colors, a meaningful `<title>`, and no external or embedded
   raster dependencies.
3. Avoid clipping, excessive whitespace, distorted proportions, editor metadata,
   and live font dependencies; outline fixed wordmark lettering when practical.
4. Add the master to the showcase on light and dark backgrounds at large, header,
   and minimum sizes.
5. Visually inspect recognizable features, proportions, spacing, baseline,
   alignment, and optical balance.
6. Ask the user to `LOCK` it or request a specific revision.
7. Revise the same master until explicitly locked.
8. Record the locked path and status before creating the next variation.

Never create the next master or PNGs while the current required master awaits
approval.

## PNG production

Begin only after all required SVGs are locked. Render directly from the masters;
never redraw or manually patch PNGs.

Default production set when all four variations are approved:

```text
<brand>-logo-primary.svg
<brand>-logo-compact.svg
<brand>-logo-stacked.svg
<brand>-mascot.svg
png/<brand>-logo-primary-light.png
png/<brand>-logo-primary-dark.png
png/<brand>-logo-compact-light.png
png/<brand>-logo-compact-dark.png
png/<brand>-logo-stacked-light.png
png/<brand>-logo-stacked-dark.png
png/<brand>-mascot-primary.png
```

Use transparent sRGB PNGs with correct alpha, exact SVG geometry, sharp edges,
approved clear space, no clipping, and predictable filenames. Recommended maximum
sizes are 2048 px primary, 1600 px compact, 1200 px stacked, and 1024×1024 mark or
mascot. Add smaller sizes only when required. Do not produce black or white
monochrome variants unless they work visually and receive approval.

## Validation

Before completion:

- confirm Markdown, HTML, tokens, and asset inventory agree;
- confirm every required SVG is explicitly locked;
- validate SVG XML, `viewBox`, vector-only content, and visual fidelity;
- confirm PNGs came from locked SVGs and verify dimensions, alpha, aspect ratio,
  color profile, light/dark use, and absence of clipping;
- resolve every local font and asset path;
- parse HTML JavaScript and inspect desktop/mobile themes visually;
- check WCAG AA contrast, keyboard access, and reduced motion;
- remove placeholders and prevent old or superseded assets from appearing current.

Use states `DISCOVERED`, `RECOMMENDED`, `APPROVED`, `IN_REVIEW`, `LOCKED`,
`SUPERSEDED`, and `ARCHIVED`.

After lock, reopen only affected decisions. Preserve unaffected assets, record the
reason, update the version/date, and regenerate affected PNGs from the revised SVG.
Use patch versions for export corrections, minor versions for usage or spacing
refinements, and major versions for identity-level changes.

## Completion handoff

Provide concise links to the locked Markdown guideline, HTML showcase, approved SVG
masters, and production PNG directory. Report the final asset count, version, lock
date, detected intent, missing assets or licensing risks, and superseded items that
should be archived.
