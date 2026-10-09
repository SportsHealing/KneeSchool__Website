#!/usr/bin/env python3
"""Render a section's chapter index page.

    python3 tools/build_section_index.py          # every declared section
    python3 tools/build_section_index.py 3        # just this one

A section arrives a chapter at a time, so a hand written index is wrong after
every batch. Everything that can be derived is derived: the chapter list and the
page list from the architecture, what exists from the published page index, and
the two lines of progress copy from the count. What cannot be derived, the
directory, the title and the standing panel, is declared once in
pipeline/config/section_indexes.json.

This replaces tools/build_anatomy_index.py, which did the same job for Section 2
alone. Section 3 needed a second index and Sections 4 to 15 will each need one,
so the generator takes the section as an argument rather than being copied.
"""

import collections
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import site_chrome as chrome  # noqa: E402
import page_index  # noqa: E402

ARCH = os.path.join(ROOT, "pipeline", "config", "architecture", "pages_0_to_3.json")
CONFIG = os.path.join(ROOT, "pipeline", "config", "section_indexes.json")
REL = "../"


def esc(t):
    return html.escape(str(t), quote=False)


def sort_key(page_id):
    return [(0, int(p)) if p.isdigit() else (1, 0, p) for p in str(page_id).split(".")]


def build(section_id, spec):
    out = os.path.join(ROOT, spec["dir"], "index.html")
    with open(ARCH) as fh:
        pages = [p for p in json.load(fh)
                 if str(p["page_id"]).startswith(section_id + ".")]
    pages.sort(key=lambda p: sort_key(p["page_id"]))
    published = page_index.load()

    chapters = collections.OrderedDict()
    for p in pages:
        chapters.setdefault((p["chapter"]["id"], p["chapter"]["name"]), []).append(p)

    cards, live = [], 0
    for (cid, cname), items in chapters.items():
        rows = []
        for p in items:
            target = published.get(p["page_id"])
            if target:
                live += 1
                href = os.path.relpath(os.path.join(ROOT, target), os.path.dirname(out))
                body = '<a href="%s">%s</a>' % (esc(href), esc(p["title"]))
            else:
                body = '<span class="soon">%s</span>' % esc(p["title"])
            rows.append("            <li>%s</li>" % body)
        cards.append("""        <div class="topic">
          <span class="num">%s</span>
          <h3>%s</h3>
          <ul>
%s
          </ul>
        </div>""" % (esc(cid), esc(cname), "\n".join(rows)))

    total = len(pages)
    # The section is either finished or it is not, and the page should say which
    # without anyone editing it.
    if live >= total:
        lede = "All %d pages are published and awaiting review." % total
        note = ("Every chapter is written. No page in this section has been through "
                "evidence verification or consultant review, and each one says so at "
                "the top.")
    else:
        lede = ("%d of %d pages are published; the rest are written in syllabus order."
                % (live, total))
        note = "Pages marked as coming soon are written and reviewed in syllabus order."

    points = "\n".join(
        "          <li><b>%s</b> %s</li>" % (esc(b), esc(rest))
        for b, rest in spec["panel_points"])

    page = chrome.head("%s | KneeSchool" % spec["title"], spec["description"], REL)
    page += chrome.header(REL)
    page += """
<main id="top">

  <section class="page-hero">
    <div class="wrap">
      <p class="crumb">%s</p>
      <div class="hero-split">
        <div>
          <h1>%s</h1>
          <p class="who">%s</p>
          <p class="lede">%s %s</p>
        </div>
        <div></div>
      </div>
    </div>
  </section>

  <section class="band dark">
    <div class="wrap">
      <div class="sec-head">
        <h2>%s</h2>
        <p class="lede">%s</p>
      </div>
      <div class="rules">
        <ul>
%s
        </ul>
      </div>
    </div>
  </section>

  <section class="band paper">
    <div class="wrap">
      <div class="sec-head">
        <h2>The %s chapters</h2>
        <p class="lede">%s</p>
      </div>
      <div class="topics">
%s
      </div>
      <div class="status" style="margin-top:clamp(2.2rem,4vw,3rem)">
        <b>Note.</b> %s
      </div>
    </div>
  </section>

</main>

""" % (chrome.crumb([("KneeSchool", REL + "index.html"), ("Reference", None),
                     (spec["title"], None)]),
       esc(spec["title"]), spec["who"], esc(spec["lede_prefix"]), esc(lede),
       esc(spec["panel_heading"]), esc(spec["panel_lede"]), points,
       NUMBER_WORDS.get(len(chapters), str(len(chapters))), esc(note),
       "\n".join(cards), esc(spec["note"]))
    page += chrome.footer(REL)
    d = os.path.dirname(out)
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(out, "w") as fh:
        fh.write(page)
    print("%s/index.html written, %d of %d pages live, %d chapters"
          % (spec["dir"], live, total, len(chapters)))


NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
                12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
                16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
                20: "twenty"}


def main():
    with open(CONFIG) as fh:
        sections = json.load(fh)["sections"]
    wanted = sys.argv[1:] or sorted(sections, key=int)
    unknown = [s for s in wanted if s not in sections]
    if unknown:
        sys.exit("no section index declared for: %s" % ", ".join(unknown))
    for section_id in wanted:
        build(section_id, sections[section_id])


if __name__ == "__main__":
    main()
