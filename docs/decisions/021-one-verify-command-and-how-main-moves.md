# Decision 021: one verify command, and how `main` moves

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Claude, under the client's instruction of 10 October 2026 |
| Status | Applied |
| Changes | New `Makefile` with a `verify` target, new `tools/lint_site.py` and `tools/check_clean.py`, `--prose-check` on `crossrefs.py`, a CI workflow, `condition_met` fixed, 17 briefs completed, README branch policy rewritten, 12 tests |

## The instruction

> do whatever you recommend to make Sure that the management of the repo,
> "main" and pull requests is as you desire

Given after two things went wrong in the same hour: `main` sat a day behind with
no mechanism to notice, and pull request #1 was merged while a fix was being
pushed, so the fix missed the merge.

## What was actually wrong

The gates were five separate commands held in one person's head. That is the
root of everything below.

- **A contributor could not run them.** There was no list anywhere. The README
  pointed at `make -C pipeline test` and said 68 tests, which was 185 short.
- **CI could not run them**, because there was no CI. GitHub's "mergeable" means
  only that a branch has no conflict, so pull request #1 was merged carrying 26
  commits and 276 pages with nothing checking it. The only verification was me
  saying the gates passed.
- **The style gate had never run over the whole site.** It ran per chapter,
  through a script outside the repository, at the time that chapter was written.
  Nothing ever asked whether a page written on Tuesday still passed on Friday.

## What was built

`make verify`, which is the test suite and then six gates, stopping at the first
failure:

| | |
|---|---|
| `lint_site.py` | the deterministic style gate over every page with a brief and a draft |
| `check_site.py` | links, chrome, fonts, stylesheet |
| `publication_qa.py` | the fifth gate, chapter 13 of the handbook |
| `crossrefs.py --check` | cross link labels |
| `crossrefs.py --prose-check` | prose references against the architecture |
| `review_pack.py --check` | the packs against the registers |
| `check_clean.py` | whether the tree changed, which it must not have |

Two of those are new, `lint_site.py` and `check_clean.py`, and `--prose-check`
is new. The prose report used to print the number of references pointing at a
non existent page and exit zero, so the one check that catches a link to a page
that does not exist could not fail a build.

The CI workflow runs `make verify` rather than restating the steps, and a test
asserts it does not name a gate of its own. Two commands meant to agree and
written out separately drift.

`check_clean.py` runs last and asks git whether the tree changed. Every gate
before it is read only, so a change means something calling itself a check is
writing. Twice it was: see the commit before this one.

## What running it over the whole site found

Three faults, all of them pre-existing, none of them visible to a per chapter
run.

**Eight style failures on 1.1.3, a page published on 8 October.** It carries
flexion angles and FIG-001 forbids figures. That rule is conditional on
`figures_allowed == false` and the brief did not have the key at all.

**The condition evaluator read a missing key as false.** Silence in a brief was
being treated as an answer, so seventeen briefs silently acquired a rule written
for Section 0's fees and entry requirements. A conditional rule now applies only
when the brief states the condition.

**Seventeen briefs were stale.** They were generated before the generator set
`figures_allowed` and were never regenerated. The key has been added to each,
and nothing else: regenerating them wholesale would have raised published word
count caps from 1800 to 2050 and, on 1.2.3, discarded curriculum tags and tier
notes added by hand for the pilot.

The second and third faults compounded into the one that matters. FIG-002, which
requires every measurement to be registered, is conditional on the same key
being **true**. So on all seventeen pages the measurements were in neither gate
and in no register. 1.1.3's five flexion angles are now registered as
`UNVERIFIED_FROM_MEMORY`, which is where every other measurement on the site has
been for days. The site total went from 352 to 357.

## How `main` moves, from now on

1. **Only through a pull request.** Not a direct push, not a fast forward from a
   terminal. The pull request is the record of what was brought across and when.
2. **A pull request merges only when `verify` is green on its head commit.**
3. **A merged pull request is finished.** Follow up work is a new pull request
   from the same working branch.

Written into the README, because an arrangement held only in a conversation is
the thing that failed this morning.

## Found afterwards, and it changes rule 1

Reading the Actions history to confirm the first `verify` run turned up a second
workflow that had been running all along: GitHub Pages has been building and
publishing this repository on every push since late September, 61 successful
runs, with a `CNAME` in the root pointing kneeschool.com at it.

Every one of those runs was on `claude/great-meitner-kofr7g`. The site publishes
from the working branch, so each push goes live immediately and unreviewed. The
README said `main` is "the stable copy, what the site is published from", and
that was describing an intention rather than a configuration.

The safeguard held. `discoverable` is false, so robots.txt disallows every
crawler and every page carries a noindex directive. Decision 015 has been doing
real work rather than sitting ready.

Rule 1 above is therefore incomplete as written. `main` moving only through a
pull request achieves nothing while the live site is served from somewhere else.
The Pages source has to point at `main`, and that is a setting in the
repository's own interface which cannot be reached from here: the Pages API is
refused through this session's proxy. Recorded as EV-21 for the client to change.

Until it changes, the rules above govern what is reviewed and the working branch
governs what is live, which is exactly backwards.

## What was considered and not done

**Branch protection on `main`.** It would enforce rule 1 rather than stating it.
Not set, because it needs admin rights on the repository and the client should
decide whether to lock themselves out of a direct push. It is one setting in
GitHub if they want it, and the rules above are the policy either way.

**Regenerating the seventeen briefs.** Rejected above: it would have changed
published pages' word count caps and lost hand written fields.

**Running the gates on a schedule as well as on push.** Not yet. Nothing about
this repository changes without a push, so a nightly run would only re-verify
the same commit.
