#!/usr/bin/env python3
"""Run the deterministic style gate over every page that has one.

The gate itself has existed since the pipeline was scaffolded, and until now it
only ever ran through a per chapter script outside the repository. That meant a
contributor could not run it, CI could not run it, and the claim that it passes
rested on somebody saying so. See decision 021.

A page is linted when it has both a brief and a styled markdown. Pages held
unpublished are included: they are drafts and the gate still applies to them.

    python3 tools/lint_site.py              every page
    python3 tools/lint_site.py 3.12.1 3.13  one page, or every page in a chapter
    python3 tools/lint_site.py --warnings   list warnings as well as failures

Exits non zero if any page has a failure. Warnings never fail the build: the
figure and position registers are warn severity on purpose, because a false
positive there must not be able to block a page.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline", "functions", "style_lint"))

import linter  # noqa: E402

BRIEFS = os.path.join(ROOT, "pipeline", "config", "briefs")
RUNS = os.path.join(ROOT, "pipeline", "runs")


def page_ids(selectors):
    """Every page with a brief and a styled markdown, narrowed by selector.

    A selector is a page id or a chapter id. A chapter id matches its pages, so
    '3.13' lints the ten pages of chapter 3.13 and nothing else.
    """
    out = []
    for name in sorted(os.listdir(BRIEFS)):
        if not name.endswith(".json"):
            continue
        page_id = name[:-5]
        if not os.path.exists(os.path.join(RUNS, page_id, "styled_v1.md")):
            continue
        if selectors and not any(
                page_id == s or page_id.startswith(s + ".") for s in selectors):
            continue
        out.append(page_id)
    return sorted(out, key=lambda p: [int(x) for x in p.split(".")])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("selectors", nargs="*",
                    help="page ids or chapter ids; omit for every page")
    ap.add_argument("--warnings", action="store_true",
                    help="list warnings as well as failures")
    args = ap.parse_args()

    pages = page_ids(args.selectors)
    if not pages:
        sys.exit("no pages matched: %s" % ", ".join(args.selectors or ["(all)"]))

    failures = warnings = 0
    for page_id in pages:
        with open(os.path.join(BRIEFS, "%s.json" % page_id)) as fh:
            brief = json.load(fh)
        with open(os.path.join(RUNS, page_id, "styled_v1.md"), encoding="utf-8") as fh:
            report = linter.lint(fh.read(), brief)
        bad = [f for f in report["findings"] if f["severity"] == "fail"]
        warn = [f for f in report["findings"] if f["severity"] == "warn"]
        failures += len(bad)
        warnings += len(warn)
        if bad or (warn and args.warnings):
            print("%-9s %s" % (page_id, brief["title"]))
        for f in bad:
            print("    FAIL  [%s] %s | %s"
                  % (f["rule_id"], f["description"][:70], f["matched_text"][:50]))
        if args.warnings:
            for f in warn:
                print("    warn  [%s] %s" % (f["rule_id"], f["matched_text"][:60]))

    print("%d page(s) linted, %d failure(s), %d warning(s)"
          % (len(pages), failures, warnings))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
