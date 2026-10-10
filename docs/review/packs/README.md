# Generated review packs

One pack per chapter, generated from that chapter's own files. Nothing here is
written by hand, and regenerating a pack rewrites everything except the Decision
and Reviewer columns.

    python3 tools/review_pack.py --status      # what is outstanding, by chapter
    python3 tools/review_pack.py --all         # regenerate every pack
    python3 tools/review_pack.py --check       # report drift, change nothing

A reviewer fills the Decision and Reviewer columns and sends the file back. Then:

    python3 tools/review_pack.py --ingest docs/review/packs/chapter-3.3.md

writes each decision into `pipeline/config/positions/<page>.json` and
`pipeline/config/figures/<page>.json`. A blank row stays outstanding and comes
back in the next pack. See decision 016.

The eight packs in the parent directory are the earlier hand written ones. They
are kept because they carry reasoning a generated pack does not: the framing
question each batch rests on, and what the reviewer should read first. They are
not regenerated and they do not read back.
