#!/usr/bin/env python3
"""Check every cross link on every draft against the architecture.

    python3 tools/crossrefs.py --check

A cross link is written as [[page_id | label]]. Both halves can be wrong
independently, and both failures are invisible on the rendered page: a wrong
page_id sends the reader somewhere else, and a wrong label tells them the page is
about something it is not. Neither shows up in a spell check or in the style gate.

The architecture owns every page_id and every title, so it is the only thing worth
checking against. Labels are compared loosely, because a cross link legitimately
shortens a long title, but a label that shares no significant word with the real
title is reported.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH_DIR = os.path.join(ROOT, "pipeline", "config", "architecture")
RUNS = os.path.join(ROOT, "pipeline", "runs")
LINK = re.compile(r"\[\[([^|\]]+)\|([^\]]+)\]\]")
# A reference written into the prose, as "0.1.2 Bones, Ligaments, Menisci and
# Muscles covers ...". The page id and the title can disagree here exactly as
# they can in a cross link, and nothing else looks at them.
PROSE = re.compile(r"\b(\d+\.\d+\.\d+)\s+"
                   r"([A-Z][\w'-]*(?:[ ,]+(?:and|the|a|of|to|for|in|on|that|"
                   r"[A-Z][\w'-]*))*)")
# Sections beyond 3 are not published yet. A forward link to one is written with
# an x for the chapter, and that is deliberate rather than a typing error.
PLACEHOLDER = re.compile(r"^\d+\.x$")
STOP = set("the a an and of or in to for on at is are be with your you it its as "
           "from by what how why when".split())


def titles():
    """page_id to title, and chapter_id to chapter name.

    Two sources. pages_*.json is the full page map for sections 0 to 3. The
    outline added on 9 October 2026 covers sections 1 to 15 with titles only,
    and it is loaded here precisely because it is titles: a forward link to
    section 7 could not be checked against anything before it arrived.

    Chapter ids go in the same map, because this site's prose links to a chapter
    as often as to a page: "3.13 takes that further", "7.20 owns the technique".
    """
    out = {}
    for name in sorted(os.listdir(ARCH_DIR)):
        path = os.path.join(ARCH_DIR, name)
        if name.startswith("pages_") and name.endswith(".json"):
            with open(path) as fh:
                pages = json.load(fh)
        elif name.startswith("outline_") and name.endswith(".json"):
            with open(path) as fh:
                doc = json.load(fh)
            pages = doc.get("pages") or []
            # chapters are carried separately because 775 of them have no pages,
            # and a link to one of those is still a link worth checking
            for chapter in doc.get("chapters") or []:
                out.setdefault(str(chapter["chapter_id"]), chapter["name"])
        else:
            continue
        for page in pages:
            # a page map entry wins over an outline entry, because it is richer
            out.setdefault(str(page["page_id"]), page["title"])
            chapter = page.get("chapter") or {}
            if chapter.get("id") and chapter.get("name"):
                out.setdefault(str(chapter["id"]), chapter["name"])
    return out


def words(text):
    return set(w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP)


# A bare reference in prose, outside a cross link block. Its id can be perfectly
# valid and still point at the wrong chapter: "4.9 covers the examination" on a
# posterior cruciate page named a real chapter, Meniscal Examination, and nothing
# caught it because nothing was broken. Seven such references were wrong across
# three chapters before this report existed. A machine cannot know what a writer
# meant, so this prints what each reference actually resolves to and leaves the
# judgement to a reader. Generated from the pages, like every other register here.
BARE_REF = re.compile(r"(?<![\w.])(\d{1,2}(?:\.\d{1,3}){1,2})(?![\w.])")

# Chapter 3.4 was the first chapter to quote a bare decimal in prose, and the
# detector read "roughly 1.0 to 1.2 times body weight" as references to chapter
# 1.0 and chapter 1.2. One of those does not exist and the other is a real page,
# which is the worse case: a silent false match on a number that was never a
# reference.
#
# What separates the two is the unit, not the decimal point. "1.0 to 1.2 times
# body weight" ends in a unit; "3.7 and 3.8 cover the cruciates" ends in prose.
# Both are chains of numbers joined by "to" or "and", so a chain is classified
# once as a whole and every number in it is kept or dropped together. Testing
# each number on its own was tried first and suppressed 156 real references,
# because the second id in "3.7 and 3.8" looks exactly like the second number in
# a range.
NUMBER_RUN = re.compile(
    r"(?<![\w.])\d{1,2}(?:\.\d{1,3}){0,2}"
    r"(?:\s*(?:to|and|or|,)\s*\d{1,2}(?:\.\d{1,3}){0,2})*")
UNIT_AFTER = re.compile(
    r"^\s*(?:times|x|mm|cm|metres|m|kg|N|Nm|degrees?|per\s+cent|%|body\s+weight"
    r"|seconds?|ms|minutes?|hours?|years?|months?|weeks?|days?|fold)\b", re.I)


DEEPER_ID = re.compile(r"^\.\d")


def reference_spans(text):
    """Every bare reference in the prose, with the measurements left out.

    Scanning inside the run rather than across the whole text also fixed a
    pre-existing miss: the old pattern refused a reference followed by a full
    stop, so every reference that ended a sentence went unchecked. There were 56
    of them. The one thing that lookahead did protect against is kept here, which
    is a four part id such as 5.3.1.1 being reported as its first three parts.
    """
    out = []
    for run in NUMBER_RUN.finditer(text):
        if UNIT_AFTER.match(text[run.end():run.end() + 40]):
            continue
        for m in BARE_REF.finditer(run.group(0)):
            begin = run.start() + m.start()
            finish = run.start() + m.end()
            if DEEPER_ID.match(text[finish:finish + 2]):
                continue
            out.append((begin, finish, m.group(1)))
    return out


def report(runs, known, listing=True):
    """List every bare prose reference, or with listing=False count only.

    Returns the number pointing at an id the architecture does not have, so the
    caller can make it an exit code. It used to print that number and exit zero,
    which meant the one check that catches a reference to a page that does not
    exist could not fail a build. See decision 021.
    """
    rows = []
    for page_id in sorted(os.listdir(runs), key=page_sort_key):
        draft = os.path.join(runs, page_id, "draft_v1.md")
        if not os.path.exists(draft):
            continue
        with open(draft) as fh:
            text = LINK.sub("", fh.read())
        for begin, finish, ref in reference_spans(text):
            context = re.sub(r"\s+", " ", text[begin:finish + 60]).strip()
            rows.append((page_id, ref, known.get(ref, "NOT IN THE ARCHITECTURE"), context))
    missing = [r for r in rows if r[2] == "NOT IN THE ARCHITECTURE"]
    if listing:
        current = None
        for page_id, ref, title, context in rows:
            if page_id != current:
                print("")
                print(page_id)
                current = page_id
            print("  %-8s %-34s %s" % (ref, title[:34], context[:58]))
        print("")
    else:
        for page_id, ref, title, context in missing:
            print("%-9s -> %-9s %s" % (page_id, ref, context[:58]))
    print("%d bare references in prose across %d pages"
          % (len(rows), len(set(r[0] for r in rows))))
    print("%d point at an id the architecture does not have" % len(missing))
    return len(missing)


def page_sort_key(page_id):
    try:
        return tuple(int(n) for n in page_id.split("."))
    except ValueError:
        return (999,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non zero if any cross link is wrong")
    ap.add_argument("--runs", default=RUNS)
    ap.add_argument("--prose-report", action="store_true",
                    help="list every bare chapter or page reference in prose with the title "
                         "it resolves to, so a valid id pointing at the wrong chapter is "
                         "visible rather than hunted for")
    ap.add_argument("--prose-check", action="store_true",
                    help="count the same references and exit non zero if any points at an "
                         "id the architecture does not have, without the full listing")
    args = ap.parse_args()

    known = titles()
    problems = []
    checked = 0
    for page_id in sorted(os.listdir(args.runs)):
        draft = os.path.join(args.runs, page_id, "draft_v1.md")
        if not os.path.exists(draft):
            continue
        with open(draft) as fh:
            text = fh.read()
        seen = {}
        for m in LINK.finditer(text):
            pid, label = m.group(1).strip(), m.group(2).strip()
            checked += 1
            # The same page twice in one cross link block is a merge artefact. It
            # renders as two rows pointing at one place, which reads as an error
            # to anyone who follows both. A section placeholder is exempt: two
            # future pages in the same unpublished section share one id.
            if pid in seen and not PLACEHOLDER.match(pid):
                problems.append((page_id, pid, label,
                                 "already linked on this page as %r" % seen[pid]))
            seen[pid] = label
            if pid not in known:
                # Pages beyond section 3 are not in the architecture file yet. A
                # forward link to one is expected, so only a malformed id is a
                # fault.
                if not (re.match(r"^\d+(\.\d+)*$", pid)
                        or PLACEHOLDER.match(pid)):
                    problems.append((page_id, pid, label, "page_id is not a page_id"))
                continue
            real = known[pid]
            if words(label) & words(real):
                continue
            problems.append((page_id, pid, label, "label does not match %r" % real))
        for m in PROSE.finditer(text):
            pid, phrase = m.group(1), m.group(2).strip()
            if pid not in known:
                continue
            checked += 1
            # Only a phrase long enough to be a title claim is worth testing. A
            # sentence that merely ends with the id, then starts a new one, is not.
            if len(phrase.split()) < 2:
                continue
            real = known[pid]
            if words(phrase) & words(real):
                continue
            problems.append((page_id, pid, phrase, "prose names %r for this id" % real))

    if args.prose_report or args.prose_check:
        missing = report(args.runs, known, listing=args.prose_report)
        if args.prose_check and missing:
            sys.exit(1)
        return

    for src, pid, label, why in problems:
        print("%-7s -> [[%s | %s]]  %s" % (src, pid, label, why))
    print("%d cross links checked, %d wrong" % (checked, len(problems)))
    if args.check and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
