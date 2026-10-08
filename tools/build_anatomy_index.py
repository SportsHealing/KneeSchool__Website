#!/usr/bin/env python3
"""Render anatomy/index.html: the Section 2 chapter index.

    python3 tools/build_anatomy_index.py

Section 2 is seventy nine pages across twelve chapters, and they arrive a chapter
at a time. A hand written index would be wrong after every batch, so it is
generated from the architecture, which owns the chapter list, and from the
published page index, which owns what exists. A page that is written shows as a
link and a page that is not shows as pending. Nothing has to be remembered.
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
TARGETS = os.path.join(ROOT, "pipeline", "config", "render_targets.json")
OUT = os.path.join(ROOT, "anatomy", "index.html")
REL = "../"


def esc(t):
    return html.escape(str(t), quote=False)


def sort_key(page_id):
    return [(0, int(p)) if p.isdigit() else (1, 0, p) for p in str(page_id).split(".")]


def main():
    with open(ARCH) as fh:
        pages = [p for p in json.load(fh) if str(p["page_id"]).startswith("2.")]
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
                href = os.path.relpath(os.path.join(ROOT, target), os.path.dirname(OUT))
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
    page = chrome.head(
        "The Anatomy Academy | KneeSchool",
        "Section 2: regional anatomy of the knee for medical students, MRCS, FRCS and "
        "fellowship, structure by structure.", REL)
    page += chrome.header(REL)
    page += """
<main id="top">

  <section class="page-hero">
    <div class="wrap">
      <p class="crumb">%s</p>
      <div class="hero-split">
        <div>
          <h1>The Anatomy Academy</h1>
          <p class="who">Section 2 &middot; Regional anatomy, structure by structure</p>
          <p class="lede">Twelve chapters covering the knee one structure at a time, written
          for medical students, MRCS and FRCS candidates, and fellows. %d of %d pages are
          published; the rest are written in syllabus order.</p>
        </div>
        <div></div>
      </div>
    </div>
  </section>

  <section class="band dark">
    <div class="wrap">
      <div class="sec-head">
        <h2>How these pages differ from the Fundamentals</h2>
        <p class="lede">Section 1 explains what the knee is. Section 2 is the dissection, and
        it starts at medical student level rather than ending there.</p>
      </div>
      <div class="rules">
        <ul>
          <li><b>Four tiers, not seven.</b> Medical student, MRCS, FRCS and, on the surgical
          anatomy pages, fellowship. There is no junior or patient tier in this section.</li>
          <li><b>No numbers.</b> These pages carry no measurement, angle, dimension or normal
          range. Nothing could be verified against a source, and a plausible wrong figure at
          this depth is worse than no figure. The anatomy is described in relative terms and
          every page says so.</li>
          <li><b>Pathology, technique and imaging interpretation are elsewhere.</b> This
          section is anatomy. What goes wrong is Section 6, what is done about it is
          Section 7, and how it is imaged is Section 5.</li>
          <li><b>Not yet reviewed.</b> No page in this section has been through evidence
          verification or consultant review, and each page states that at the top.</li>
        </ul>
      </div>
    </div>
  </section>

  <section class="band">
    <div class="wrap">
      <div class="sec-head">
        <h2>The twelve chapters</h2>
        <p class="lede">Pages marked as coming soon are written and reviewed in syllabus
        order.</p>
      </div>
      <div class="topics">
%s
      </div>
      <div class="status" style="margin-top:clamp(2.2rem,4vw,3rem)">
        <b>Note.</b> Nothing in this section is clinical advice or operative instruction. It
        describes normal anatomy for people who already have a clinical qualification or are
        working towards one.
      </div>
    </div>
  </section>

</main>

""" % (chrome.crumb([("KneeSchool", REL + "index.html"), ("Reference", None),
                     ("The Anatomy Academy", None)]),
       live, total, "\n".join(cards))
    page += chrome.footer(REL)
    with open(OUT, "w") as fh:
        fh.write(page)
    print("anatomy/index.html written, %d of %d pages live, %d chapters"
          % (live, total, len(chapters)))


if __name__ == "__main__":
    main()
