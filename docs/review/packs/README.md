# Generated review packs

One pack per chapter, generated from that chapter's own files in three formats.
Nothing here is written by hand, and regenerating a pack rewrites everything
except the Decision and Reviewer columns.

    python3 tools/review_pack.py --status                      # outstanding, by chapter
    python3 tools/review_pack.py --all                          # regenerate the markdown
    python3 tools/review_pack.py --chapter 3.3 --format all     # add the xlsx and the docx
    python3 tools/review_pack.py --check                        # report drift, change nothing

The markdown is generated for every chapter. The spreadsheet and the Word file
are generated per chapter on request, because both embed a timestamp and
regenerating fifty binaries on every run would churn the repository.

The spreadsheet is what a reviewer fills: a dropdown on each Decision column, a
Note column for amended wording, and a Progress sheet that counts the decisions
as they are made. The Word file is landscape and is what gets printed.

A reviewer fills the Decision and Reviewer columns and sends any of the three
back. Then:

    python3 tools/review_pack.py --ingest docs/review/packs/chapter-3.3.xlsx

writes each decision into `pipeline/config/positions/<page>.json` and
`pipeline/config/figures/<page>.json`. A blank row stays outstanding and comes
back in the next pack. One malformed row stops the whole file, so nothing is
written half way. See decisions 016 and 017.

The spreadsheet and the Word file need two libraries:

    pip install openpyxl python-docx

The markdown path needs nothing but the standard library, so a checkout without
them can still generate, check and ingest markdown packs.

The eight packs in the parent directory are the earlier hand written ones. They
are kept because they carry reasoning a generated pack does not: the framing
question each batch rests on, and what the reviewer should read first. They are
not regenerated and they do not read back.
