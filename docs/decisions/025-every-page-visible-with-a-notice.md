# Decision 025: every produced page is visible, and the site says it is unfinished

| Field | Value |
|---|---|
| Date | 12 October 2026 |
| Decided by | Client, 12 October 2026: "I want to see all produced pages on the site; we can put a disclaimer on the site as in progress" |
| Status | Applied |
| Changes | Clinical Examination Academy added to the ribbon, site wide work in progress notice, two new tests, `discoverable` unchanged |

## The instruction

> I want to see all produced pages on the site; we can put a disclaimer on the
> site as in progress

Two things, and the first one turned out to be a real defect rather than a
request.

## What was wrong

**Section 4's 65 pages were unreachable by browsing.** They passed every gate on
this site. Each one had an inbound link, so an orphan check found nothing. But
nothing outside the `examination/` directory linked into it, and the Clinical
Examination Academy was never added to the ribbon, so the whole section was an
island with no path into it from anywhere a visitor starts.

They were reachable only by typing a URL. Verified against `main` before the
fix: no file outside `examination/` contained a link to any page inside it.

The ribbon lives in `tools/site_chrome.py` and lists the Anatomy Academy and the
Biomechanics Academy under Reference. A third section was built, published and
indexed without anybody adding the fourth line. That is a one line omission and
it hid 65 pages and roughly 70,000 words.

**No gate checked for it**, which is the part worth recording. Six gates, 275
tests, and a whole section could be invisible. The orphan-style check that would
have been the obvious guard also fails here, because every page had a link: the
island was internally well connected. The property that matters is reachability
from the homepage, not the existence of an inbound link.

The client found it by asking to see the pages.

## What was done

**The ribbon.** One line, under Reference, between the Biomechanics Academy and
the Conditions library. All 384 published pages are now reachable from the
homepage by clicking.

**The notice.** A site wide band above the navigation on every page, defined once
in `site_chrome.py` so it cannot drift. It says three things and no more:

> **Work in progress.** This site is being built in the open. No page on it has
> yet been reviewed by a clinician, every page says so, and nothing here is
> medical advice or a substitute for seeing someone about your knee.

It links to the build status page. It is deliberately not sticky: it should be
read once at the top rather than following a reader down a page it has nothing
further to say about. It uses the warning colour rather than the gold, because
this is a caution and not a label.

Every page already carried its own status line under the publication QA gate.
This is the one a visitor sees before reading anything.

**Two tests**, because the gates missed this and should not miss it again.

- `EveryPageIsReachableByClicking` walks the link graph from `index.html` and
  fails if any published page is not reached. Checked by removing the ribbon
  line: the test fails, and passes when it is restored.
- `EveryPageCarriesTheBuildNotice` checks all 402 HTML files, because a
  disclaimer on most pages is not a disclaimer.

## What was not done

**`discoverable` is still false.** Every page still carries a `noindex`
directive and `robots.txt` still disallows every crawler.

The instruction was to make the pages visible on the site and to add a
disclaimer, and both are done. Making them *findable by search engines* is a
different act: it puts 2,139 unsigned clinical recommendations and 448 unchecked
measurements in front of people searching for knee advice, who did not follow a
link from anyone who could warn them.

The disclaimer makes that defensible in a way it was not before. It is still the
client's call and not this process's, and decision 015 left open who owns the
flip. It is recorded here as asked and not taken.

## The cost of what was done

The pages are now browsable by anyone with the address, which is what was asked
for and is what the notice exists to qualify. A visitor who ignores the notice,
the per page status line and the reference note on every page can still read an
unreviewed clinical recommendation and act on it. Three notices is the most this
site can do short of review.
