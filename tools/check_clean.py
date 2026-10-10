#!/usr/bin/env python3
"""Fail if the working tree is not clean.

The last step of `make verify`. Every check before it is read only, so if the
tree has changed, something that calls itself a check is writing. That happened
twice: the position extractor appended to a note on every run, and a test ran
that extractor against the repository's own registers and restored one file of
the many it touched. Both were found by a stop hook noticing uncommitted changes
rather than by anything in the build. See decision 021.

Run it after the checks, not before: a dirty tree at the start is ordinary work
in progress, and a dirty tree the checks caused is a bug.

    python3 tools/check_clean.py            fail on any change
    python3 tools/check_clean.py --baseline /tmp/before.txt

With --baseline it compares against a status captured earlier, so uncommitted
work in progress does not fail the run and a change the checks made still does.
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def status():
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True)
    if out.returncode:
        sys.exit("git status failed: %s" % out.stderr.strip())
    return sorted(line for line in out.stdout.splitlines() if line.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--baseline", help="a file holding an earlier git status --porcelain")
    ap.add_argument("--write-baseline", help="write the current status and exit 0")
    args = ap.parse_args()

    now = status()

    if args.write_baseline:
        with open(args.write_baseline, "w", encoding="utf-8") as fh:
            fh.write("\n".join(now) + ("\n" if now else ""))
        print("baseline written: %d entr(ies)" % len(now))
        return

    before = []
    if args.baseline and os.path.exists(args.baseline):
        with open(args.baseline, encoding="utf-8") as fh:
            before = sorted(line for line in fh.read().splitlines() if line.strip())

    new = [line for line in now if line not in before]
    if not new:
        print("working tree unchanged by the checks")
        return

    print("the checks changed %d file(s), which means something that calls "
          "itself a check is writing:" % len(new))
    for line in new:
        print("   ", line)
    sys.exit(1)


if __name__ == "__main__":
    main()
