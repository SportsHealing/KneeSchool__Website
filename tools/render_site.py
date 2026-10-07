#!/usr/bin/env python3
"""Render every pipeline page listed in render_targets.json.

    python3 tools/render_site.py
    python3 tools/render_site.py --only 0.3.1 0.3.2

Two passes, deliberately. A cross link can only resolve once the page it points
at is in the published page index, and on a first build nothing is in it yet.
Pass one writes every page and registers it; pass two rewrites them with every
link now resolvable. Rendering is deterministic, so a second pass over an
unchanged site changes nothing.
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = os.path.join(ROOT, "pipeline", "config", "render_targets.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="render just these page ids")
    ap.add_argument("--passes", type=int, default=2)
    args = ap.parse_args()

    with open(TARGETS) as fh:
        targets = json.load(fh)["pages"]
    if args.only:
        unknown = [p for p in args.only if p not in targets]
        if unknown:
            sys.exit("no render target for: %s" % ", ".join(unknown))
        targets = dict((p, targets[p]) for p in args.only)

    missing = []
    for page_id, t in targets.items():
        src = os.path.join(ROOT, "pipeline", "runs", page_id, t.get("source", "styled_v1.md"))
        if not os.path.exists(src):
            missing.append(page_id)
    if missing:
        sys.exit("no styled markdown for: %s" % ", ".join(missing))

    for n in range(args.passes):
        for page_id, t in targets.items():
            src = os.path.join(ROOT, "pipeline", "runs", page_id,
                               t.get("source", "styled_v1.md"))
            cmd = [sys.executable, os.path.join(ROOT, "tools", "render_article.py"), src,
                   "--brief", os.path.join(ROOT, "pipeline", "config", "briefs",
                                           "%s.json" % page_id),
                   "--out", os.path.join(ROOT, t["out"]),
                   "--parent", t["parent"], "--status", t["status"], "--register"]
            out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
            if out.returncode:
                sys.stderr.write(out.stdout + out.stderr)
                sys.exit("render failed for %s" % page_id)
            if n == args.passes - 1:
                print("%-8s %s" % (page_id, out.stdout.strip().split(" written, ")[-1]))
    print("%d pages rendered in %d passes" % (len(targets), args.passes))


if __name__ == "__main__":
    main()
