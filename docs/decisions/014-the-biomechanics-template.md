# Decision 014: the biomechanics and landmark papers templates

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Claude, applied and open to revision |
| Status | Applied. Chapter 3.1 built on it |
| Builds on | Decision 003, which invented the Section 0 templates the same way |
| Holds | Page 3.1.8 and the other ten landmark papers pages |

## Why a decision was needed

Section 3 is 188 pages and every one of them has a page type the template file did
not cover. 177 are `biomechanics` and 11 are `landmark_papers`. Both were marked
`variant_pending` in `page_type_map.json`, which meant they borrowed the anatomy
template: Structure and Location, Relations, **Blood Supply and Innervation**,
Function, Clinical Relevance.

Those headings are wrong for the subject. A page called What Is Biomechanics?
has no blood supply. The map had flagged this as a decision waiting to be made,
and Section 3 is where it came due.

## The biomechanics template

| Slug | Heading |
|---|---|
| `the_principle` | The Principle |
| `at_the_knee` | At the Knee |
| `what_changes_it` | What Changes It |
| `how_it_is_measured` | How It Is Measured |
| `clinical_relevance` | Clinical Relevance |

Rule: ordered subset per tier; How It Is Measured from medical student upwards.

The shape follows how the subject is taught: state the mechanical principle,
show it in this joint, name the variables that change it, say how it is measured
and what the measurement is worth, then say what it means clinically.

**How It Is Measured is the section that earns its place.** Biomechanics is a
field where a cadaver figure, a laboratory figure and an in vivo figure are three
different kinds of number, and they frequently disagree. A template that has
nowhere to say so produces pages that quote figures as though they were settled.

## The landmark papers template

| Slug | Heading |
|---|---|
| `what_the_question_was` | What the Question Was |
| `what_was_done` | What Was Done |
| `what_it_showed` | What It Showed |
| `what_it_changed` | What It Changed |
| `what_to_read_now` | What to Read Now |

Defined, and not used. See below.

## Page 3.1.8 is held, and so are the other ten

Eleven pages in Section 3 are Landmark Papers pages. Their subject is named
studies.

This build environment cannot retrieve a paper. It has no PubMed, no journal, no
textbook, and the Operations Handbook names an invented citation as a critical
failure, the one failure it grades that way. A page whose whole subject is
specific papers, written by a process that cannot open one, would either carry
citations recalled from memory, which is the failure, or carry no paper, which is
not the page the architecture asked for.

So the template exists and the pages wait. The same treatment as the three
Section 0 pages held under decisions 003 and 004: written where they can be
written, held where they cannot, and recorded rather than quietly dropped.

The other ten are 3.17.1 to 3.17.10, the whole of chapter 3.17 Landmark
Biomechanics Papers.

**Corrected on 10 October 2026.** This decision originally named the other ten as
3.2.11, 3.3.15, 3.4.12, 3.5.11, 3.6.12, 3.7.12, 3.8.11, 3.9.11, 3.10.10 and
3.11.9, on the assumption that every chapter closes with a landmark papers page.
That assumption was not checked against the architecture and it is wrong. None of
those ten ids exists. The architecture puts one landmark papers page at the end of
chapter 3.1 and collects the rest into chapter 3.17, by subject rather than by
chapter: ACL, PCL, meniscal, medial, posterolateral, patellofemoral, osteotomy,
arthroplasty, the Imperial contributions, and future research priorities.

The practical effect is that chapters 3.2 to 3.16 hold nothing back. Chapter 3.2
is complete at ten pages and chapter 3.3 at fourteen, rather than complete except
for a held page that was never in the plan.

## Three changes the chapter forced

**The FAQ allowance now applies to any word band.** Decision 002 added 250 words
when the patient tier is present, inside the one and two tier bands. The
allowance belongs to the FAQ block rather than to the tier count: the first four
tier page with a patient block came out at 2,034 words against a ceiling of
1,800, and the FAQ block was the difference. The allowance now applies wherever
the patient tier appears.

**Tier order is normalised every time a brief is generated.** One page in the
architecture lists its tiers as medical student, MRCS, FRCS, patient. A brief
carrying that order produces an article whose depth dial runs backwards. The
order is now sorted against the template on every brief rather than only when a
tier override applies.

**A fourth emitter.** `emit4.py` reads the body section order from the template
by page type rather than holding its own list, so it serves both new types and
any future one. The three earlier emitters each hard coded the anatomy order.

## The junior closing message, and a question

The handbook attaches the junior closing message to symptom or injury content.
The gate drives that off page type, and decision 003 exempted four Section 0
types where the message read as a non sequitur.

Chapter 3.1's junior blocks are about physics. On 3.1.1, What Is Biomechanics?,
the message "if any of this sounds like something happening to you, speak to a
parent, teacher, coach or doctor" follows a paragraph about levers.

It is included anyway. Adding a fifth page type to a client rule's exemption list
is not a call to make quietly, and the cost of including it is one sentence.

**Settled on 10 October 2026.** The client's answer is to leave it as is, so
`biomechanics` does not join the exemption list and the message stays. In
practice it appears on chapter 3.1 alone, since no page in 3.2 or 3.3 carries a
junior tier, and the architecture gives the rest of Section 3 three professional
tiers. The oddity is therefore confined to the five junior blocks in 3.1, and it
reads correctly on two of them.

## Questions

1. ~~Should `biomechanics` join the page types exempt from the junior closing
   message?~~ Answered on 10 October 2026: it stays as it is. See above.
2. Are the eleven Landmark Papers pages worth attempting from memory with every
   claim registered as unverified, or do they wait for source access like the
   evidence verification stage itself? Held is the current answer.
