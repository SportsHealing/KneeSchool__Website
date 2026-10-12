# Decision 023: the examination template, and the accuracy figures it refuses

| Field | Value |
|---|---|
| Date | 11 October 2026 |
| Decided by | Claude, applied and open to revision |
| Status | Applied. Chapter 4.1 built on it |
| Builds on | Decision 014, which invented the biomechanics and landmark papers templates the same way |
| Changes | `examination` template added, `page_type_map.json` no longer marks it variant pending, new rule ACC-001, five new body section headings |

## Why a decision was needed

Section 4 is 227 pages and every one of them is an examination page. The type
map marked `examination` as `variant_pending` and pointed it at the **anatomy**
template, whose headings are Structure and Location, Relations, Blood Supply and
Innervation, Function, Clinical Relevance.

A page called The Lachman Test has no blood supply. This is the same situation
decision 014 found in Section 3, flagged in the same file, and it came due the
moment Section 4 started.

## The template

| Slug | Heading |
|---|---|
| `what_it_tests` | What It Tests |
| `how_it_is_performed` | How It Is Performed |
| `what_a_positive_means` | What a Positive Means |
| `how_good_it_is` | How Good It Is |
| `where_it_misleads` | Where It Misleads |

Rule: ordered subset per tier; How Good It Is from MRCS upwards.

The shape follows how a test is actually taught and, more importantly, how it is
actually used. State what structure or motion the test interrogates. Describe
the manoeuvre. Say what a positive finding licenses you to conclude, which is
narrower than what it is usually taken to mean. Say how good the test is. Then
say where it misleads.

**Where It Misleads is the section that earns its place.** A knee examination
test fails in patterned, nameable ways: an effusion limits a Lachman, guarding
abolishes it, an anaesthetised knee exaggerates it, and a chronically lax knee
reads differently from an acutely injured one. A template with nowhere to put
that produces pages that teach the manoeuvre and omit the thing that makes a
clinician wrong.

This template serves both kinds of page in the section. A specific test page
uses all five sections. A principles page such as 4.1.5 Common Examination
Pitfalls uses What It Tests and Where It Misleads and leaves the middle out,
which the ordered subset rule allows.

## ACC-001, and why accuracy figures are refused

Section 4's content is tests, and the obvious thing to write about a test is its
sensitivity and specificity. This build has no source access, so those figures
would come from memory.

Decision 022 made the argument for citations and it transfers exactly:

- **The comparative pattern is recalled robustly** and is standard teaching.
  Lachman beats anterior drawer. The pivot shift is specific and insensitive.
  McMurray is specific and insensitive. Each of those is one fact held with its
  reasoning attached, and a reader who knows the subject can check it.
- **A specific percentage is recalled alone.** Nothing in the pattern constrains
  it. A wrong value looks exactly like a right one to the writer and to the
  reader.

So ACC-001 refuses a sensitivity, specificity, predictive value, likelihood
ratio or area under the curve written as a number, on any page whose type is
`examination`. The page states the comparison instead.

**This is a fail rather than a warn**, which ATTR-002 is not, because of what
the error does. A wrong anatomical figure misleads. A wrong sensitivity changes
what a clinician does next with a negative test, and a test believed more
sensitive than it is produces a missed diagnosis rather than an inaccuracy.

Angles, distances and grades are untouched. Thirty degrees of flexion for a
Lachman is part of the technique rather than an accuracy claim, it is not a
fabrication risk of this kind, and it is registered as a figure under decision
006 like every other measurement on the site.

## What this costs

Section 4 will teach every test without quoting its accuracy, which is a worse
page than one with correct figures and a better page than one with invented
ones. A reviewer with access to the literature can add them, and the pages are
written so the figures slot into How Good It Is without restructuring anything.

The deeper cost is that a comparative claim is harder to check than a number.
"More sensitive than" is an assertion a reviewer must agree with rather than
look up, so the review burden moves from verification to judgement. That is a
real loss and it is preferable to the alternative.
