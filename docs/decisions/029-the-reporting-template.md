# Decision 029: the reporting template

**Date:** 25 October 2026
**Status:** Applied
**Supersedes nothing. Discharges a cost recorded in decision 028.**

## What decision 028 said would happen

Decision 028 gave Section 5 the imaging template and listed four kinds of page
it had to stretch across. One of them it flagged:

> **5.20 reporting.** How It Is Acquired reads as how the report is produced.
> This is the loosest fit in the set and is the first thing to revisit.

and, under Cost:

> The reporting chapter is the weakest fit and will probably want its own type.
> Recording that now is cheaper than discovering it at page 200.

This is that type. Section 5 is finished at 216 of 224 published pages, so the
revisit happens at the end of the section rather than in the middle of it, which
is the cheapest moment it could have happened.

## What was actually wrong

Two of the six imaging sections collided with their own meaning.

| Imaging heading | What chapter 5.20 used it for |
| --- | --- |
| What It Shows | What the report is for |
| How It Is Acquired | How the report is built |
| **What Normal Looks Like** | **What a good report looks like** |
| **What Abnormal Looks Like** | **What a poor report looks like** |
| How Good It Is | How good reporting is |
| Where It Misleads | Where reports mislead |

Everywhere else in Section 5, normal and abnormal describe a knee. On these
eight pages they described a document. A reader arriving at 5.20.5 from 5.11.2
met the same heading meaning something else, with nothing on the page to say so
except a paragraph on 5.20.1 that told them how to read the chapter:

> On the pages of this chapter the six template headings are read as questions
> about the report rather than about an image.

A translation note standing in for a template. It worked, and it put the burden
on the reader to carry an instruction from one page across seven others.

The other four headings were strained rather than wrong, and two of them were
right as they stood.

## The new type

| Section key | Heading |
| --- | --- |
| `what_the_report_is_for` | What the Report Is For |
| `how_the_report_is_built` | How the Report Is Built |
| `what_a_good_one_looks_like` | What a Good One Looks Like |
| `what_a_poor_one_looks_like` | What a Poor One Looks Like |
| `how_good_it_is` | How Good It Is |
| `where_it_misleads` | Where It Misleads |

Six sections, ordered subset per tier, same word count band as imaging.

The last two are the imaging keys unchanged, deliberately. `how_good_it_is`
carries a floor of MRCS in `section_tier_rules` from decision 023, and reusing
the key rather than renaming it keeps that floor reaching this template without
a second rule to maintain. They are also the two headings that were right
already, which is why there was nothing to rename.

## What did not change

**The content.** The eight pages were already written to these six questions,
because the translation note is what they were written against. The change is
the headings, the `page_type`, and the join between them. No page's argument,
ordering or references moved.

**The registers.** 526 figures and 3,294 unsigned positions, both unchanged.
The chapter carries no figures and its positions are the same sentences.

## Four joins that had to move together

A page type is not one file. Missing any of these would have left a green build
and a wrong site.

1. **`tools/extract_section5.py`.** `pages_5.json` is generated and a test holds
   the committed map against a rebuild, so editing the map by hand would have
   failed that test on the next run. The extractor already special cased chapter
   5.21 as `landmark_papers`; 5.20 is now the same shape of case.
2. **`pipeline/config/page_type_map.json`.** The join from the architecture's
   fine grained `page_type` onto a template. Without it the linter resolves the
   type to nothing and fails every page with "the handbook defines no such
   template".
3. **`pipeline/config/article_template.json`.** The template, and the four new
   headings in `body_section_headings`. A section key with no heading renders as
   its own key.
4. **`pipeline/config/lint_rules.json`.** ACC-001 named `examination` and
   `imaging`. Splitting a chapter out of `imaging` would have dropped it out of
   the accuracy ban silently, with every gate still green. This is the one
   genuine risk the change carried and it is the one a test now holds.

## Cost

The same cost decision 028 recorded, one template later. No editorial authority
has confirmed these six sections. The shape is this process's invention, as the
imaging and examination templates' shapes are, and a reviewer should know it.

What is different is that this template was derived from eight written pages
rather than proposed ahead of them, so its sections are a description of what
the chapter turned out to need rather than a guess at what it would.

Nine tests in `pipeline/tests/test_architecture.py` hold the four joins, the
heading rename across all three stage files of all eight pages, and the accuracy
ban's reach.
