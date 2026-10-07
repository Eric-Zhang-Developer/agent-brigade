# One-way doors

Agents take reasonable defaults so they never wait. That's right for reversible choices and wrong for these: some
decisions are expensive to undo once code and data depend on them. Agents never take a default on a one-way door.

## The rule
If your work needs one of these decided and there's no decision record for it:
1. File a GitHub issue labelled `needs-human` and `one-way-door`, with the options and what each costs
   to reverse. Write `Default taken: none: parked`.
2. Leave your PR as a draft with a note, and switch to your next ready feature.
3. A person decides, writes `specs/decisions/<slug>-<topic>.md`, and closes the issue with a link to it.

## Always one-way doors
- **Data model and schema:** tables, collections, primary keys, ID formats, anything persisted.
- **Auth and identity:** who can log in, how, and what a user account is.
- **Public interfaces:** API shapes others call, URLs people bookmark, file formats others read.
- **The database and hosting platform**, and anything with lock-in or a free-tier limit you'll demo on.
- **Money and secrets:** billing, paid plans, where keys live.
- **Deleting data or history.**
- **Licenses and anything published:** making a repo public, publishing a package, sending email to users.

## This project's additions
<!-- List paths or topics specific to this project, e.g. "anything under db/migrations/". Mirror the paths in
specs/review-paths.toml, so a human also reviews them before merge. -->
-
