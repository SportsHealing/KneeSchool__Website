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


def title_budget():
    """Characters available before the site suffix is appended."""
    with open(os.path.join(ROOT, "pipeline", "config", "site.json")) as fh:
        site = json.load(fh)
    return site["seo"]["title_max"] - len(site["title_suffix"])


def disambiguate(title, chapter, budget, peers=()):
    """A colliding page's title tag, with the chapter name trimmed to fit.

    The suffix has a length budget because PUB-001 bounds the whole title tag
    and the renderer appends the site suffix after this, so the fix for chapter
    14's uniqueness rule could break chapter 13's length rule. Chapter 3.12
    found it: "Effects of Malalignment, Tibiofemoral Contact Mechanics |
    KneeSchool" is 68 characters against a bound of 60.

    Which words to drop is the whole problem, and neither end is the answer.
    Dropping from the back loses "Examination" from "Patellofemoral
    Examination", which is the word that separates it from "Patellofemoral
    Biomechanics". Dropping from the front loses "ACL" from "ACL Examination",
    which is the word that separates it from "Rotational Instability
    Examination". Chapter 4.15 produced the first failure and showed the second:
    two pages were given the identical title tag the disambiguation existed to
    separate, and PUB-009 caught it at the gate.

    So the words are ranked by how many of the colliding pages' other chapter
    names contain them, and the most shared word goes first. On a tie the later
    word goes, which keeps the leading word of a name whose words are all
    equally distinguishing. A single remaining word that still does not fit is
    left, so PUB-001 reports it rather than the renderer shipping a mangled
    title.

    The suffix is not always the chapter name. Chapter 5.2 holds two pages
    called Radiation Dose, one under the source's X-ray Physics heading and
    one under its CT Physics heading, and decision 027's flattening left them
    in one chapter with one name between them. The chapter name separates
    nothing there, so the caller passes the navigational grouping instead.
    See suffix_for.
    """
    words = chapter.split()
    shared = collections.Counter()
    for word in words:
        shared[word] = sum(1 for peer in peers if word in peer.split())
    while len(words) > 1 and len("%s, %s" % (title, " ".join(words))) > budget:
        worst = max(range(len(words)), key=lambda i: (shared[words[i]], i))
        words.pop(worst)
    return "%s, %s" % (title, " ".join(words))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="render just these page ids")
    ap.add_argument("--passes", type=int, default=2)
    args = ap.parse_args()

    with open(TARGETS) as fh:
        targets = json.load(fh)["pages"]
    all_targets = dict(targets)

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

    # Chapter 14 requires a unique SEO title per page, and the architecture gives
    # several Section 2 pages the same short title inside different chapters:
    # five pages called Surgical Anatomy, four called Gross Anatomy. The H1 is
    # the architecture's and cannot change, but the title tag is a separate
    # field, so a colliding page carries its chapter name in the title tag. The
    # collision set is computed from the work rather than listed by hand, so a
    # new page that collides is disambiguated the day it is written.
    #
    # The scan below runs over every target, not over the --only subset, and it
    # has to. Chapter 4.15 rendered with --only and published Patellofemoral
    # Arthritis with the same title tag as chapter 3.12's page, because the
    # collision set was computed after --only had narrowed the targets and the
    # other page was not in it. PUB-009 caught it at the gate, which is the
    # backstop working rather than the renderer being right.
    h1 = {}
    chapters = {}
    nav_groups = {}
    for page_id, t in all_targets.items():
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
                chapter = json.load(fh)["chapter"]
            chapters[page_id] = chapter["name"]
            if chapter.get("nav_group"):
                nav_groups[page_id] = chapter["nav_group"]
    # The suffix has a length budget. PUB-001 bounds the whole title tag, and the
    # renderer adds the site suffix after this, so a long chapter name can make
    # the fix for chapter 14's uniqueness rule break chapter 13's length rule.
    # Chapter 3.12 found it: "Effects of Malalignment, Tibiofemoral Contact
    # Mechanics | KneeSchool" is 68 characters against a bound of 60. Trailing
    # words are dropped from the chapter name until it fits, which keeps the
    # distinguishing word and loses the generic one. A chapter name whose first
    # word alone does not fit is left whole, so PUB-001 reports it rather than
    # the renderer shipping a mangled title.
    counts = collections.Counter(h1.values())

    def suffix_for(page_id, title):
        """What to append to a colliding page's title tag.

        The chapter name, unless another page carrying this title sits in the
        same chapter. The chapter name cannot separate those, so the
        navigational grouping the source gave the page is used instead. A page
        with neither is left to collide, and the refusal below reports it.
        """
        chapter = chapters.get(page_id)
        same_chapter = [other for other, t in h1.items()
                        if t == title and other != page_id
                        and chapters.get(other) == chapter]
        if same_chapter and nav_groups.get(page_id):
            return nav_groups[page_id]
        return chapter

    seo_titles = {}
    for page_id, title in h1.items():
        if counts[title] <= 1:
            continue
        suffix = suffix_for(page_id, title)
        if not suffix:
            continue
        peers = [suffix_for(other, t) for other, t in h1.items()
                 if t == title and other != page_id and suffix_for(other, t)]
        seo_titles[page_id] = disambiguate(title, suffix,
                                          title_budget(), peers)
    # Two pages given the same disambiguated title is the failure the
    # disambiguation exists to prevent, so it is refused here rather than left
    # for PUB-009 to find after the files are written.
    still = [t for t, n in collections.Counter(seo_titles.values()).items() if n > 1]
    if still:
        sys.exit("disambiguation did not separate these title tags:\n  "
                 + "\n  ".join(sorted(still)))

    if args.only:
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
