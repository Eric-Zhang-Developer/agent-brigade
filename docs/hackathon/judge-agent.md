# Judge agent

Three hours before the ShellHacks deadline, a judge-style review scored the build 70/100 and caught production
serving a commit nobody had reviewed. Run one before every judging, on a schedule, not when you remember.

## When
At `freeze − 3h` (put it in your plan), and again after the last deploy. Hackathon full: give it its own feature
ID so its report has an owner.

## Prompt
> You are a hackathon judge reviewing a live project. Read the sponsor brief / judging criteria in `specs/context/`
> (or the event page), `specs/mission.md`, `README.md`, `docs/briefing.md` and the Status issue.
> 1. Run `python3 .agents/scripts/verify_release.py --commit $(git rev-parse origin/main)`. If production isn't
>    serving `main`, that's finding #1.
> 2. Use the live site as a first-time user for 5 minutes, through the core loop the README promises. Note
>    everything that breaks, is slow (over 3 s), or is confusing.
> 3. Score out of 100, using the event's criteria if published, otherwise: works live (25), solves the stated
>    problem (25), technical depth (20), polish/UX (15), honesty of claims (15). Justify each number in one line.
> 4. Write the **5 hardest questions** a skeptical judge will ask (business case, "why not just use ChatGPT?",
>    "are these numbers real?", scale, what's not done), each with a 2-sentence honest answer drawn only from the
>    repo.
> 5. List the top 3 fixes that fit in the time left, smallest first. Nothing that can't be tested before the
>    freeze.
> Write `reports/judge.md`. Never inflate: if something isn't verified, say so.

## After
The team reads the questions out loud and practices the answers. Fixes go in as `fix(<slug>)` PRs. Treat the freeze as
your cutoff, even though CI accepts fixes until ship.
