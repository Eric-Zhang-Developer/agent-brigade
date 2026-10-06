# Mission: agent-brigade

## Why
Each weekend's lessons should become infrastructure, so growth compounds instead of depending on memory.

At ShellHacks 2026, four people and their coding agents merged 349 PRs in 32 hours from a shared spec and won
first place. What worked: the spec as the only source of truth, disjoint file ownership, a PR as the claim, done
notes, and defaults instead of questions. What broke was everything that still needed a person awake. Agents ran
out of work every 10–30 minutes. Sessions died. Time gates were only advice. A human merged conflict markers. An
untested feature merged 4 minutes before the deadline. The live demo throttled in front of a judge, and nobody
fully understood the code. Personal projects fail the same way, more slowly: no deadline, context that fades,
casual big decisions, and agent code that never gets read.

## Who
- A student builder at a hackathon, with 1–4 teammates and their agents, who needs to be set up in minutes.
- A solo builder with an icebox of half-finished projects, who wants agents working while they sleep or are in
  class.
- Any coding agent that reads files and runs git (Claude Code, Codex, Cursor and others).

## What
A GitHub template repository: a Markdown protocol, Markdown templates, and Python standard-library scripts.
Two profiles (`hackathon`, `project`) share one core. Two sizes (`lite`, `full`) scale the ceremony from a
weekend side project to a 4-person, 36-hour sprint. Either profile works with one agent or many.

## Goals (decision criteria, in priority order)
1. **Humans decide at checkpoints; agents never wait.** The time between necessary human interventions should be
   hours, not minutes. Agents always have the next ready task, and a blocked agent logs and switches.
2. **Rules are enforced, not remembered.** Anything that must happen is a script, a hook or a CI check, and humans
   are held to the same rules as agents.
3. **Honest by default.** Never invent data. Every number traces to a source. Unknowns stay visible. Say what isn't
   done.
4. **Fast to start.** `init.py` gets a fresh clone ready in under 10 minutes for either profile.
5. **Ships things.** Deadlines, milestones and cut lists exist so work reaches done.
6. **Understood by its humans.** Briefings and judge-style reviews close the gap between what agents built and what
   people can explain.
7. **Credible and generic.** It's legitimate to bring to any hackathon, because it is process tooling, never
   project code.

## Non-negotiables
- **Generic only.** No project or domain logic, and nothing that would count as pre-written hackathon project code.
- **Stack-agnostic.** Protocol and templates are Markdown. Scripts are Python 3.11+, standard library only, with
  config via `tomllib`.
- **Harness-agnostic.** Core files never require a specific agent tool. Tool-specific notes live only in
  `core/docs/integrations/`.
- **One core, two profiles.** Shared behavior lives in `core/` and mode-specific behavior in `profiles/`. No
  duplicated logic.
- **Plain language.** Readable by a second-time hacker. Jargon gets a one-line definition on first use.
- **No invented facts** in docs or examples: no fake metrics, dates or testimonials. Examples use a toy domain and
  say so.
- **Personal material** comes only from `docs/story.md`.
- The ShellHacks team is credited in the README.
