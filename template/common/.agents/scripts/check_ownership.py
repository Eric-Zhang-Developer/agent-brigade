#!/usr/bin/env python3
"""Ownership gate: fail a PR that touches files outside what its title allows.

  check_ownership.py --lint-specs                       specs are consistent (ids, deps, owns overlap)
  check_ownership.py --title "[F05] Map" --base origin/main   every changed file is allowed for that title

Title rules are in core/docs/config.md ("PR titles").
"""

import sys

from kitlib import as_list, changed_files, git_lines, load_config, load_specs, parse_title, parser, root_from


def lint_specs(cfg: dict, features: dict[str, list[dict]]) -> list[str]:
    errors = []
    frozen = as_list(cfg["ownership"]["frozen"])
    for fid, fms in features.items():
        if not fid:
            errors += [f"{fm['_path']}: missing id" for fm in fms]
        elif len(fms) > 1:
            errors.append(f"duplicate id {fid}: " + ", ".join(fm["_path"] for fm in fms))
    specs = {fid: fms[0] for fid, fms in features.items() if fid}
    if sum(1 for fm in specs.values() if fm.get("bootstrap") is True) > 1:
        errors.append("more than one feature has bootstrap: true")
    for fid, fm in specs.items():
        for dep in as_list(fm.get("depends_on")):
            if dep not in specs:
                errors.append(f"{fid}: depends_on {dep} does not exist")
        if fm.get("cut") not in (None, "ok", "never"):
            errors.append(f"{fid}: cut must be ok or never, not {fm.get('cut')!r}")
    entries = [(fid, e) for fid, fm in specs.items() for e in as_list(fm.get("owns"))]
    for i, (fid, e) in enumerate(entries):
        for other, o in entries[i + 1:]:
            if other != fid and (o.startswith(e) or e.startswith(o)):
                errors.append(f"{fid} owns {e!r}, which overlaps {other}'s {o!r}")
        for f in frozen:
            if f.startswith(e) or e.startswith(f):
                errors.append(f"{fid} owns {e!r}, which overlaps frozen path {f!r}")
    return sorted(set(errors))


def allowed(title: str, cfg: dict, features: dict, revert_files=None):
    """(predicate(path) -> bool, description). Raises ValueError for an unusable title."""
    t = parse_title(title)
    if t is None:
        raise ValueError(f"title {title!r} has no known prefix: [F<n>] [FIX-F<n>] [C<n>] [PLAN] [REVERT-<sha>]")
    specs, changes = cfg["paths"]["specs"].rstrip("/"), cfg["paths"]["changes"].rstrip("/")
    open_paths = as_list(cfg["ownership"]["open"])
    if t["kind"] == "contract":
        prefixes = as_list(cfg["ownership"]["frozen"]) + [f"{specs}/"] + open_paths
    elif t["kind"] == "plan":
        prefixes = [f"{specs}/features/", f"{specs}/roadmap.md", f"{specs}/inbox/"]
    elif t["kind"] == "revert":
        files = set(revert_files or [])
        return (lambda p: p in files), f"revert of {t['sha']}: {sorted(files)}"
    else:
        fid = t["id"]
        if fid not in features:
            raise ValueError(f"unknown feature {fid}")
        fm = features[fid][0]
        if fm.get("bootstrap") is True:
            return (lambda p: True), f"{fid} is bootstrap: anything"
        prefixes = as_list(fm.get("owns")) + open_paths + [
            f"{changes}/{fid}.md", f"{specs}/features/{fid}-", f"{specs}/decisions/{fid}-", f"{specs}/inbox/{fid}-",
        ]
    return (lambda p: any(p.startswith(x) for x in prefixes)), f"{prefixes}"


def main(argv=None) -> int:
    ap = parser(__doc__)
    ap.add_argument("--lint-specs", action="store_true", help="check spec front matter")
    ap.add_argument("--title", help="PR title to check the diff against")
    ap.add_argument("--base", default="origin/main", help="base ref for the diff (default origin/main)")
    args = ap.parse_args(argv)
    if not args.lint_specs and args.title is None:
        ap.print_help()
        return 2
    root = root_from(args)
    cfg = load_config(root)
    features = load_specs(root, cfg)
    rc = 0
    if args.lint_specs:
        errs = lint_specs(cfg, features)
        for e in errs:
            print(f"spec lint: {e}")
        print(f"spec lint: {len(features)} features, {'FAIL' if errs else 'ok'}")
        rc |= bool(errs)
    if args.title is not None:
        t = parse_title(args.title)
        revert_files = git_lines(root, "show", "--name-only", "--format=", t["sha"]) if t and t["sha"] else None
        try:
            ok, desc = allowed(args.title, cfg, features, revert_files)
        except ValueError as e:
            print(f"ownership: {e}")
            return 1
        files = changed_files(root, args.base)
        bad = [f for f in files if not ok(f)]
        for f in bad:
            print(f"ownership: {f} is outside what {args.title!r} may change")
        print(f"ownership: {len(files)} changed files, allowed {desc}: {'FAIL' if bad else 'ok'}")
        rc |= bool(bad)
    return rc


if __name__ == "__main__":
    sys.exit(main())
