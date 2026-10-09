# Decision 010: publication QA, the fifth gate

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Applied |
| Closes | Build status item EV-11 |
| Source | Chapters 13, 14 and 15 of the Master Operations Handbook, under decision 009 |

## The question put

> Build publication QA as a fifth gate, checking SEO title, meta description,
> slug and image alt text? No page carries those fields yet, so building the
> gate means adding the fields to the brief first.

Answered yes.

## What the handbook asks for

Chapter 13 names five QA tiers. The pipeline had four.

| Tier | What it checks | Where it lives |
|---|---|---|
| 1 | AI generation | Agent 1, Generator |
| 2 | Assistant editorial review | Agent 3 and the style gate |
| 3 | Source verification | Agent 2, which has never run |
| 4 | Consultant review | The review pack, awaiting a consultant |
| 5 | Publication review | New. `tools/publication_qa.py` |

Chapter 13 says publication QA "checks formatting, SEO, links, images, alt text,
disclaimers, metadata and page status". Chapter 14 says every page requires an
SEO title, a meta description, a slug, an H1, an H2 structure, FAQs, related
articles, internal links and image alt text.

Links, HTML structure and chrome drift were already checked by
`tools/check_site.py`, which runs over the same files, so the new gate does not
repeat them. FAQs are checked by the style gate under decision 009. What nothing
checked before is the metadata a search engine and a screen reader read.

## The nine rules

| Rule | What it requires |
|---|---|
| PUB-001 | An SEO title, 15 to 60 characters, ending in the site suffix. The homepage leads with the brand instead |
| PUB-002 | A meta description, 70 to 160 characters, ending in a finished sentence |
| PUB-003 | A canonical link that agrees with where the file sits, and a lower case hyphenated slug |
| PUB-004 | Exactly one H1, and a heading ladder that never skips a level |
| PUB-005 | Alt text on every image |
| PUB-006 | The educational and not a substitute statement |
| PUB-007 | At least one internal link, and a link upwards out of its own directory |
| PUB-008 | Charset, viewport, description, canonical and theme colour |
| PUB-009 | A title and a description unique across the site |

Every bound lives in `pipeline/config/site.json`, so the numbers are
configuration. The handbook states none of them; they are the ordinary search
result display limits, and that is said in the file.

## Where the fields came from

The question assumed the fields would have to be written by hand for 116 pages.
They did not.

**Meta description.** Every article already opens with a two line summary
written for the reader, and 97 of 100 fitted 70 to 160 characters with nothing
done to them. Three did not and now carry a written description in
`render_targets.json`.

This also fixed a real defect. The renderer had been emitting
`doc["summary"][:160]`, a hard truncation that cut sentences mid word. PUB-002
fails any description that does not end in a full stop, so that cannot return.

**SEO title.** No page title exceeded 60 characters. Twenty pages shared a
title with another page, because the architecture gives Section 2 pages short
names inside their chapters: five called Surgical Anatomy, four called Gross
Anatomy, three called MRI Anatomy. The H1 belongs to the architecture and cannot
change. The title tag is a separate field, so a colliding page now carries its
chapter in it: `Surgical Anatomy, ACL | KneeSchool`.

The collision set is computed from the work by `tools/render_site.py`, not
listed by hand, so a new page that collides is disambiguated the day it is
written.

**Slug and canonical.** Every page now carries
`<link rel="canonical">` built from its own path. The base URL is one line of
`site.json`, taken from chapter 1 of the handbook, which names the platform
KneeSchool.com. If the live domain differs, that is the line to change.

**Alt text.** No page carries an image, so PUB-005 passes on all 116 by having
nothing to check. It is in place so the first image cannot arrive without alt
text.

## Result

116 pages, 0 findings. Two pages needed fixing to get there: the homepage title
convention, which was right and the rule was wrong, and the Junior Academy
landing page, whose description was six words.

## What publication QA still cannot check

Chapter 13 lists page status under this gate. The site shows a pipeline status
note on every article page, but it is not reconciled against the tracker's
`publication_status` field, because the tracker is a seed file that no process
updates yet. When the tracker becomes live, PUB-010 is that reconciliation.
