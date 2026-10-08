#!/usr/bin/env python3
"""The figure register: every measurement on a page, and whether anyone has checked it.

    python3 tools/figures.py --extract            # rebuild registers from the pages
    python3 tools/figures.py --report             # the checking list, grouped by page
    python3 tools/figures.py --report --unchecked # only the ones still unverified

The client's instruction was to keep the measurements and check them. This
environment has no source access, so every figure on the site is written from
standard teaching and none is attributable to a paper. What makes that
survivable is that the checking list is generated from the pages rather than
compiled by hand, so it cannot fall behind them.

A register entry records the figure as written, the sentence it supports, the
tier and section it sits in, how many times it appears on the page, a
verification state and a source field for the reviewer to fill. Extraction never overwrites a state or a source that somebody
has already set; it adds new figures and marks vanished ones REMOVED.

A range is one figure. "20 to 30 degrees" registers as that, not as a bare 20
and a 30 degrees, because a lone bound tells a reviewer nothing.
"""

import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline", "functions", "style_lint"))
import linter  # noqa: E402

RUNS = os.path.join(ROOT, "pipeline", "runs")
BRIEFS = os.path.join(ROOT, "pipeline", "config", "briefs")
REGISTRY = os.path.join(ROOT, "pipeline", "config", "figures")
FRESH = "UNVERIFIED_FROM_MEMORY"
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def sort_key(page_id):
    return [(0, int(p)) if p.isdigit() else (1, 0, p) for p in str(page_id).split(".")]


def sentence_around(text, start):
    """The sentence a figure sits in. That sentence is the claim being made."""
    head = text.rfind("\n\n", 0, start)
    tail = text.find("\n\n", start)
    block = text[(head + 2 if head >= 0 else 0): (tail if tail >= 0 else len(text))]
    offset = start - (head + 2 if head >= 0 else 0)
    pos = 0
    for part in SENTENCE_END.split(block):
        if pos <= offset < pos + len(part) + 1:
            return re.sub(r"\s+", " ", part).strip()
        pos += len(part) + 1
    return re.sub(r"\s+", " ", block).strip()[:300]


def located(doc, start, text):
    """Which tier and which body section the figure sits in, by line number."""
    line = linter.line_of(text, start)
    tier, section = None, None
    for i, raw in enumerate(doc.lines[:line], start=1):
        m = re.match(r"^\s{0,3}(#{2,3})\s+(.+?)\s*$", raw)
        if not m:
            continue
        title = linter.normalise_title(m.group(2))
        if len(m.group(1)) == 2:
            for t, heading in (doc.template.get("tier_headings") or {}).items():
                if linter.normalise_title(heading) == title:
                    tier, section = t, None
        else:
            section = m.group(2).strip()
    return tier, section


def scan(page_id):
    path = os.path.join(RUNS, page_id, "styled_v1.md")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        raw = fh.read()
    template = linter.load_article_template()
    doc = linter.Document(raw, template)
    rules = linter.load_rules()
    rule = next((r for r in rules["rules"] if r["id"] == "FIG-002"), {})
    # One row per distinct figure, not one per occurrence. A figure quoted in the
    # body and repeated in a key learning point is one thing to check.
    found = collections.OrderedDict()
    for token, start, end, text in linter.body_figures(doc, rule):
        key = linter.normalise_figure(token)
        if key in found:
            found[key]["occurrences"] += 1
            continue
        tier, section = located(doc, start, text)
        found[key] = collections.OrderedDict([
            ("as_written", token),
            ("tier", tier),
            ("section", section),
            ("claim", sentence_around(text, start)),
            ("occurrences", 1),
            ("verification", FRESH),
            ("source", ""),
        ])
    return list(found.values())


def merge(page_id, found):
    """Keep what a reviewer has set; add what is new; mark what has gone."""
    path = os.path.join(REGISTRY, "%s.json" % page_id)
    prior = {}
    if os.path.exists(path):
        with open(path) as fh:
            old = json.load(fh)
        for e in old.get("figures") or []:
            prior[linter.normalise_figure(e.get("as_written", ""))] = e

    out, seen = [], set()
    for e in found:
        key = linter.normalise_figure(e["as_written"])
        seen.add(key)
        was = prior.get(key)
        if was:
            # the sentence can change without the figure changing; the reviewer's
            # verdict and source are theirs and are never overwritten
            e["verification"] = was.get("verification", FRESH)
            e["source"] = was.get("source", "")
            if was.get("note"):
                e["note"] = was["note"]
        out.append(e)
    for key, was in prior.items():
        if key in seen:
            continue
        was["verification"] = "REMOVED"
        was.setdefault("note", "")
        was["note"] = (was["note"] + " " if was["note"] else "") + \
            "No longer on the page; kept so the record of what was checked survives."
        out.append(was)
    return out


def write(page_id, figures):
    with open(os.path.join(BRIEFS, "%s.json" % page_id)) as fh:
        brief = json.load(fh)
    body = collections.OrderedDict([
        ("register_version", "1.0"),
        ("page_id", page_id),
        ("title", brief["title"]),
        ("source_of_truth", "docs/decisions/006-keep-the-measurements.md"),
        ("note", "Generated by tools/figures.py --extract from the page itself. Edit the "
                 "verification and source fields; everything else is rewritten on the next "
                 "extraction. A figure the reviewer corrects or deletes is marked REMOVED "
                 "rather than removed from this file."),
        ("figures", figures),
    ])
    path = os.path.join(REGISTRY, "%s.json" % page_id)
    with open(path, "w") as fh:
        fh.write(json.dumps(body, indent=2) + "\n")
    return path


def page_ids():
    return sorted((d for d in os.listdir(RUNS)
                   if os.path.isdir(os.path.join(RUNS, d))), key=sort_key)


def cmd_extract():
    total, pages = 0, 0
    for page_id in page_ids():
        found = scan(page_id)
        if found is None:
            continue
        with open(os.path.join(BRIEFS, "%s.json" % page_id)) as fh:
            brief = json.load(fh)
        if not (brief.get("governance") or {}).get("figures_allowed"):
            continue
        if not found and not os.path.exists(os.path.join(REGISTRY, "%s.json" % page_id)):
            continue
        figures = merge(page_id, found)
        write(page_id, figures)
        live = [f for f in figures if f["verification"] != "REMOVED"]
        total += len(live)
        pages += 1
        print("%-7s %2d figure(s)" % (page_id, len(live)))
    print("%d figures registered across %d pages" % (total, pages))


def cmd_report(unchecked_only):
    rows, counts = [], collections.Counter()
    for name in sorted(os.listdir(REGISTRY), key=lambda n: sort_key(n[:-5])):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(REGISTRY, name)) as fh:
            reg = json.load(fh)
        for f in reg.get("figures") or []:
            counts[f["verification"]] += 1
            if unchecked_only and f["verification"] != FRESH:
                continue
            rows.append((reg["page_id"], reg["title"], f))
    page = None
    for page_id, title, f in rows:
        if page_id != page:
            print("\n%s  %s" % (page_id, title))
            page = page_id
        print("  %-12s %-16s %s" % (f["as_written"], f.get("tier") or "", f["claim"][:96]))
    print()
    for state, n in sorted(counts.items()):
        print("%-24s %d" % (state, n))
    print("%-24s %d" % ("total", sum(counts.values())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--unchecked", action="store_true")
    args = ap.parse_args()
    if args.extract:
        cmd_extract()
    if args.report or not args.extract:
        cmd_report(args.unchecked)


if __name__ == "__main__":
    main()
