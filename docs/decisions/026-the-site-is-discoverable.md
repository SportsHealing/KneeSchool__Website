# Decision 026: the site is discoverable, and who decided that

| Field | Value |
|---|---|
| Date | 12 October 2026 |
| Decided by | **The client.** Their words: "yrs merge all of them we will take responsibility and add a disclaimer that this is a site in progress" |
| Status | Applied |
| Supersedes | Decision 015's posture of published and not publicised |
| Changes | `discoverable` true in `site.json`, every page's noindex directive removed, `robots.txt` allows every crawler, `sitemap.xml` generated for the first time, four tests rewritten |

## What changed and who owns it

`discoverable` has been false since the site went up. Every page carried a
`noindex` directive and `robots.txt` disallowed every crawler, so the site was
published and not findable. Decision 015 recorded that as the client's position
of 10 October 2026 and left open who would flip it.

It was raised with the client three times in one session on 12 October 2026, each
time with the consequence stated: flipping it makes search engines index 2,139
unsigned clinical recommendations and 448 unchecked measurements, and puts them in
front of people searching for advice about their knees who did not follow a link
from anyone who could warn them.

The client's answer was to take responsibility and to add a disclaimer. Both
halves of that are now true: the responsibility is recorded here in their words,
and the disclaimer is the work in progress band that decision 025 put on every
page.

**This decision is the client's and is recorded as theirs.** It is the one
decision in this directory where that distinction is the point.

## What is now true

- `site.json` has `discoverable: true`
- No page carries a robots directive. Verified across all 402 pages.
- `robots.txt` reads `Allow: /` and names the sitemap
- `sitemap.xml` exists with 394 urls
- The work in progress band appears on every page, above the navigation
- Every page still carries its own status line: editorial draft, evidence
  verification did not run, not consultant reviewed, not for clinical use
- Every page still carries a reference note saying nothing on it was retrieved
  from a source

So a reader arriving from a search engine sees three separate statements that
this is unverified before they reach any clinical content. That is the most this
site can do short of review.

## A bug the flip exposed

`robots.txt` has named `sitemap.xml` since the day it was written, and the file
never existed.

That was harmless while every crawler was disallowed, because none of them read
`robots.txt` past the `Disallow`. The moment `discoverable` became true it was a
404 for every crawler that followed it, and the site would have been indexed
without the map it advertised.

Same shape as the other latent bugs here: correct under one setting, wrong under
the other, with nothing checking the setting it was wrong under. `apply_chrome.py`
now writes the sitemap beside the `robots.txt` that points at it, so the two
cannot disagree, and removes it if the site ever goes back to not discoverable.

## Four tests rewritten

The publication posture tests asserted the old world and would have passed a bad
flip.

- `test_the_site_is_currently_not_publicised` asserted the flag was false. That
  tested one moment rather than the mechanism. It now asserts the flag is a
  deliberate boolean with a recorded reason.
- `test_every_page_carries_the_directive` asserted `noindex` was present
  unconditionally. It now checks that the pages agree with the switch, whichever
  way it is set.
- The two PUB-010 rule tests used the live configuration, so one of them stopped
  exercising the rule the moment the flag changed. They now pass explicit
  configurations and cover both postures, and two more were added so each
  posture is checked for both a present and an absent directive.
- `test_the_sitemap_agrees_with_the_switch` is new, and would have caught the
  missing sitemap.

## What this costs, stated plainly

Indexing is not fully reversible. A page can stay in a search engine's cache
after it is removed from the site, so setting this back to false does not undo
it. That is why the default was the cautious one and why this needed a decision
rather than a commit message.

The material now findable has not been read by a clinician. The registers say
so, the status page says so, and every page says so. What protects a reader is
three notices and the client's judgement, and the first of those is weaker than
review.

Nothing else has changed. The review packs, the registers and the gates are
exactly as they were, and the work of getting a consultant through them is
unchanged by this decision.
