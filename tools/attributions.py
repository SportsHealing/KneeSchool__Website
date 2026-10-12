#!/usr/bin/env python3
"""The attribution register: every study a page hangs on a named author.

    python3 tools/attributions.py --extract              # rebuild from the pages
    python3 tools/attributions.py --report               # the checking list
    python3 tools/attributions.py --report --unchecked   # only the unresolved

Chapter 3.17 is ten pages whose subject is named studies, written by a process
with no access to a paper. Decision 022 sets the terms: the finding and the
surname it is taught under may be written, because they are recalled together
and either one checks the other; the year, the journal, the volume and the page
may not, because they are recalled alone and a wrong one is indistinguishable
from a right one. ATTR-001 enforces the second half.

This register is the first half. It lists, per page, every attribution the page
makes, with the claim attached to it, so a reviewer with a library resolves a
list rather than reading ten pages hunting for names. An entry carries a
verification state and two fields the reviewer fills: the citation as it
actually is, and whether the attribution was right.

Generated from the pages, never compiled by hand, for the reason every other
register on this site is: a hand list falls behind the pages it describes and
nothing reports that it has.
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
REGISTRY = os.path.join(ROOT, "pipeline", "config", "attributions")
FRESH = "UNVERIFIED_FROM_MEMORY"
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
DECADE = re.compile(r"\b(1[89]\d0s|20[0-4]0s)\b")
WITHDRAWN_NOTE = ("No longer on the page; kept so the record of what was "
                  "checked survives.")


def sort_key(page_id):
    return [(0, int(p)) if p.isdigit() else (1, 0, p) for p in str(page_id).split(".")]


def sentences(text):
    for block in text.split("\n\n"):
        if block.strip().startswith("#"):
            continue
        flat = re.sub(r"\s+", " ", block.lstrip("- ")).strip()
        for sent in SENTENCE_END.split(flat):
            if sent.strip():
                yield sent.strip()


def located(doc, name):
    """The tier and body section where the attribution first appears."""
    tier, section = None, None
    best = None
    for i, raw in enumerate(doc.lines, start=1):
        m = re.match(r"^\s{0,3}(#{2,3})\s+(.+?)\s*$", raw)
        if m:
            title = linter.normalise_title(m.group(2))
            if len(m.group(1)) == 2:
                hit = None
                for t, heading in (doc.template.get("tier_headings") or {}).items():
                    if linter.normalise_title(heading) == title:
                        hit = t
                tier, section = hit, None
            else:
                section = m.group(2).strip()
            continue
        if best is None and re.search(
                r"\b%s\b" % re.escape(re.split(r"[,\s]+", name)[0]), raw):
            best = (tier, section)
    return best or (None, None)


def scan(page_id):
    path = os.path.join(RUNS, page_id, "styled_v1.md")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        raw = fh.read()
    template = linter.load_article_template()
    doc = linter.Document(raw, template)
    body = doc.body_text()

    names = linter.attributed_names(body)

    def phrase(name):
        return re.compile(r"\b%s\b" % re.escape(name).replace(r"\ ", r"\s+"))

    found = collections.OrderedDict()
    for name in names:
        # A short name inside a longer one would otherwise collect the longer
        # one's sentences: "Noyes" picked up the decade belonging to "Butler,
        # Noyes and Grood" and reported it as his own.
        supersets = [phrase(o) for o in names
                     if o != name and len(o) > len(name) and name in o]
        # Match the whole name phrase, not its first word. Matching the first
        # word left "Butler, Noyes and Grood" with no claim at all, because the
        # word carries a comma, and it gave Noyes alone a decade that belonged
        # to the three of them together.
        pattern = phrase(name)
        claims, decades = [], []
        for sent in sentences(body):
            if not pattern.search(sent):
                continue
            if any(sup.search(sent) for sup in supersets):
                continue
            claims.append(sent)
            decades += DECADE.findall(sent)
        tier, section = located(doc, name)
        found[name] = collections.OrderedDict([
            ("attributed_to", name),
            ("decade_as_written", sorted(set(decades))),
            ("tier", tier),
            ("section", section),
            ("claim", claims[0][:300] if claims else ""),
            ("further_claims", [c[:300] for c in claims[1:4]]),
            ("occurrences", len(claims)),
            ("verification", FRESH),
            ("citation_as_retrieved", ""),
            ("attribution_correct", ""),
        ])
    return list(found.values())


def merge(page_id, found):
    """Keep what a reviewer has set; add what is new; mark what has gone."""
    path = os.path.join(REGISTRY, "%s.json" % page_id)
    prior = {}
    if os.path.exists(path):
        with open(path) as fh:
            old = json.load(fh)
        for e in old.get("attributions") or []:
            prior[(e.get("attributed_to") or "").strip().lower()] = e

    out, seen = [], set()
    for e in found:
        key = e["attributed_to"].strip().lower()
        seen.add(key)
        was = prior.get(key)
        if was:
            e["verification"] = was.get("verification", FRESH)
            e["citation_as_retrieved"] = was.get("citation_as_retrieved", "")
            e["attribution_correct"] = was.get("attribution_correct", "")
            if was.get("note"):
                e["note"] = was["note"]
        out.append(e)
    for key, was in prior.items():
        if key in seen:
            continue
        was["verification"] = "REMOVED"
        note = (was.get("note") or "").strip()
        # the same idempotency bug positions.py had: concatenating this note on
        # every extraction made a clean checkout go dirty on every run
        if WITHDRAWN_NOTE not in note:
            was["note"] = (note + " " + WITHDRAWN_NOTE).strip()
        out.append(was)
    return out


def write(page_id, attributions):
    with open(os.path.join(BRIEFS, "%s.json" % page_id)) as fh:
        brief = json.load(fh)
    body = collections.OrderedDict([
        ("register_version", "1.0"),
        ("page_id", page_id),
        ("title", brief["title"]),
        ("source_of_truth",
         "docs/decisions/022-landmark-papers-without-source-access.md"),
        ("note", "Generated by tools/attributions.py --extract from the page itself. "
                 "Fill verification, citation_as_retrieved and attribution_correct; "
                 "everything else is rewritten on the next extraction. An attribution "
                 "that leaves the page is marked REMOVED rather than deleted, so the "
                 "record of what was checked survives the edit."),
        ("attributions", attributions),
    ])
    if not os.path.isdir(REGISTRY):
        os.makedirs(REGISTRY)
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
        brief_path = os.path.join(BRIEFS, "%s.json" % page_id)
        if not os.path.exists(brief_path):
            continue
        with open(brief_path) as fh:
            brief = json.load(fh)
        # scoped to the page type whose subject is named studies; every other
        # page on the site names no author and would register an empty list
        if brief.get("page_type") != "landmark_papers":
            continue
        found = scan(page_id)
        if found is None:
            continue
        if not found and not os.path.exists(os.path.join(REGISTRY, "%s.json" % page_id)):
            continue
        attributions = merge(page_id, found)
        write(page_id, attributions)
        live = [a for a in attributions if a["verification"] != "REMOVED"]
        total += len(live)
        pages += 1
        print("%-9s %2d attribution(s)" % (page_id, len(live)))
    print("%d attributions registered across %d pages" % (total, pages))


def cmd_report(unchecked_only):
    rows, counts = [], collections.Counter()
    if not os.path.isdir(REGISTRY):
        print("no attribution register yet")
        return
    for name in sorted(os.listdir(REGISTRY), key=lambda n: sort_key(n[:-5])):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(REGISTRY, name)) as fh:
            reg = json.load(fh)
        for a in reg.get("attributions") or []:
            counts[a["verification"]] += 1
            if unchecked_only and a["verification"] != FRESH:
                continue
            rows.append((reg["page_id"], reg["title"], a))
    page = None
    for page_id, title, a in rows:
        if page_id != page:
            print("\n%s  %s" % (page_id, title))
            page = page_id
        print("  %-22s %-10s %s" % (a["attributed_to"],
                                    ", ".join(a.get("decade_as_written") or []),
                                    a["claim"][:88]))
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
