# Budget and model routing

Rate limits and spend run out mid-run. Plan them like any other resource.

## Route work by task type
| Task | Use | Why |
|---|---|---|
| Specs, planning, judge review, briefing | Your strongest model | Judgment errors cost the most |
| Feature builds with a clear spec | A strong, cost-efficient coding model | Most of the volume |
| Mechanical fixes, formatting, renames | Your cheapest capable model | Low risk |
| Browser checks / computer use | Whichever tool does it best for you | Capability varies by tool |

Write your actual routing in `specs/tech-stack.md` (or `specs/decisions/000-defaults.md`), with the model names you
use. The table above is a pattern, not a recommendation for any particular vendor.

## Rules
- At **75%** of any budget you can see (subscription limit, API spend), start no new feature work (`AGENTS.md`).
- Billing alerts are not caps. Set a hard limit where your provider allows one.
- Product API keys (the ones your app calls) are separate from coding-agent logins. Budget them separately.
- **Hackathon:** keep `[budget].reserve_final_hours` worth of capacity for fixes, the deploy and the demo. If your
  plan has usage resets, schedule them; don't spend the last one before the freeze.
- **Project:** set `[budget].monthly_usd` and check spend weekly (`docs/project/budget.md`).
