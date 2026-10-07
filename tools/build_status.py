#!/usr/bin/env python3
"""Render about/status.html from docs/build_status.json.

    python3 tools/build_status.py

Several published pages tell the reader that progress on a missing feature is
recorded on the build status page. That makes the page a promise rather than a
convenience, so it is generated from one data file instead of being kept in step
by hand. Edit the JSON; run this; commit both.
"""

import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import site_chrome as chrome  # noqa: E402

DATA = os.path.join(ROOT, "docs", "build_status.json")
OUT = os.path.join(ROOT, "about", "status.html")
REL = "../"


def esc(t):
    return html.escape(str(t), quote=False)


def row(it):
    cells = [
        ('Item', "<b>%s</b> %s" % (esc(it["ref"]), esc(it["title"]))),
        ('State', esc(it.get("state", ""))),
        ('What is in the way', esc(it.get("blocker", ""))),
        ('What would move it', esc(it.get("needed", ""))),
    ]
    if it.get("pages"):
        cells.append(('Pages', esc(it["pages"])))
    return "<tr>" + "".join('<td data-label="%s">%s</td>' % (h, v) for h, v in cells) + "</tr>"


def group(g):
    heads = ["Item", "State", "What is in the way", "What would move it"]
    if any(i.get("pages") for i in g["items"]):
        heads.append("Pages")
    return """
      <div class="sec-head">
        <h2>%s</h2>
        <p class="lede">%s</p>
      </div>
      <div class="table-scroll">
        <table class="map">
          <thead>
            <tr>%s</tr>
          </thead>
          <tbody>
            %s
          </tbody>
        </table>
      </div>
""" % (esc(g["name"]), esc(g["lede"]),
       "".join('<th scope="col">%s</th>' % h for h in heads),
       "\n            ".join(row(i) for i in g["items"]))


def main():
    with open(DATA) as fh:
        data = json.load(fh)
    groups = data["groups"]
    total = sum(len(g["items"]) for g in groups)

    page = chrome.head("Build status | KneeSchool",
                       "What is finished, what is waiting for review, and what cannot be built "
                       "from here until something outside the repository changes.", REL)
    page += chrome.header(REL)
    page += """
<main id="top">

  <section class="page-hero">
    <div class="wrap">
      <p class="crumb">%s</p>
      <div class="hero-split">
        <div>
          <h1>Build status</h1>
          <p class="who">What is done, what is waiting, and what is blocked</p>
          <p class="lede">%d open items. A page that tells you a feature is not available yet
          links here, so this list is the answer to where that work has got to.</p>
        </div>
        <div></div>
      </div>
    </div>
  </section>
""" % (chrome.crumb([("KneeSchool", REL + "index.html"), ("About", None),
                     ("Build status", None)]), total)

    for n, g in enumerate(groups):
        page += '\n  <section class="band%s">\n    <div class="wrap">%s    </div>\n  </section>\n' % (
            " dark" if n % 2 == 0 else "", group(g))

    page += """
  <section class="band wrap">
    <div class="status">
      <b>How to read this.</b> Nothing on this list is hidden from the pages themselves. Where a
      page describes something the site cannot yet do, the page says so in its own words. This
      list exists so that the reason, and what would change it, is recorded in one place.
    </div>
  </section>

</main>

"""
    page += chrome.footer(REL)
    with open(OUT, "w") as fh:
        fh.write(page)
    print("%s written, %d items in %d groups" % (os.path.relpath(OUT, ROOT), total, len(groups)))


if __name__ == "__main__":
    main()
