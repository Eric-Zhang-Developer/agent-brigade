# Weekly routine

One sitting a week (about 30 minutes of your time) keeps a project moving, instead of letting it fade into the
icebox. Agents do the prep; you decide.

## 1. Agents prep (run before you sit down)
> Read AGENTS.md. Then:
> 1. `python3 .agents/scripts/status.py` (the status report).
> 2. **Briefing:** rewrite `docs/briefing.md` (`docs/briefing.md`): what changed this week and why, honest
>    numbers, what isn't done.
> 3. **Planner:** draft next week's features into one `[PLAN]` PR (`docs/planner.md`), sized to what got
>    done this week, aimed at the next milestone.
> 4. Propose an updated `NOW.md` in the same PR.
> Don't merge the `[PLAN]` PR.

## 2. You decide (the checkpoint)
1. Read `docs/briefing.md`. Anything you can't explain, ask an agent to walk you through it. This is how
   comprehension debt gets paid down.
2. Clear the `needs-human` issues. One-way doors first; close each with a decision record.
3. Trim and merge the `[PLAN]` PR.
4. Check the milestone: on track? If not, move something to the cut list **now**, not on ship day.
5. Check spend against `[budget].monthly_usd` (`budget.md`).

## 3. Agents run
Start your agents (or leave them running with the watchdog) and go live your week. Check the Status issue
when you feel like it, not because you have to.
