# Third-party skills

The complete installer downloads the following skills directly from their
original repositories at the revisions recorded in `manifest.json`.

| Installed name | Source | License status |
| --- | --- | --- |
| `prototype` | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT |
| `vercel-react-best-practices` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | No repository license declared when this pack was published |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 (`skills/frontend-design/LICENSE.txt`) |
| `vercel-composition-patterns` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | MIT declared in skill metadata |
| `fastapi` | [fastapi/fastapi](https://github.com/fastapi/fastapi) | MIT |
| `nodejs-backend-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | MIT |
| `python-testing-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | MIT |
| `vitest` | [antfu/skills](https://github.com/antfu/skills) | MIT |
| `playwright-best-practices` | [currents-dev/playwright-best-practices-skill](https://github.com/currents-dev/playwright-best-practices-skill) | MIT |
| `supabase` | [supabase/agent-skills](https://github.com/supabase/agent-skills) | MIT |
| `supabase-postgres-best-practices` | [supabase/agent-skills](https://github.com/supabase/agent-skills) | MIT |

These files are not copied into this repository. The installation script acts
as a convenience client that fetches them from their maintainers. Their
respective terms, attribution, and update policies continue to apply.

The upstream revisions are pinned for reproducible installation. Updating a
pin requires reviewing upstream changes, updating `manifest.json` and
`scripts/install.sh` together, and rerunning the installation test.

## Bundled UI assets

The Meta PDS dashboard embeds selected SVG icons from
[Lucide](https://lucide.dev), distributed under the ISC license. The icons are
stored as a small inline sprite so the local dashboard has no network or runtime
icon dependency.
