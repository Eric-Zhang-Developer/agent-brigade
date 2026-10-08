# 000: Project defaults (read before every feature)

Settled 2026-10-06 in planning and kept current since. Each row says how to undo it.

| # | Topic | Default | Undo |
|---|---|---|---|
| D1 | Profile vs. size | Two separate dials. `profile` (hackathon / project) sets the clock. `size` (lite / full) sets ceremony and parallelism. Multi-agent work is supported in both profiles. | Merge the dials into one setting |
| D2 | Kit's own specs | Live in `dev/`. The installer only copies `template/`, so projects never see them. | Move them to `specs/` |
| D3 | Judgment calls | `needs-human` GitHub issues (v0.2; replaced the v0.1 `specs/inbox/` files). | Go back to one file per item |
| D4 | Planner queue | The planner opens a `plan:` PR that adds new feature specs and lists them in `milestones.toml`. The open PR *is* the proposed queue. A human approves the batch by merging it, deleting any spec they don't want first. `plan:` PRs are never self-merged. | Use a `specs/proposed/` folder instead |
| D5 | Review paths | `review-paths.toml` is turned into `.github/CODEOWNERS` by the installer; GitHub's "require code owner review" enforces it. No custom checker. | Add a CI check that reads PR reviews via `gh` |
| D6 | Watchdog restart | Runs a user-configured command template from `.agents/config.toml` (`[watchdog].restart`). Agents touch a heartbeat file each loop; a stale heartbeat means a dead session. Per-harness recipes live in `docs/integrations/`. | Add built-in adapters per harness |
| D7 | One deadline model | `check_gates.py` reads `milestones.toml` for both profiles (v0.3; `gates.toml` is gone). | Split per profile |
| D8 | `NOW.md` | Listed in `[ownership].open`, so any PR may edit it. In `full` size only the lead session updates it, to avoid conflicts. Feature agents put state in their done notes. | Make it a frozen path |
| D9 | Example domain | A toy, clearly labeled (for example a word-frequency CLI). Never anything shaped like a real hackathon project. | none |
| D10 | Commits | No `Co-Authored-By` or other trailers (Eric's standing rule). | none |
| D11 | License | MIT (Eric, 2026-10-08), chosen before going public. | Relicense (needs every contributor's agreement) |
| D12 | Repo | `Eric-Zhang-Developer/agent-brigade`, private while it's being built. Eric flips it public. | none |

## Ambiguity rules (when the spec, your Defaults and this table are all silent)
1. Keep every rule in `mission.md` exact.
2. Prefer showing "unknown / not done" over guessing.
3. Prefer the smaller change that someone else can undo.
4. Prefer the standard library and plain files over anything clever.
5. Log the choice in `dev/specs/decisions/<topic>.md`: context, options, choice, how to undo.
