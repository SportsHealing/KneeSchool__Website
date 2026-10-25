#!/usr/bin/env python3
"""Render about/status.html from docs/build_status.json.

    python3 tools/build_status.py

Several published pages tell the reader that progress on a missing feature is
recorded on the build status page. That makes the page a promise rather than a
convenience, so it is generated from one data file instead of being kept in step
by hand. Edit the JSON; run this; commit both.
"""

import collections
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import site_chrome as chrome  # noqa: E402

DATA = os.path.join(ROOT, "docs", "build_status.json")
OUT = os.path.join(ROOT, "about", "status.html")
REL = "../"
CONFIG = os.path.join(ROOT, "pipeline", "config")
# A {{token}} in any build_status.json string is filled from the registers. The
# numbers used to be typed into the prose, and by the time chapter 4.11 was
# written the page was telling a reader there were 448 unchecked measurements
# when the register held 462, that 32 chapters carried recommendations when 37
# did, and that the largest was 3.7 when it was 4.2. Nobody introduced that: the
# prose was correct when written and the registers moved. Same failure as the
# hand compiled figure list that decision 006 replaced, so it gets the same
# answer rather than a correction.
TOKEN = re.compile(r"\{\{([a-z_]+)\}\}")


def thousands(n):
    return "{:,}".format(n)


def register(kind, field, state):
    """Live counts from one register directory: entries, pages, per chapter."""
    per_chapter = collections.Counter()
    pages, total = set(), 0
    for path in sorted(glob.glob(os.path.join(CONFIG, kind, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            entries = json.load(fh)[field]
        live = [e for e in entries if e.get("verification", state) == state]
        if not live:
            continue
        page_id = os.path.basename(path)[:-len(".json")]
        total += len(live)
        pages.add(page_id)
        per_chapter[".".join(page_id.split(".")[:2])] += len(live)
    return total, len(pages), per_chapter


def register_counts():
    """Every number about/status.html quotes about the registers.

    Generated from the registers for the reason the registers are themselves
    generated from the pages: a hand kept number falls behind what it describes
    and nothing reports that it has.
    """
    figures, fig_pages, _ = register("figures", "figures", "UNVERIFIED_FROM_MEMORY")
    positions, pos_pages, by_chapter = register("positions", "positions", "UNSIGNED")
    attributions, attr_pages, _ = register("attributions", "attributions",
                                           "UNVERIFIED_FROM_MEMORY")
    counts = sorted(by_chapter.values())
    largest = max(by_chapter.items(), key=lambda kv: (kv[1], kv[0])) if by_chapter else ("", 0)
    packs = len(glob.glob(os.path.join(ROOT, "docs", "review", "packs", "chapter-*.md")))
    # Counted from the same function apply_chrome.py writes the sitemap from,
    # not from sitemap.xml itself. Reading the file made this page quote the
    # previous count whenever a batch of pages was added and build_status ran
    # before apply_chrome.
    urls = len(chrome.sitemap_paths()) if chrome.site_config().get("discoverable") else 0
    return {
        "figures_unchecked": thousands(figures),
        "figure_pages": thousands(fig_pages),
        "positions_unsigned": thousands(positions),
        "position_pages": thousands(pos_pages),
        "position_chapters": thousands(len(by_chapter)),
        "largest_position_chapter": largest[0],
        "largest_position_count": thousands(largest[1]),
        "median_position_count": thousands(counts[len(counts) // 2] if counts else 0),
        "attributions_unchecked": thousands(attributions),
        "attribution_pages": thousands(attr_pages),
        "review_pack_chapters": thousands(packs),
        "sitemap_urls": thousands(urls),
    }


def fill(value, counts):
    """Substitute {{token}} anywhere in the data file's strings."""
    if isinstance(value, str):
        def one(m):
            if m.group(1) not in counts:
                raise SystemExit("build_status.json uses an unknown token: %s" % m.group(0))
            return counts[m.group(1)]
        return TOKEN.sub(one, value)
    if isinstance(value, list):
        return [fill(v, counts) for v in value]
    if isinstance(value, dict):
        return dict((k, fill(v, counts)) for k, v in value.items())
    return value


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
    data = fill(data, register_counts())
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
      %s
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
