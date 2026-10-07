#!/usr/bin/env python3
"""The index of which page_id is published at which URL.

    python3 tools/page_index.py --prune
    python3 tools/page_index.py --list

Every article carries an Explore Further block written as [[page_id | label]].
Until a page exists there is nothing to link to, so the renderer shows the label
as pending text. This index is how the renderer knows which ones exist.

It is written by the renderer rather than maintained by hand, because a hand
maintained list of three thousand page ids would be wrong within a week. Each
render registers its own page. --prune drops entries whose file has since gone.
"""

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "pipeline", "config", "published_pages.json")


def load():
    if not os.path.exists(PATH):
        return {}
    with open(PATH) as fh:
        return json.load(fh).get("pages") or {}


def save(pages):
    def key(pid):
        return [(0, int(p)) if p.isdigit() else (1, 0, p) for p in str(pid).split(".")]
    body = {
        "index_version": "1.0",
        "note": ("page_id to published path, relative to the repository root. Written by "
                 "tools/render_article.py --register. Read by the same renderer to decide "
                 "whether a cross link resolves or shows as pending."),
        "pages": dict((pid, pages[pid]) for pid in sorted(pages, key=key)),
    }
    with open(PATH, "w") as fh:
        fh.write(json.dumps(body, indent=2) + "\n")


def register(page_id, out_path):
    pages = load()
    pages[str(page_id)] = os.path.relpath(os.path.abspath(out_path), ROOT)
    save(pages)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    pages = load()
    if args.prune:
        gone = [p for p, path in pages.items() if not os.path.exists(os.path.join(ROOT, path))]
        for p in gone:
            del pages[p]
        save(pages)
        print("pruned %d, %d remain" % (len(gone), len(pages)))
    if args.list or not args.prune:
        for pid, path in pages.items():
            print("%-8s %s" % (pid, path))
        print("%d pages indexed" % len(pages))


if __name__ == "__main__":
    main()
