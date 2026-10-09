# Decision 008: the architecture numbering is canonical

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Applied |
| Closes | Build status item EV-9 |

## The instruction

> Architecture numbering is canonical; all files attached here.

## What was in conflict

Two documents numbered the same academies differently.

| Academy | Master Operations Handbook | Publishing architecture |
|---|---|---|
| Anatomy | Chapter 6 | Section 2 |
| Conditions | Chapter 9 | Section 6 |

Nothing in this repository ever used the handbook numbering, so "Section 6" was
ambiguous between documents while both stood.

## The ruling

The publishing architecture wins. `Section 2` means Anatomy Academy. `Section 6`
means the Conditions Library. Page ids are `section.chapter.page` in architecture
numbering throughout: configuration, briefs, tracker, cross links, prose and
file paths.

## What changes

Nothing in the build. The repository already used architecture numbering
everywhere, so the ruling confirms the existing state rather than altering it.
That is the useful outcome: no migration, and the ambiguity is closed.

## What it means for the other documents

Where the Master Operations Handbook or either playbook draft refers to a
chapter number, read it as that document's own internal chapter, not as a page
id. Chapter references inside those documents stay as written; they are not
rewritten into architecture numbering, because the documents are historical
records and editing them would destroy the audit trail.

The style gate already distinguishes the two. `XREF_WORD` in
`pipeline/functions/style_lint/linter.py` matches `chapter 6` and `section 6` as
cross references and exempts them from the measurement rules, whichever document
the writer had in mind.
