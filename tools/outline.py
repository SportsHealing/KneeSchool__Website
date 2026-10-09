#!/usr/bin/env python3
"""Query the Sections 1 to 15 outline.

    python3 tools/outline.py --summary
    python3 tools/outline.py --section 7
    python3 tools/outline.py --gaps
    python3 tools/outline.py --find "root repair"

The outline is titles only. It answers what exists and what it is called, which
is what planning needs. It cannot answer what a page must cover or must leave to
another page, and tools/architecture.py will not generate a brief from it. See
docs/findings/001-sections-1-to-15-architecture.md.
"""

import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTLINE = os.path.join(ROOT, "pipeline", "config", "architecture", "outline_1_to_15.json")
CONVENTIONS = os.path.join(ROOT, "pipeline", "config", "section_conventions.json")
PAGE_MAP = os.path.join(ROOT, "pipeline", "config", "architecture", "pages_0_to_3.json")


def load():
    with open(OUTLINE) as fh:
        doc = json.load(fh)
    with open(CONVENTIONS) as fh:
        conv = json.load(fh)["sections"]
    with open(PAGE_MAP) as fh:
        mapped = set(str(p["page_id"]) for p in json.load(fh))
    return doc, conv, mapped


def key(page_id):
    return [(0, int(p)) if p.isdigit() else (1, 0, p) for p in str(page_id).split(".")]


def cmd_summary(doc, conv, mapped):
    print("%-4s %-40s %9s %8s %8s %7s %7s"
          % ("sec", "name", "chapters", "enum'd", "pages", "briefed", "tiers"))
    tp = tc = tb = 0
    for sid in sorted(conv, key=int):
        s = conv[sid]
        pages = [p for p in doc["pages"] if p["section"]["id"] == sid]
        briefed = sum(1 for p in pages if p["page_id"] in mapped)
        tp += len(pages); tc += s["chapters"]; tb += briefed
        print("%-4s %-40s %9d %8d %8d %7d %7s"
              % (sid, s["name"][:40], s["chapters"], s["chapters_enumerated_to_pages"],
                 len(pages), briefed, len(s.get("tiers_declared") or []) or "-"))
    print("%-4s %-40s %9d %8s %8d %7d" % ("", "TOTAL", tc, "", tp, tb))
    print("\n%d pages are in the full page map and can be briefed." % tb)
    print("%d pages are outline only: title, chapter and part, nothing else." % (tp - tb))
    print("%d chapters carry no enumerated pages at all." % sum(
        len(conv[s]["chapters_without_pages"]) for s in conv))


def cmd_section(doc, conv, mapped, sid):
    s = conv.get(sid)
    if not s:
        sys.exit("no section %s in the outline" % sid)
    print("SECTION %s: %s" % (sid, s["name"]))
    for g in s.get("declared") or []:
        print("\n  %s (%s)" % (g["trigger"], g["kind"]))
        for item in g["items"]:
            print("    - %s" % item)
    pages = sorted((p for p in doc["pages"] if p["section"]["id"] == sid),
                   key=lambda p: key(p["page_id"]))
    chapter = None
    print()
    for p in pages:
        if p["chapter"]["id"] != chapter:
            chapter = p["chapter"]["id"]
            part = (p.get("part") or {}).get("name")
            print("  Chapter %s %s%s" % (chapter, p["chapter"]["name"],
                                         "   [part %s]" % part if part else ""))
        flag = " *" if p["page_id"] in mapped else "  "
        print("   %s %-9s %s" % (flag, p["page_id"], p["title"]))
    empty = s["chapters_without_pages"]
    if empty:
        print("\n  %d chapter(s) with no pages enumerated:" % len(empty))
        names = dict((c["chapter_id"], c["name"]) for c in doc["chapters"])
        for cid in empty:
            print("     %-8s %s" % (cid, names.get(cid, "")))


def cmd_gaps(doc, conv, mapped):
    names = dict((c["chapter_id"], c["name"]) for c in doc["chapters"])
    total = 0
    for sid in sorted(conv, key=int):
        empty = conv[sid]["chapters_without_pages"]
        if not empty:
            continue
        total += len(empty)
        print("SECTION %s %s: %d chapter(s) without pages"
              % (sid, conv[sid]["name"], len(empty)))
        for cid in empty:
            print("   %-8s %s" % (cid, names.get(cid, "")))
    print("\n%d chapters need their pages enumerating before they can be planned." % total)


def cmd_find(doc, conv, mapped, needle):
    n = needle.lower()
    hits = [p for p in doc["pages"] if n in p["title"].lower()]
    for p in sorted(hits, key=lambda p: key(p["page_id"])):
        flag = "*" if p["page_id"] in mapped else " "
        print("%s %-9s %-44s  %s / %s"
              % (flag, p["page_id"], p["title"], p["section"]["name"],
                 p["chapter"]["name"]))
    ch = [c for c in doc["chapters"] if n in c["name"].lower()]
    for c in sorted(ch, key=lambda c: key(c["chapter_id"])):
        print("  chapter %-7s %-42s  %s" % (c["chapter_id"], c["name"],
                                            c["section"]["name"]))
    print("\n%d page(s) and %d chapter(s) match %r" % (len(hits), len(ch), needle))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--section")
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--find")
    args = ap.parse_args()
    doc, conv, mapped = load()
    if args.section:
        cmd_section(doc, conv, mapped, args.section)
    elif args.gaps:
        cmd_gaps(doc, conv, mapped)
    elif args.find:
        cmd_find(doc, conv, mapped, args.find)
    else:
        cmd_summary(doc, conv, mapped)


if __name__ == "__main__":
    main()
