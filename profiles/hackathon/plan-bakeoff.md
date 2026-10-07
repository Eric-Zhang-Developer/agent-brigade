# Plan bake-off (hours 0–2)

At ShellHacks, nobody wrote code for the first 90 minutes. Five competing plans were written, scored on one table,
and merged into a single spec in about 20 minutes. That table turned five opinions into one decision.

## Steps
1. **Read the sponsor material before anyone opens an editor.** Look for an answer key: a worked example with
   known right answers becomes your golden test. Most teams will put the sample data on screen; **the sample
   should be the test, not the dataset.**
2. **Write 3–5 plans in parallel** (agents draft, humans steer), each in `plans/<letter>/PLAN.md`. Same prompt for
   each: the problem, the user, the core loop, the stack, the riskiest assumption, what's cut.
3. **Score them on one table.** Same criteria for every plan:

| Criterion | Plan A | Plan B | Plan C |
|---|---|---|---|
| Solves the judges' actual problem (quote the brief) | | | |
| Core loop demoable in 45 seconds | | | |
| Fits the time, with a safe demo by a fixed hour | | | |
| Setup risk (accounts, keys, data access) | | | |
| Each prize track it qualifies for | | | |
| What 100 other teams will do, and how this differs | | | |

4. **Keep and drop, with reasons.** For each plan, write what you keep and what you drop, and why. Merge the keeps
   into the winner.
5. **Write the non-negotiables as exact rules** in `mission.md` ("under 25 miles; exactly 25 counts").
6. **Stage the ambition** in `roadmap.md`: R0 a safe demo by a fixed hour, R1 the core, R2 the ambitious target,
   R3 one stretch picked at a set hour.
7. Delete `plans/`, or mark it read-only. The spec wins from here on.
