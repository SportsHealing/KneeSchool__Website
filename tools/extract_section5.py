#!/usr/bin/env python3
"""Build pipeline/config/architecture/pages_5.json from the source architecture.

Section 5 is in the same position Section 4 was in under decision 024. Part 1
governs tier coverage and page scope, and it gives Section 5 one sentence: an
estimate of 250 to 350 pages and a list of chapter headings. Part 2, which would
carry the real page map, is not in this repository. So the map is built here,
from the source document and from Part 1's own boundaries, rather than by hand.

Two things this script fixes that the outline file got wrong.

The outline recorded chapters 5.2 to 5.5 as four, four, five and two pages. Those
chapters are organised as navigational sub sections, "Section 5.2.1 X-ray
Physics", with the real pages one level below as 5.2.1.1 to 5.2.1.5. The outline
took the sub section headings as pages and dropped the 78 leaves beneath them.
Part 1's numbering convention says navigational groupings never appear in page
ids, which is the same ruling decision 024 applied to chapter 4.2, so those
leaves are renumbered flat within their chapter and the 15 headings become no
page at all.

That moves Section 5 from the outline's 161 pages to 224, which also sits inside
Part 1's own estimate where 161 did not.

Everything this script cannot derive is named in decision 027 rather than
guessed quietly. The weakest of them is the tier set: Part 1's Section 4
sentence said "Examination for Medical Student to Fellowship tiers" and decision
024 had that to lean on, while Part 1's Section 5 sentence says nothing about
tiers at all.
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "docs",
                   "KneeSchool_Sections_1_to_15_Full_Architecture.txt")
PART1 = os.path.join(ROOT, "docs",
                     "KneeSchool_Master_Publishing_Architecture_Part1.md")
OUT = os.path.join(ROOT, "pipeline", "config", "architecture", "pages_5.json")

SECTION = {"id": "5", "name": "Imaging Academy"}

# Decision 027. Part 1 states no tier set for Section 5. Every page in the
# architecture that defers to Section 5 does so from a professional tier: the
# Section 2 chapters that exclude "Imaging interpretation beyond normal anatomy
# (owned by Section 5)" run medical_student to frcs, and Section 4, which defers
# its imaging the same way, runs medical_student to fellowship. This mirrors
# Section 4 and is an editorial default awaiting Editor in Chief sign off, which
# is what Part 1 section 3 says every tier set in Part 1 is.
TIERS = ["medical_student", "mrcs", "frcs", "fellowship"]

# Part 1's authority boundaries, inverted for an imaging section. Section 5 owns
# acquisition and interpretation; these name the owners of what an imaging page
# would otherwise drift into.
BASE_MNC = [
    "Clinical examination technique and interpretation (owned by Section 4)",
    "Clinical management and treatment selection (owned by Section 6)",
    "Operative technique (owned by Section 7)",
    "Structure level anatomy beyond what the image shows (owned by Section 2)",
    "Biomechanics beyond what the appearance depends on (owned by Section 3)",
]

def own_chapters(chapter):
    """The in-section boundary, which differs by what the chapter is for.

    The first version put "Per modality and per structure appearance (owned per
    page by 5.2 to 5.20)" on every page, which is correct on the introduction
    chapter and self excluding everywhere else: page 5.6.1 Normal Meniscus is
    one of the pages that line points at.
    """
    if chapter == "5.1":
        return ("Per modality and per structure appearance "
                "(owned per page by 5.2 to 5.20)")
    if chapter == "5.21":
        return ("Current imaging technique and interpretation "
                "(owned by 5.1 to 5.20)")
    return ("Appearance on another modality or of another structure "
            "(owned per chapter by 5.2 to 5.20)")


CHAPTER = re.compile(r"^Chapter (5\.\d+)\s+(.+?)\s*$")
NAV = re.compile(r"^Section (5\.\d+\.\d+)\s+(.+?)\s*$")
LEAF = re.compile(r"^(5\.\d+\.\d+(?:\.\d+)?)\s+(.+?)\s*$")
START = "SECTION 5: IMAGING ACADEMY"
STOP = "SECTION 6: CONDITIONS LIBRARY"


def source_lines():
    with open(SRC, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    begin = next(i for i, l in enumerate(lines) if l.strip() == START)
    finish = next(i for i, l in enumerate(lines) if l.strip() == STOP)
    return lines[begin + 1:finish]


# The scope sentence is the title restated, which is the most this process can
# honestly supply without Part 2. The clause after the title is chosen by what
# the chapter is for, because "Generation of X-rays, as it is acquired and
# interpreted" is not true of anything.
SCOPE_CLAUSE = [
    (("5.2",), "as the knee specialist needs to understand it."),
    (("5.20",), "as it is reported."),
    (("5.21",), "as the literature established it."),
]
SCOPE_DEFAULT = "as it is acquired and interpreted."


def scope_for(chapter, title):
    for chapters, clause in SCOPE_CLAUSE:
        if chapter in chapters:
            return "%s, %s" % (title, clause)
    return "%s, %s" % (title, SCOPE_DEFAULT)


def spiral_deeper():
    """The deeper step after each Section 5 page or chapter, from the spiral map.

    The map is the architecture's own statement of what follows what, so the
    deeper pages come from it rather than from a judgement about which condition
    chapter belongs with which imaging chapter. Two rows name a single page
    rather than a chapter, 5.3.4 for osteoarthritis and 5.16.5 for osteotomy, and
    those are kept at page level rather than widened to their chapter. Chapters
    the topic rows do not name fall back to the Imaging row, whose own deeper
    step is the case library.
    """
    with open(PART1, encoding="utf-8") as fh:
        text = fh.read()
    table = text.split("## 5. Spiral Linkage Map", 1)[1].split("\n## ", 1)[0]
    deeper = {}
    fallback = []
    for row in table.splitlines():
        if not row.startswith("|") or row.startswith("|---"):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) != 2 or cells[0] == "Topic":
            continue
        topic, chain = cells
        steps = [s.strip() for s in chain.split("→")]
        for i, step in enumerate(steps[:-1]):
            ids = re.findall(r"\b5\.\d+(?:\.\d+)*\b", step)
            if not ids:
                continue
            nxt = re.findall(r"\b\d+\.\d+(?:\.\d+)*\b", steps[i + 1])
            if not nxt:
                continue
            if topic == "Imaging":
                fallback = nxt[:1]
                continue
            for one in ids:
                # A row naming 5.3.4 is talking about that page. A row naming
                # 5.6 is talking about the chapter. Keep the distinction.
                deeper.setdefault(one, []).extend(nxt[:1])
    return deeper, fallback


def build():
    deeper_map, fallback = spiral_deeper()
    chapters = collections.OrderedDict()
    navs = []
    chapter = None
    for line in source_lines():
        line = line.rstrip()
        m = CHAPTER.match(line)
        if m:
            chapter = m.group(1)
            chapters[chapter] = {"name": m.group(2), "leaves": []}
            continue
        m = NAV.match(line)
        if m:
            navs.append((m.group(1), m.group(2)))
            continue
        m = LEAF.match(line)
        if m and chapter:
            chapters[chapter]["leaves"].append((m.group(1), m.group(2)))
    pages = []
    renumbered = []
    # Renumbering invalidates any spiral map reference to a navigational id in a
    # flattened chapter. The map's 5.3.4 means the sub section "Osteoarthritis
    # Imaging", and after flattening 5.3.4 is the page "Tunnel View", so taking
    # the reference at face value would wire the osteoarthritis chain to a
    # radiographic view. Each old navigational id is translated to the pages that
    # came from under it instead.
    nav_to_new = {}
    # The grouping is also the only thing that distinguishes two pages the
    # flattening gives the same title. Chapter 5.2 has a Radiation Dose page
    # under X-ray Physics (5.2.1.3) and another under CT Physics (5.2.4.3), and
    # after flattening they are 5.2.3 and 5.2.24 with one title and one chapter
    # name between them. The renderer disambiguates a colliding title tag with
    # the chapter name, which separates nothing here, so it would refuse to
    # render. Keeping the heading keeps the distinction the source made.
    nav_names = dict(navs)
    nav_group = {}
    for chapter, data in chapters.items():
        leaves = data["leaves"]
        # A chapter whose leaves sit a level below a navigational grouping is
        # renumbered flat, in document order, per Part 1's numbering convention.
        flat = any(len(pid.split(".")) == 4 for pid, _ in leaves)
        if flat:
            renumbered.append(chapter)
        ids = ["%s.%d" % (chapter, i) for i in range(1, len(leaves) + 1)] \
            if flat else [pid for pid, _ in leaves]
        if flat:
            for new_id, (old_id, _) in zip(ids, leaves):
                nav = ".".join(old_id.split(".")[:3])
                nav_to_new.setdefault(nav, []).append(new_id)
                if nav in nav_names:
                    nav_group[new_id] = nav_names[nav]
    for nav, new_ids in nav_to_new.items():
        if nav in deeper_map:
            for new_id in new_ids:
                deeper_map.setdefault(new_id, []).extend(deeper_map[nav])
            del deeper_map[nav]
    for chapter, data in chapters.items():
        leaves = data["leaves"]
        flat = chapter in renumbered
        ids = ["%s.%d" % (chapter, i) for i in range(1, len(leaves) + 1)] \
            if flat else [pid for pid, _ in leaves]
        landmark = chapter == "5.21"
        on_a_topic_chain = chapter in deeper_map \
            or any(k.startswith(chapter + ".") for k in deeper_map)
        for page_id, (_, title) in zip(ids, leaves):
            # A page the map names itself wins over its chapter's entry.
            deeper = deeper_map.get(page_id) or deeper_map.get(chapter) \
                or fallback
            chapter_entry = collections.OrderedDict([
                ("id", chapter), ("name", data["name"])])
            if page_id in nav_group:
                chapter_entry["nav_group"] = nav_group[page_id]
            pages.append(collections.OrderedDict([
                ("page_id", page_id),
                ("title", title),
                ("section", dict(SECTION)),
                ("chapter", chapter_entry),
                ("tiers_required", list(TIERS)),
                ("scope", scope_for(chapter, title)),
                ("siblings", [i for i in ids if i != page_id]),
                ("deeper_pages", sorted(set(deeper))),
                ("must_not_cover", BASE_MNC + [own_chapters(chapter)]),
                ("page_type", "landmark_papers" if landmark else "imaging"),
                # Derived from the spiral map rather than stated by Part 1: a
                # chapter on a core topic chain is high, a chapter reached only
                # through the Imaging row is medium, landmark papers low.
                ("priority", "low" if landmark
                 else "high" if on_a_topic_chain else "medium"),
            ]))
    return pages, navs, renumbered


def main():
    pages, navs, renumbered = build()
    counts = collections.Counter(p["chapter"]["id"] for p in pages)
    print("%d pages across %d chapters" % (len(pages), len(counts)))
    print("%d navigational groupings became no page: %s"
          % (len(navs), ", ".join(i for i, _ in navs)))
    print("chapters renumbered flat: %s" % ", ".join(renumbered))
    for chapter in counts:
        print("  %-6s %-40s %d"
              % (chapter,
                 next(p["chapter"]["name"] for p in pages
                      if p["chapter"]["id"] == chapter),
                 counts[chapter]))
    if "--write" in sys.argv:
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(pages, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("written to %s" % OUT)
    else:
        print("dry run; pass --write to write %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
