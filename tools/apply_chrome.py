#!/usr/bin/env python3
"""Rewrite the header and footer of every page from tools/site_chrome.py.

    python3 tools/apply_chrome.py          # rewrite every page
    python3 tools/apply_chrome.py --check  # report drift, change nothing

The site has no build step, so the navigation is duplicated into every file. The
cost of that is drift: change the ribbon and ten pages disagree until each one
is edited. This tool is the answer. One source, applied everywhere, and --check
in the site check catches a page that fell behind.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import site_chrome as chrome  # noqa: E402

SKIP_DIRS = {".git", "pipeline", "docs", "node_modules", "assets"}
HEADER = re.compile(r'<header class="site-head">.*?</header>\n', re.DOTALL)
FOOTER = re.compile(r'<footer class="site-foot"[^>]*>.*?</footer>\n', re.DOTALL)
# The stylesheet link lives in <head>, which the header replacement does not
# reach, so its cache busting version is rewritten separately.
STYLES = re.compile(r'href="((?:\.\./)*assets/styles\.css)(?:\?v=[^"]*)?"')


def pages():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".html"):
                out.append(os.path.join(base, f))
    return sorted(out)


def rel_for(path):
    depth = os.path.relpath(path, ROOT).count(os.sep)
    return "../" * depth


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="report pages whose chrome has drifted, and change nothing")
    args = ap.parse_args()

    changed, drifted, skipped = [], [], []
    for path in pages():
        rel = rel_for(path)
        with open(path, encoding="utf-8") as fh:
            original = fh.read()

        if not HEADER.search(original) or not FOOTER.search(original):
            skipped.append(os.path.relpath(path, ROOT))
            continue

        version = chrome.stylesheet_version()
        updated = STYLES.sub(lambda m: 'href="%s?v=%s"' % (m.group(1), version), original)
        updated = HEADER.sub(lambda m: chrome.header(rel), updated, count=1)
        # the footer template closes the document, so anything after it goes
        updated = FOOTER.sub(lambda m: chrome.footer(rel), updated, count=1)
        updated = re.sub(r'(</footer>\n).*\Z', r'\1\n</body>\n</html>\n', updated,
                         flags=re.DOTALL)

        if updated == original:
            continue
        if args.check:
            drifted.append(os.path.relpath(path, ROOT))
        else:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(updated)
            changed.append(os.path.relpath(path, ROOT))

    for name in skipped:
        print("  skipped (no header or footer to replace): %s" % name)
    if args.check:
        for name in drifted:
            print("  DRIFTED  %s" % name)
        print("%d page(s) out of step with tools/site_chrome.py" % len(drifted))
        return 1 if drifted else 0
    for name in changed:
        print("  updated  %s" % name)
    print("%d page(s) rewritten, %d already current" % (changed.__len__(),
                                                        len(pages()) - len(changed) - len(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
