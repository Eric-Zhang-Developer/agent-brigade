# Weekly routine

One sitting a week (about 30 minutes of your time) keeps a project moving, instead of letting it fade into the
icebox. Agents do the prep; you decide.

## 1. Agents prep (run before you sit down)
> Read AGENTS.md. Then:
> 1. `python3 .agents/scripts/status.py --out -` (the status report).
> 2. **Briefing:** rewrite `docs/briefing.md` in its own `docs:` PR (prompt: the kit's docs/briefing.md): what changed this week and why, honest
>    numbers, what isn't done.
> 3. **Planner:** draft next week's features into one `plan:` PR (`docs/planner.md`), sized to what got
>    done this week, aimed at the next milestone.
> 4. Propose an updated `NOW.md` in the same PR.
> 5. **Verifier drift:** run `python3 .agents/scripts/verify.py --slug <slug>` for each feature shipped this week and
>    sort each failure as `docs/verification.md` "Keeping it current" says (recipe drifted, script broke, product
>    regressed).
> Don't merge the `plan:` PR.

At full size, also run the [sampling review](#sampling-review-full-size) as its own agent.

## Sampling review (full size)
Agents self-merge, so nobody reads every PR. Once a week, one agent reads a sample and turns **repeated** mistakes
into checks, so the next agent can't make them. Paste this into a fresh session:

> You are the sampling reviewer. Read AGENTS.md and the kit's `docs/review.md` (the rubric). Then:
> 1. Read the last 5 merged PRs (`gh pr list --state merged --limit 5`), their diffs, done notes and specs on
>    `origin/main`. Also count merged `fix(<slug>)` PRs per feature: three or more means its spec or environment
>    is the problem, not the agent.
> 2. List **repeated** problems only. A class counts once it has happened twice (in this sample, or here plus an
>    earlier PR, a revert or a `specs/context/findings.md` line). Cite each instance by PR and `file:line`.
> 3. For each class, pick the highest fix that works, and say why the higher ones don't:
>    **structure** (make the mistake impossible: one owner, one way, delete the copyable old path), then a
>    **lint or CI check** whose error says the fix, then a **test**, then a **written rule** last.
> 4. Prove each new check: it must fail on the original bad commit (`git checkout <sha> -- <file>`, run the check,
>    paste the failure, then restore the file).
> 5. Reject a candidate that won't be true in 6 months, is too specific to one file or date, is already covered,
>    or happened once. Already covered but buried? Move or reword the existing rule; don't add a second one.
> 6. Which `needs-human` issues this week could the agent have answered by running something? Treat them like
>    any other mistake: twice is a class.
> Output, per class, one of: a `fix:` PR (a lint or test in project code), a `contract:` PR (a rule in
> `AGENTS.md`, or a check under a frozen path; a person merges it), a decision record, or "one-off: <why>".
> List the rejected candidates with their reasons, so a person can overrule you.

Adapted from pstack's `correct` and `reflect` skills (poteto).

## 2. You decide (the checkpoint)
1. Read `docs/briefing.md`. Anything you can't explain, ask an agent to walk you through it. This is how
   comprehension debt gets paid down.
2. Clear the `needs-human` issues. One-way doors first; close each with a decision record.
3. Trim and merge the `plan:` PR.
4. Check the milestone: on track? If not, move something to the cut list **now**, not on ship day.
5. Check spend against `[budget].monthly_usd` (`budget.md`).

## 3. Agents run
Start your agents (or leave them running with the watchdog) and go live your week. Check the Status issue
when you feel like it, not because you have to.
