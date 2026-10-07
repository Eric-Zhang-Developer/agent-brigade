
## Project rules
- **`NOW.md` is the resume point.** Read it first. The session lead updates it last (a `docs:` PR): where things
  stand, the one next step, open questions. Builders put their state in done notes, not in `NOW.md`.
- **One-way doors: no defaults, ever.** Data model and schema, auth and identity, public APIs and URLs, the database
  and hosting, money and secrets, deleting data, anything published. File a `needs-human` + `one-way-door` issue and
  switch tasks.
- **Milestones** in `specs/milestones.toml` are enforced by CI: inside a milestone's freeze, only its own features
  merge, and features on its cut list don't. When one ships, `python3 .agents/scripts/ship.py <milestone>` archives
  its specs and writes the release page; open it as a `plan:` PR.
- **Budget:** at 75% of any spend or usage limit you can see, start no new feature work.
