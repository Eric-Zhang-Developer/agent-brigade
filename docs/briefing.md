# Briefing

At ShellHacks, the team couldn't fully explain its own product to judges, because agents wrote most of the code
and nobody had read it. The briefing is a one-page `docs/briefing.md`, kept current by an agent, so the humans
always understand what they've built.

## When it runs
- Hackathon: before every demo, and as a required step hours before judging (`docs/hackathon/overnight.md`).
- Project: weekly, as part of `docs/project/weekly.md`.

## Prompt
> You are the briefer. Read the constitution, `changes/`, `specs/decisions/` and the code. Rewrite
> `docs/briefing.md` (one page, about 5 minutes to read, plain language) with exactly these sections:
> 1. **The problem**: who has it and why it matters, in 3 sentences.
> 2. **What it does**: the core loop a user goes through, step by step.
> 3. **How it works**: the architecture in 5–8 bullets, naming the real folders. One small diagram if it helps.
> 4. **Honest numbers**: every count or metric, with where it comes from (file, command or source), and what is
>    NOT done, verified or confirmed. Say the limits out loud.
> 5. **What changed since the last briefing**, and why (link decisions).
> 6. **Questions a smart outsider would ask**, with short answers.
> Never invent a number. If you can't trace it, write "unknown" and say what would establish it. Open a PR (it
> owns `docs/briefing.md`).

## Reading it
Read it out loud once before a demo. Anything you can't explain in your own words is the next thing to ask your
agent about.
