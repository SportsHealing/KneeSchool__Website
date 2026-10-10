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
import collections
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

    # Two page ids pointing at the same output file would publish one page and
    # silently lose the other, with every gate still passing: the file exists,
    # it is valid, and nothing knows a second page was meant to be there.
    # Chapter 3.6 came within one slug of this, because its Load Sharing, Shock
    # Absorption and Proprioception pages share their titles with chapter 3.4's
    # and chapter 2.7's. The titles are the architecture's and cannot change,
    # so the slugs carry a prefix and this refuses the mistake rather than
    # trusting it was noticed.
    out_paths = {}
    clashes = []
    for page_id, t in sorted(targets.items()):
        out = t["out"]
        if out in out_paths:
            clashes.append("%s and %s both render to %s"
                           % (out_paths[out], page_id, out))
        out_paths[out] = page_id
    if clashes:
        sys.exit("render targets collide:\n  " + "\n  ".join(clashes))

    if args.only:
        unknown = [p for p in args.only if p not in targets]
        if unknown:
            sys.exit("no render target for: %s" % ", ".join(unknown))
        targets = dict((p, targets[p]) for p in args.only)

    # Chapter 14 requires a unique SEO title per page, and the architecture gives
    # several Section 2 pages the same short title inside different chapters:
    # five pages called Surgical Anatomy, four called Gross Anatomy. The H1 is
    # the architecture's and cannot change, but the title tag is a separate
    # field, so a colliding page carries its chapter name in the title tag. The
    # collision set is computed from the work rather than listed by hand, so a
    # new page that collides is disambiguated the day it is written.
    h1 = {}
    chapters = {}
    for page_id, t in targets.items():
        src_path = os.path.join(ROOT, "pipeline", "runs", page_id,
                                t.get("source", "styled_v1.md"))
        if not os.path.exists(src_path):
            continue
        with open(src_path, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("# "):
                    h1[page_id] = line[2:].strip()
                    break
        brief = os.path.join(ROOT, "pipeline", "config", "briefs", "%s.json" % page_id)
        if os.path.exists(brief):
            with open(brief) as fh:
                chapters[page_id] = json.load(fh)["chapter"]["name"]
    counts = collections.Counter(h1.values())
    seo_titles = {}
    for page_id, title in h1.items():
        if counts[title] > 1 and chapters.get(page_id):
            seo_titles[page_id] = "%s, %s" % (title, chapters[page_id])

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
            if page_id in seo_titles:
                cmd += ["--seo-title", seo_titles[page_id]]
            if t.get("meta_description"):
                cmd += ["--meta-description", t["meta_description"]]
            out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
            if out.returncode:
                sys.stderr.write(out.stdout + out.stderr)
                sys.exit("render failed for %s" % page_id)
            if n == args.passes - 1:
                print("%-8s %s" % (page_id, out.stdout.strip().split(" written, ")[-1]))
    print("%d pages rendered in %d passes" % (len(targets), args.passes))


if __name__ == "__main__":
    main()
