#!/usr/bin/env python3
"""Publication QA: the fifth gate.

    python3 tools/publication_qa.py            # every page, failures only
    python3 tools/publication_qa.py --report   # every page, every rule, pass or fail
    python3 tools/publication_qa.py --page index.html

Chapter 13 of the Master Operations Handbook names five QA tiers: AI generation,
assistant editorial review, source verification, consultant review, and
publication review. The first four are the pipeline. This is the fifth. The
handbook says publication QA "checks formatting, SEO, links, images, alt text,
disclaimers, metadata and page status", and chapter 14 says every page requires
an SEO title, a meta description, a slug, an H1, an H2 structure, related
articles, internal links and image alt text.

Three of those were already checked elsewhere and are not repeated here. Link
integrity, the HTML structure and chrome drift belong to tools/check_site.py,
which runs over the same files. This tool is the part that was missing: the
metadata a search engine and a screen reader read, which nothing checked before.

Every bound comes from pipeline/config/site.json, so the thresholds are
configuration rather than numbers buried in code. See decision 010.
"""

import argparse
import collections
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import site_chrome as chrome  # noqa: E402

SKIP_DIRS = {".git", "pipeline", "docs", "node_modules", "assets"}


class Head(HTMLParser):
    """Everything the publication rules need, in one pass: the head metadata,
    the heading ladder, the images and the visible text."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.title = None
        self.meta = {}
        self.canonical = None
        self.headings = []        # (level, text)
        self.images = []          # (src, alt or None)
        self.internal_links = []
        self.text = []
        self._in_title = False
        self._heading = None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = a.get("name") or ("charset" if "charset" in a else None)
            if name:
                self.meta[name] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href", "")
        elif tag in ("h1", "h2", "h3", "h4"):
            self._heading = [int(tag[1]), []]
        elif tag == "img":
            self.images.append((a.get("src", ""), a.get("alt")))
        elif tag == "a":
            href = a.get("href", "")
            if href and not href.startswith(("http://", "https://", "mailto:",
                                             "tel:", "#")):
                self.internal_links.append(href)
        elif tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4") and self._heading:
            self.headings.append((self._heading[0],
                                  " ".join(self._heading[1]).strip()))
            self._heading = None
        elif tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self._heading:
            self._heading[1].append(data)
        if not self._skip:
            self.text.append(data)

    def visible(self):
        return re.sub(r"\s+", " ", " ".join(self.text))


def pages(only=None):
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(base, f), ROOT)
                if only is None or rel in only:
                    out.append(rel)
    return sorted(out)


def parse_all(rels):
    parsed = {}
    for rel in rels:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            p = Head()
            p.feed(fh.read())
            parsed[rel] = p
    return parsed


# ---------------------------------------------------------------- the rules --
# Each returns a list of failure strings for one page. Site wide uniqueness
# needs every page at once, so those two rules take the whole set.

def pub_001(rel, page, cfg, _all):
    """SEO title: present, within bounds, carrying the site suffix."""
    seo, out = cfg["seo"], []
    if not page.title:
        return ["no <title>"]
    title = page.title.strip()
    brand = cfg["title_suffix"].strip(" |")
    if rel == "index.html":
        # The homepage leads with the brand rather than trailing it, which is
        # the ordinary convention and what a search result should show.
        if not title.startswith(brand):
            out.append("the homepage title does not start %r" % brand)
    elif not title.endswith(cfg["title_suffix"]):
        out.append("title does not end %r" % cfg["title_suffix"])
    if not (seo["title_min"] <= len(title) <= seo["title_max"]):
        out.append("title is %d characters, wanted %d to %d"
                   % (len(title), seo["title_min"], seo["title_max"]))
    return out


def pub_002(rel, page, cfg, _all):
    """Meta description: present, within bounds, a finished sentence."""
    seo, out = cfg["seo"], []
    d = page.meta.get("description", "").strip()
    if not d:
        return ["no meta description"]
    if not (seo["description_min"] <= len(d) <= seo["description_max"]):
        out.append("meta description is %d characters, wanted %d to %d"
                   % (len(d), seo["description_min"], seo["description_max"]))
    if not d.endswith((".", "?", "!")):
        out.append("meta description does not end a sentence, so it reads as "
                   "truncated: %r" % d[-40:])
    return out


def pub_003(rel, page, cfg, _all):
    """Slug: the canonical link agrees with where the file sits."""
    if not page.canonical:
        return ["no canonical link"]
    want = chrome.canonical_url(rel)
    if page.canonical != want:
        return ["canonical is %r, the file is at %r" % (page.canonical, want)]
    slug = os.path.basename(rel)[:-5]
    if slug != "index" and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        return ["slug %r is not lower case words separated by hyphens" % slug]
    return []


def pub_004(rel, page, cfg, _all):
    """Formatting: one H1, and a heading ladder that never skips a level."""
    out = []
    h1s = [t for lvl, t in page.headings if lvl == 1]
    if len(h1s) != 1:
        out.append("%d H1 headings, wanted exactly 1" % len(h1s))
    last = 0
    for lvl, text in page.headings:
        if last and lvl > last + 1:
            out.append("heading jumps from H%d to H%d at %r" % (last, lvl, text[:40]))
        last = lvl
    return out


def pub_005(rel, page, cfg, _all):
    """Alt text on every image. No page carries one yet; the rule is here so
    that the first one cannot arrive without it."""
    return ["<img src=%r has no alt text>" % src
            for src, alt in page.images if alt is None or not alt.strip()]


def pub_006(rel, page, cfg, _all):
    """Disclaimer. tools/check_site.py fails the build on this too; publication
    QA reports it because the handbook lists disclaimers under this gate."""
    want = cfg["medical_safety"]["required_sentence"]
    if want.lower() not in page.visible().lower():
        return ["no educational and not a substitute statement"]
    return []


def pub_007(rel, page, cfg, _all):
    """Internal linking. Chapter 14: every page links upwards to its parent,
    sideways to related topics and downwards to more advanced pages. What is
    mechanically checkable is that the page links upwards at all, and that it
    links somewhere other than the chrome."""
    if not page.internal_links:
        return ["no internal links"]
    ups = [h for h in page.internal_links if h.startswith("../") or
           (os.sep not in rel and not h.startswith("."))]
    if not ups and os.sep in rel:
        return ["no link upwards out of its own directory"]
    return []


def pub_008(rel, page, cfg, _all):
    """Metadata."""
    out = []
    for name in cfg["required_metadata"]:
        if name == "canonical":
            if not page.canonical:
                out.append("no canonical link")
        elif name not in page.meta:
            out.append("no %s meta" % name)
    return out


def pub_009(rel, page, cfg, all_pages):
    """Uniqueness. A duplicate title or description makes two pages compete for
    the same search result, which is the one SEO fault that cannot be seen by
    reading a single page."""
    out = []
    titles = collections.Counter((p.title or "").strip()
                                 for p in all_pages.values())
    descs = collections.Counter(p.meta.get("description", "").strip()
                                for p in all_pages.values())
    if titles[(page.title or "").strip()] > 1:
        out.append("title is not unique on the site")
    if descs[page.meta.get("description", "").strip()] > 1:
        out.append("meta description is not unique on the site")
    return out


def pub_010(rel, page, cfg, _all):
    """The publication posture. While the site is published and not publicised,
    every page carries the noindex directive; when that changes, no page does.
    A site where some pages are indexable and some are not has no posture, and
    the half that is indexable is the half that publicises it."""
    want = not cfg.get("discoverable")
    got = page.meta.get("robots", "")
    if want and "noindex" not in got.lower():
        return ["no robots noindex directive, but site.json says the site is "
                "published and not publicised"]
    if not want and "noindex" in got.lower():
        return ["carries a robots noindex directive, but site.json says the site "
                "is discoverable"]
    return []


RULES = [
    ("PUB-001", "SEO title", pub_001),
    ("PUB-002", "Meta description", pub_002),
    ("PUB-003", "Slug and canonical", pub_003),
    ("PUB-004", "Heading structure", pub_004),
    ("PUB-005", "Image alt text", pub_005),
    ("PUB-006", "Disclaimer", pub_006),
    ("PUB-007", "Internal linking", pub_007),
    ("PUB-008", "Metadata", pub_008),
    ("PUB-009", "Uniqueness", pub_009),
    ("PUB-010", "Publication posture", pub_010),
]


def run(rels=None):
    cfg = chrome.site_config()
    rels = pages(rels)
    parsed = parse_all(pages())          # uniqueness needs the whole site
    results = collections.OrderedDict()
    for rel in rels:
        page = parsed[rel]
        results[rel] = [(rid, name, rule(rel, page, cfg, parsed))
                        for rid, name, rule in RULES]
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true",
                    help="print every rule for every page, passing or not")
    ap.add_argument("--page", nargs="*", help="check only these paths")
    args = ap.parse_args()

    results = run(args.page)
    failed_pages, failures = 0, 0
    by_rule = collections.Counter()
    for rel, rows in results.items():
        bad = [(rid, name, msgs) for rid, name, msgs in rows if msgs]
        if bad:
            failed_pages += 1
        if args.report:
            print("%s" % rel)
            for rid, name, msgs in rows:
                print("  %-9s %-20s %s" % (rid, name, "ok" if not msgs else ""))
                for m in msgs:
                    print("      %s" % m)
        else:
            for rid, name, msgs in bad:
                print("%s" % rel)
                break
            for rid, name, msgs in bad:
                for m in msgs:
                    print("  %-9s %s" % (rid, m))
        for rid, name, msgs in bad:
            by_rule[rid] += len(msgs)
            failures += len(msgs)

    print("")
    print("%d pages checked, %d pages with a finding, %d findings"
          % (len(results), failed_pages, failures))
    for rid, name, _ in RULES:
        if by_rule[rid]:
            print("  %-9s %-20s %d" % (rid, name, by_rule[rid]))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
