# Decision 017: the review pack in three formats

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Client, on 10 October 2026 |
| Status | Applied |
| Changes | New module `tools/review_pack_files.py`, `--format`, ingest from three formats, 9 tests |

## The instruction

> Spreadsheet and formatted word file

Asked in answer to this, put after the markdown packs went up:

> The generated packs are markdown. Would a spreadsheet be easier for a
> consultant to fill, given they will be working in a column of 85 cells?

## What was added

Every pack now generates in three formats from the same data:

    python3 tools/review_pack.py --chapter 3.3 --format all

The markdown stays the default. The spreadsheet is what a reviewer fills, and the
Word file is what gets printed.

All three carry the same rows and the same row references, and `--ingest` reads
any of them. That was the requirement rather than an extra: a pack a reviewer
cannot return is a document, and a document is what the build already had.

**The spreadsheet** has six sheets. Read me, with the facts and the allowed
decisions. Pages. Claims. Recommendations and Measurements, each with a Decision
column carrying a dropdown, a name column and a Note column for amended wording.
Progress, which counts the decisions with formulas so the reviewer can see how far
they have got while still working in the file.

Each fillable sheet carries one filled example row, marked `EXAMPLE`. It cannot be
read back, because the row reference pattern will not match it, and the progress
formulas start below it so it is not counted.

**The Word file** is landscape throughout. A recommendation is a whole sentence,
and in a portrait column it wraps to four lines, which is what makes an eighty
five row table unreadable. Arial 10pt, the four tables with fixed cell widths,
and the Decision and Reviewer cells empty.

## Why python-docx rather than docx-js

The available guidance prefers docx-js for creating a Word file. It was not used,
for two reasons.

The return path decides it. docx-js cannot open an existing document, so reading a
filled pack back would need a second library anyway, and the pack would have two
dependency stories instead of one.

Every tool in `tools/` is Python. Adding a Node toolchain for one output format,
in a repository with no Node anywhere else, costs more than it saves.

## Two things found while verifying

**python-docx writes a schema-invalid settings.xml.** Its shipped default template
carries `<w:zoom w:val="bestFit"/>`, and the schema requires `w:percent` on that
element. Word tolerates it; a strict reader does not. Every file python-docx
writes has this fault. The generator now sets the attribute before saving, and
the document validates clean.

**LibreOffice does not work in this build container.** It could not recalculate
the workbook, timing out at 26 seconds and again at 179. It could not convert the
Word file to PDF, and it could not convert a one line plain text file either, so
the failure is its own rather than the files'.

Two consequences, both recorded rather than worked around:

The workbook's formulas are written without cached values, because nothing here
can compute them. `fullCalcOnLoad` is set instead, which Excel, LibreOffice and
Google Sheets all honour on open. The formula ranges are checked by a test rather
than by recalculation, since a COUNTIF over the wrong rows evaluates cleanly and
reports the wrong number.

The Word file was never rendered and looked at. It is verified structurally
instead: XSD validation passes, and the orientation, page size, font, table shapes
and column widths are read back and asserted. That is weaker than looking at it,
and it is what this environment allows.

## Why `--all` does not generate them

Both formats embed a timestamp, so two identical runs differ byte for byte.
Generating fifty binaries on every run would churn the repository and make
`--check` meaningless for them. `--all` stays markdown only, and a chapter is
named when its pack is going out.
