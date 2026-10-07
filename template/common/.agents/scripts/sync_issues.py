#!/usr/bin/env python3
"""Keep one GitHub issue per feature spec, so the issues list is the human's view of the whole backlog.

  sync_issues.py [--dry-run]

CI runs this on every push to main. For each specs/features/<ID>-*/spec.md:
  no issue titled "[<ID>] ..."     create one: a link to the spec, labelled `feature`
  spec name changed                 retitle the issue
  changes/<ID>.md exists (done)     close the issue
The spec stays the source of truth; the issue is where people track and discuss it. Bodies and comments are never
rewritten after creation, and a closed issue is never reopened (a human may have closed it on purpose).
Also makes sure the labels the workflow uses exist.
"""

import sys

from lib import as_list, done_ids, gh, gh_json, load_config, load_specs, parser, root_from

LABELS = {
    "feature": ("1d76db", "A feature spec in specs/features/"),
    "needs-human": ("d93f0b", "A judgment call waiting on a person"),
    "one-way-door": ("b60205", "A decision that's expensive to undo; agents take no default"),
    "blocked": ("fbca04", "Work that can't continue until something else happens"),
    "main-red": ("b60205", "main CI is failing"),
    "contract-change": ("5319e7", "A change to frozen shared files ([C<n>] PR)"),
    "status": ("0e8a16", "The pinned status report"),
}


def ensure_labels(root, dry: bool) -> list[str]:
    have = {lb["name"] for lb in gh_json(root, "label", "list", "--limit", "200", "--json", "name") or []}
    made = []
    for name, (color, desc) in LABELS.items():
        if name not in have:
            made.append(name)
            if not dry:
                gh(root, "label", "create", name, "--color", color, "--description", desc, "--force")
    return made


def plan(specs: dict, done: set, issues: list[dict], repo_url: str, branch: str) -> list[tuple]:
    """Actions as tuples: ('create', id, title, body) | ('retitle', number, title) | ('close', number, id)."""
    actions = []
    for fid in sorted(specs, key=lambda f: int(f[1:]) if f[1:].isdigit() else 0):
        fm = specs[fid]
        title = f"[{fid}] {fm.get('name', '')}".strip()
        match = next((i for i in issues if i["title"].startswith(f"[{fid}]")), None)
        if match is None:
            if fid in done:
                continue  # finished before syncing started: no point opening a closed issue
            deps = ", ".join(as_list(fm.get("depends_on"))) or "none"
            body = (f"Spec: [{fm['_path']}]({repo_url}/blob/{branch}/{fm['_path']})\n\n"
                    f"Depends on: {deps}\n\n"
                    f"The spec is the source of truth; change scope there, discuss here. "
                    f"This closes when `changes/{fid}.md` lands on {branch}.")
            actions.append(("create", fid, title, body))
            continue
        if match["state"].upper() == "OPEN" and fid in done:
            actions.append(("close", match["number"], fid))
        elif match["title"] != title:
            actions.append(("retitle", match["number"], title))
    return actions


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print what would change, change nothing")
    args = ap.parse_args(argv)
    root = root_from(args)
    cfg = load_config(root)
    repo = gh_json(root, "repo", "view", "--json", "url,defaultBranchRef")
    if repo is None:
        print("sync_issues: gh unavailable, not authenticated, or no GitHub remote; nothing synced")
        return 1
    made = ensure_labels(root, args.dry_run)
    issues = gh_json(root, "issue", "list", "--label", "feature", "--state", "all", "--limit", "1000",
                     "--json", "number,title,state") or []
    specs = {fid: fms[0] for fid, fms in load_specs(root, cfg).items() if fid}
    actions = plan(specs, done_ids(root, cfg), issues, repo["url"], repo["defaultBranchRef"]["name"])
    failed = 0
    for a in actions:
        if a[0] == "create":
            cmd = ["issue", "create", "--title", a[2], "--body", a[3], "--label", "feature"]
        elif a[0] == "retitle":
            cmd = ["issue", "edit", str(a[1]), "--title", a[2]]
        else:
            cmd = ["issue", "close", str(a[1]), "--comment", f"Done: `{cfg['paths']['changes']}/{a[2]}.md` is on main."]
        print(f"sync_issues: {'would ' if args.dry_run else ''}{a[0]} {a[1]}")
        if not args.dry_run:
            r = gh(root, *cmd)
            if not r or r.returncode != 0:
                failed += 1
                print(f"sync_issues: failed: {r.stderr.strip() if r else 'no gh'}")
    print(f"sync_issues: {len(specs)} specs, {len(actions)} change(s), {len(made)} label(s) added"
          f"{', ' + str(failed) + ' failed' if failed else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
