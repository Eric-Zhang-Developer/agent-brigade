# Where this came from

I love hackathons because the deadline forces you to finish. Outside of them, I have what I call an icebox: half a
dozen projects I started, loved, and never shipped. This kit is my attempt to fix both sides of that.

## The weekend

In September 2026 I drove to ShellHacks at FIU without a team. Two days earlier I'd posted in a Discord channel
looking for teammates and met three people I'd never worked with. At the sponsor fair we skipped the big names and
picked a smaller company's track: Sperry Tech's "Gridlock," a real problem about power companies planning grid
projects in isolation.

We didn't write code for the first 90 minutes. We wrote five competing plans, scored them against each other, and
turned the winner into a spec: plain-text files that told every AI agent what to build, what it owned, and what
never to do. Then we let the agents go. In 32 hours they produced 307 commits and 349 pull requests with almost no
conflicts. We won first place.

## The honest version

The win hid a lot of cracks.

- The agents needed me every 10 to 30 minutes, because they kept running out of work. I slept about an hour.
- A teammate merged straight into main, conflict markers and all.
- A 1,191-line feature merged four minutes before the deadline. We reverted it with a minute to spare.
- Our live demo crashed in front of a judge. Nothing had tested the production database under real load.

What worked was the spec, the ownership rules, and a test built from the sponsor's own example. What broke was
everything around the agents: every part that still depended on a person being awake.

[OPTIONAL: I'd spent a long job search hearing no. That weekend was the first time my work got to speak for itself,
and I wanted to keep what made that possible.]

## The other half of the problem

The same gap shows up in personal projects, just slower. There's no deadline, so nothing ships. Context fades
between sessions, so every return starts from scratch. Agents forget everything when a session ends, and honestly,
so do I.

## What this kit is

It's the protocol from that weekend, generalized and hardened:

- **The spec is the brain, the agent is the muscle.** Chat history is never the source of truth. The method comes
  from the DeepLearning.AI × JetBrains spec-driven development course.
- **Humans make decisions. Agents do the work.** Agents never sit waiting on a question. They take the safest
  reversible default, log it, and keep going.
- **Never invent.** Every number traces back to a source, and unknowns stay blank.
- **Say your limits out loud.** Our README admitted that only 46 of 3,287 locations were confirmed. That's why people
  believed the rest.

It comes with two profiles. **Hackathon** is tuned for speed, parallel agents and an unbreakable demo. **Project**
is tuned for continuity: a resume file, hard limits on decisions agents can't make alone, and milestones that bring
a little of the hackathon deadline into everyday work.

## What it isn't

It isn't magic, and it doesn't replace judgment. The hard calls are still yours. It's also not project code: it's
tooling, the same as your editor setup.

## Thanks

To my ShellHacks teammates, [Daniel](https://github.com/fradicus), [Kiro](https://github.com/kirolosmaikel-ops) and
[Sharan](https://github.com/iKnow24), who built the first version of this with me under pressure, and to the Sperry
Tech team for a problem worth solving.
