# Review rubric

For the reviewer, the gardener and the weekly sampling review (`roles.md`, `project/weekly.md`). Review against the
intent (the spec's Requirements), not your taste. Condensed from pstack's `interrogate` and `blast-radius` skills
(poteto).

## Look for
- **The real thing, not a proxy.** A check that reads a file's age, a cached value or a log line instead of the
  actual state is a gap.
- **Artifacts, not self-reports.** A done note or PR body that says "tested" proves nothing. Look for the command,
  its output and the commit it ran on (`verification.md`).
- **The one fact it's safe because of.** Most risky-looking changes are safe because of one fact. Name it, and say
  how far its evidence got: *said* < *cited `file:line`* < *ran a check* < *reproduced live*. Below "ran a check"
  on a risky change is a finding.
- **Where grep stops.** Formats and wire shapes, database columns, config keys and feature flags, another language
  reading the same file, code a few hops downstream. Listing callers isn't the job.
- **A written rule where a structure would be better.** A comment or rule that says "don't do X" when a lint, a
  type or one owner would make X impossible.
- **Two ways of doing one thing, left behind.** A new path next to the old one it replaced. Agents copy whichever
  they see first; migrate the callers and delete the old one.
- **Root cause or symptom.** A guard, retry or cast that hides a broken contract somewhere else.

## Verdict
Sort every finding into **Act on** (would block a real PR), **Consider**, **Noted** or **Dismissed** (wrong or
missing context, with one line why). Show the dismissed ones: that's how a person overrules you. More than 5 Act on
items means you aren't filtering hard enough. "I'd have done it differently" isn't a finding unless you can show the
concrete problem.
