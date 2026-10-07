# Planner

Agents ran out of work at ShellHacks, and only humans wrote specs, so someone had to be awake every 10–30
minutes. The planner fixes that: an agent drafts the next batch of feature specs, and a human approves the whole
batch at a checkpoint.

## When it runs
- Hackathon: hourly, and whenever the status report says **Backlog low**.
- Project: weekly (`profiles/project/weekly.md`), and when the backlog runs low.

## Target
Keep ready + claimed features at about **2× `[agents].max_parallel`**. Fewer, and agents idle. Many more, and
the specs go stale before anyone builds them.

## Prompt (paste into any agent)
> You are the planner. Read AGENTS.md, then from origin/main: `kit.toml`, the constitution, `reports/status.md`
> (run `python3 core/scripts/status_report.py` first), every file in `specs/decisions/` and `specs/inbox/`, and
> `specs/context/` if it exists.
> Draft just enough new features to bring ready + claimed to 2× max_parallel. For each one:
> - copy `specs/features/_template/` to `specs/features/F<next>-<slug>/`, fill every section, and pick `owns`
>   prefixes that overlap nothing (run `check_ownership.py --lint-specs`)
> - keep it under the PR size cap, or plan it in parts
> - tie it to a roadmap stage or milestone, and add its row to `specs/roadmap.md`
> - turn inbox answers and demo feedback into requirements. Never invent facts; cite the context file.
> - add nothing on the roadmap's "Not doing" list. Add no one-way-door work without a decision record.
> Open ONE PR titled `[PLAN] <date> batch of N` listing each feature in one line, and why it matters now. Never
> merge it yourself.

## The human's side
Review the `[PLAN]` PR in one pass. Delete the specs you don't want, edit what's wrong, then merge. Merging is the
approval: builders pick up the new features on their next run.
