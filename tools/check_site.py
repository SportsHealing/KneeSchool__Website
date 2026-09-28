#!/usr/bin/env python3
"""Whole site check for the static pages.

    python3 tools/check_site.py

Structure, dashes, house style, and whether every link actually goes somewhere.
The site has no build step, so nothing else catches a broken relative path or a
heading that drifted from the style rules. Exit code 1 on any failure.
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline", "functions", "style_lint"))
import linter  # noqa: E402

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
SKIP_TEXT = {"style", "script", "title"}
DASHES = re.compile(r"[‒–—―]")
HYPHEN_DASH = re.compile(r"\S\s-\s\S")


class Page(HTMLParser):
    def __init__(self, path):
        HTMLParser.__init__(self)
        self.path = path
        self.stack, self.errors = [], []
        self.ids, self.links, self.assets = set(), [], []
        self.text, self._skip = [], 0
        self.lang = None
        self.title_seen = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.title_seen = True
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href"):
            self.assets.append(a["href"])
        if tag == "img" and a.get("src"):
            self.assets.append(a["src"])
        if tag in SKIP_TEXT:
            self._skip += 1
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in SKIP_TEXT:
            self._skip -= 1
        if not self.stack:
            self.errors.append("stray </%s> at %s" % (tag, self.getpos()))
        elif self.stack[-1][0] != tag:
            self.errors.append("</%s> closes <%s> opened at %s"
                               % (tag, self.stack[-1][0], self.stack[-1][1]))
        else:
            self.stack.pop()

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)

    def visible(self):
        return " ".join(self.text)


def html_files():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "pipeline", "docs", "node_modules")]
        for f in sorted(files):
            if f.endswith(".html"):
                out.append(os.path.join(base, f))
    return sorted(out)


# Warnings that have been looked at and deliberately kept. Each one needs a
# reason, so the list stays short and the remaining warnings stay worth reading.
# A warning with no entry here is a warning someone still has to answer for.
EXEMPTIONS = [
    ("levels/junior.html", "PHRASE-001", "meet the",
     "chapter 0.5.5 is titled 'Meet the Researchers' in the architecture document; "
     "the site label matches the source by decision"),
    ("index.html", "PHRASE-001", "meet the",
     "existing approved homepage copy, 'Meet the topic'; flagged to the client, not yet changed"),
    ("encyclopaedia/whole-body.html", "PHRASE-001", "not only",
     "the rule targets 'not only X but also Y'; 'the person and not only the scan' is not that "
     "construction, so this is a rule false positive"),
]


def exemption_for(rel, rule_id, phrase):
    for path, rid, ph, reason in EXEMPTIONS:
        if rel == path and rid == rule_id and ph == phrase:
            return reason
    return None


def phrase_rules():
    rules = linter.load_rules(os.path.join(ROOT, "pipeline", "config", "lint_rules.json"))
    return [r for r in rules["rules"]
            if r["id"] in ("PHRASE-001", "UK-001") and r.get("banned_phrases")]


def chrome_drift():
    """A page whose header or footer has fallen behind tools/site_chrome.py.
    The site has no build step, so the ribbon is copied into every file and
    drift is the obvious failure mode."""
    import subprocess
    out = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "apply_chrome.py"),
                          "--check"], capture_output=True, text=True, cwd=ROOT)
    return ["%s: header or footer is out of step with tools/site_chrome.py"
            % line.split()[-1]
            for line in out.stdout.splitlines() if line.strip().startswith("DRIFTED")]


def main():
    pages, failures, warnings, exempt = {}, [], [], []
    files = html_files()
    if not files:
        print("no HTML files found")
        return 1

    for path in files:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        page = Page(path)
        page.feed(raw)
        pages[os.path.normpath(path)] = page

        rel = os.path.relpath(path, ROOT)
        for err in page.errors:
            failures.append("%s: %s" % (rel, err))
        if page.stack:
            failures.append("%s: unclosed %s"
                            % (rel, ", ".join("<%s> at %s" % (t, p) for t, p in page.stack)))
        if page.lang != "en-GB":
            failures.append("%s: html lang is %r, expected 'en-GB'" % (rel, page.lang))
        if not page.title_seen:
            failures.append("%s: no <title>" % rel)

        body = page.visible()
        if DASHES.search(raw):
            failures.append("%s: contains an em or en dash" % rel)
        m = HYPHEN_DASH.search(body)
        if m:
            failures.append("%s: space hyphen space in prose near %r" % (rel, m.group(0)))

        low = body.lower()
        for rule in phrase_rules():
            for phrase in rule["banned_phrases"]:
                for hit in re.finditer(r"(?<![a-z])" + re.escape(phrase.lower()) + r"(?![a-z])", low):
                    ctx = re.sub(r"\s+", " ", body[max(0, hit.start() - 40):hit.end() + 25]).strip()
                    reason = exemption_for(rel, rule["id"], phrase)
                    line = "%s: %s %r ... %s" % (rel, rule["id"], phrase, ctx)
                    if reason:
                        exempt.append("%s\n          reason: %s" % (line, reason))
                    else:
                        warnings.append(line)

    # ---- link integrity across the whole site ----
    for path, page in sorted(pages.items()):
        rel = os.path.relpath(path, ROOT)
        here = os.path.dirname(path)
        for href in page.links + page.assets:
            if href.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            if href == "#":
                continue
            if href.startswith("/"):
                failures.append("%s: root relative link %r will not resolve from a subpath" % (rel, href))
                continue
            target, _, frag = href.partition("#")
            target = target.split("?", 1)[0]   # drop the cache busting version
            if not target:
                if frag and frag not in page.ids:
                    failures.append("%s: anchor #%s does not exist on this page" % (rel, frag))
                continue
            dest = os.path.normpath(os.path.join(here, target))
            if not os.path.exists(dest):
                failures.append("%s: link %r points at a missing file" % (rel, href))
            elif frag:
                other = pages.get(dest)
                if other is None and dest.endswith(".html"):
                    failures.append("%s: link %r targets an unparsed page" % (rel, href))
                elif other is not None and frag not in other.ids:
                    failures.append("%s: link %r targets a missing anchor" % (rel, href))

    drift = chrome_drift()
    failures.extend(drift)

    print("checked %d pages" % len(pages))
    for e in exempt:
        print("  KEPT  %s" % e)
    for w in warnings:
        print("  WARN  %s" % w)
    for f in failures:
        print("  FAIL  %s" % f)
    print("")
    print("%d failures, %d warnings, %d deliberately kept"
          % (len(failures), len(warnings), len(exempt)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
