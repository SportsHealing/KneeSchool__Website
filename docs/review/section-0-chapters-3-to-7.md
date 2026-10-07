# Consultant review pack: Section 0, chapters 0.3 to 0.7

| Field | Value |
|---|---|
| Section | 0 Junior Academy |
| Chapters | 0.3 Careers, 0.4 Medical School Entry, 0.5 Young Investigators, 0.6 Certificates, 0.7 For Teachers, Coaches and Parents, plus 0.1.6 |
| Pages | 27 written, 24 published. Section 0 is 38 written, 35 published |
| Page types | careers 6, study_skills 11, teacher_resource 6, assessment 4 (1 published) |
| Tier | Junior on 22 pages, Patient on the five chapter 0.7 pages |
| Held unpublished | 0.6.2, 0.6.3 and 0.6.4, at the client's instruction. All of chapter 0.6 except the certificate |
| Style gate | All 27 pass. Zero failures, zero warnings |
| Evidence verification | **Did not run on any page** |
| Reference lists | **None** |
| Words | 17,961 |

## What changed since the last pack

The last pack said these 27 pages were blocked, because the handbook defines no
template for any of their four page types. That is resolved, by ruling rather
than by discovery.

**Decision 003** defines four templates locally, in `article_template.json`,
each marked `source_of_truth: decision 003` so a reader of the config can tell
which templates the handbook owns and which this build does. The section orders
are in `docs/decisions/003-section-0-page-templates.md`.

If you reject an order, the prose survives. Only the heading sequence in the
config and the section keys in the content modules change.

**Decision 002 gained an FAQ allowance.** The five chapter 0.7 pages carry the
patient tier, which obliges an FAQ block of three to five questions. On a one
tier page that is around 250 words of structure nobody is allowed to shorten.
Two pages failed the 900 word ceiling on that overhead alone, with no padding in
them. The ceiling now rises by 250 where the patient tier is present.

## The rule that shapes these pages most

These chapters invite entry requirements, admissions test scores, fees,
deadlines and competition ratios. All of those change annually, and nothing
could be verified, because no source retrieval was available.

**No page here states an entry requirement, a test score, a fee, a deadline or
an application statistic.** Where a figure would normally sit, the page names
the body that publishes it and tells the reader to check there. The named bodies
are the General Medical Council, the Royal College of Surgeons, the British
Orthopaedic Association, the Medical Schools Council, UCAS, the UCAT Consortium,
Cochrane, NICE and the Information Commissioner's Office.

**Confirmed by the client. This is closed.** No entry requirement, test score,
fee, deadline or application statistic goes on a Section 0 page, and a reviewer
should not add one. Please do not raise it.

## What you are being asked to confirm

1. **The four section orders.** Decision 003. This is the cheapest thing to
   change now and the most expensive later, because 294 further pages in
   sections 10 to 15 will use at least two of these templates.
2. ~~The no figures rule.~~ Confirmed by the client and closed. See above.
3. **Accuracy on the training pathway.** Chapter 0.3 describes the route from
   school to consultant, and chapter 0.3.4 describes MRCS and FRCS. You have
   been through both. Nobody else reviewing this has.
4. **Eight published pages describe a feature the site cannot do.** Each says
   so on the page. They are listed on `about/status.html` and in
   `docs/build_status.json` as PG-1 to PG-8.

This question has been answered, and the answer was consistent. Three of the
   four chapter 0.6 pages are written, passed the gate, and are held
   unpublished: Future Surgeon Challenge, School Leaderboards and Digital
   Badges. A page whose whole subject is a feature that does not exist was
   judged not worth the shelf space. The syllabus shows all three as coming
   soon, and the drafts are in `pipeline/runs`.

   The rule that came out of it, worth applying to later sections: **a page may
   say a feature is not ready, but a page whose only subject is a feature that
   is not ready does not publish.** That is why 0.7.2 Classroom Slide Decks is
   still live and the badges page is not. 0.7.2 gives a teacher a route without
   the files; the badges page gave nobody anything.

   The one page this leaves worth a second look is 0.6.1 Knee Explorer
   Certificate. It survives because a teacher can award it today, and chapter
   0.6 is now a single page. Is one certificate enough to keep the chapter, or
   should it move into 0.1?

## Three pages to read first

**0.7.4 Supporting an Injured Young Athlete.** The page most likely to change
what a reader does. It is written for a parent in the weeks after a child's knee
injury, and it refuses to give a timescale, a diagnosis or a return date. It
gives five questions to ask the clinical team instead, and it says plainly that
losing sport for months is a loss and that persistent low mood needs the GP.
Judgement needed on two things: whether the five questions are the right five,
and whether refusing timescales is helpful or merely frustrating.

**0.7.3 Coaching Safely.** Written for a youth coach, and the page where the
line between coaching and treating has to hold. It says: stop the athlete, do
not test the joint, tell a parent the same day. It lists five findings that end
a session. It states that return to play is a clinical decision. Check the five
findings, and check that nothing on it reads as permission to assess.

**0.3.5 Women in Orthopaedics.** A framing judgement, in the same way 0.2.4 was
in the last pack. The page states that orthopaedics has one of the smallest
proportions of women of any surgical specialty, gives three explanations from
the literature, and says none of them is about ability. It carries no figure,
because the figure moves and could not be checked. It names no individuals,
because a profile of a real person needs that person's consent. Both of those
make the page weaker and both were deliberate.

## What has not been checked

Nothing on these 27 pages has been verified against a source. Not one claim
about an examination, an entry route, a professional body or a piece of
education policy. The verification stage could not run, and this pack is
standing in for it.

The claims are listed per page in `pipeline/runs/<page_id>/draft_v1.handoff.json`
under `claims_needing_verification`. They are mostly checkable in an afternoon
against the bodies named on each page, which is a different proposition from
verifying a clinical claim.

## Where the pages are

| Chapter | Pages | Published under |
|---|---|---|
| 0.1.6 | Curriculum Links | `junior/curriculum-links.html` |
| 0.3 | 6 careers pages | `junior/` |
| 0.4 | 6 study skills pages | `junior/` |
| 0.5 | 5 study skills pages | `junior/` |
| 0.6 | 4 assessment pages, 1 published | `junior/` |
| 0.7 | 5 teacher resource pages | `junior/` |

All 38 are listed on `levels/junior.html`. Thirty five are links; the three
held chapter 0.6 pages show as coming soon. Chapter 0.7 is also reachable from
the Learn menu, because a teacher is not going to look for adult material under
a heading that says Junior Academy.
