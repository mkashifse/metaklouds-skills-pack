# Third-party skills

The complete installer downloads these support skills directly from their
original repositories at revisions pinned in `manifest.json`.

| Installed name | Source | License status |
| --- | --- | --- |
| `vercel-react-best-practices` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | No repository license declared when reviewed |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 (`skills/frontend-design/LICENSE.txt`) |
| `vercel-composition-patterns` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | MIT declared in skill metadata |
| `fastapi` | [fastapi/fastapi](https://github.com/fastapi/fastapi) | MIT |
| `nodejs-backend-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | MIT |
| `python-testing-patterns` | [wshobson/agents](https://github.com/wshobson/agents) | MIT |
| `vitest` | [antfu/skills](https://github.com/antfu/skills) | MIT |
| `playwright-best-practices` | [currents-dev/playwright-best-practices-skill](https://github.com/currents-dev/playwright-best-practices-skill) | MIT |
| `supabase` | [supabase/agent-skills](https://github.com/supabase/agent-skills) | MIT |
| `supabase-postgres-best-practices` | [supabase/agent-skills](https://github.com/supabase/agent-skills) | MIT |

These files are not copied into this repository. The installer fetches them
from their maintainers. Their terms, attribution, and update policies continue
to apply.

Updating a pin requires reviewing upstream changes, updating `manifest.json`
and `scripts/install.sh` together, and rerunning installation tests.
