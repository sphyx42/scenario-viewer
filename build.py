#!/usr/bin/env python3
"""Build the scenario viewer from a checkout of the scenarios repo.

Usage:
    python3 build.py --scenarios path/to/scenarios [--out dist/index.html]
                     [--repo matc-ems/scenarios] [--branch main]
                     [--commit SHA] [--pages-url https://matc-ems.github.io/scenarios/]

Reads every <collection>/<scenario>/unified.json (sim-lab and main-lab),
compresses them, and writes one self-contained HTML page. Uses only the
Python standard library.
"""
import argparse
import base64
import datetime
import glob
import gzip
import json
import os
import subprocess
import sys

COLLECTIONS = ("sim-lab", "main-lab")
HERE = os.path.dirname(os.path.abspath(__file__))


def git_commit(path):
    try:
        return subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scenarios", required=True, help="path to a checkout of the scenarios repo")
    ap.add_argument("--out", default=os.path.join(HERE, "dist", "index.html"))
    ap.add_argument("--template", default=os.path.join(HERE, "src", "template.html"))
    ap.add_argument("--repo", default="matc-ems/scenarios", help="owner/name used for GitHub links")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--commit", default=None, help="scenarios commit SHA (read from git if omitted)")
    ap.add_argument("--pages-url", default="", help="GitHub Pages URL of the scenarios repo; adds player/printable links")
    args = ap.parse_args()

    scenarios, problems = [], []
    for col in COLLECTIONS:
        for f in sorted(glob.glob(os.path.join(args.scenarios, col, "*", "unified.json"))):
            folder = os.path.basename(os.path.dirname(f))
            try:
                with open(f, encoding="utf-8") as fh:
                    d = json.load(fh)
                d.setdefault("meta", {})
                d["meta"]["id"] = d["meta"].get("id") or folder
                d.setdefault("patient", {})
                d.setdefault("scene", {})
                d.setdefault("phases", [])
                d["_col"] = col
                scenarios.append(d)
            except Exception as e:  # keep building; report at the end
                problems.append(f"{col}/{folder}: {e}")

    if not scenarios:
        sys.exit(f"No scenarios found under {args.scenarios} (looked in {', '.join(COLLECTIONS)}).")

    raw = json.dumps(scenarios, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    data = base64.b64encode(gzip.compress(raw, 9)).decode("ascii")
    config = {
        "repo": args.repo,
        "branch": args.branch,
        "commit": args.commit if args.commit is not None else git_commit(args.scenarios),
        "pagesUrl": args.pages_url,
        "builtAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }

    with open(args.template, encoding="utf-8") as fh:
        html = fh.read()
    html = html.replace("__CONFIG__", json.dumps(config).replace("</", "<\\/")).replace("__DATA__", data)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)

    counts = {c: sum(1 for s in scenarios if s["_col"] == c) for c in COLLECTIONS}
    print(f"Wrote {args.out}: {len(scenarios)} scenarios ({', '.join(f'{k} {v}' for k, v in counts.items())}), "
          f"{len(html) / 1e6:.1f} MB")
    for p in problems:
        print(f"::warning::Skipped {p}")


if __name__ == "__main__":
    main()
