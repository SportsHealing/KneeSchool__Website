# Decision 019: the five patient factors

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Client, on 10 October 2026 |
| Status | Applied |
| Changes | `decision_factors` added to `article_template.json`, new lint rule DEC-001, consultant blocks on 3.11.9 and 6.1.1 extended, POSITION_VERBS extended again, 10 tests, 45 further recommendations registered |

## The instruction

> Also decision-making should always take into account the patients age and
> physiology, Medical comorbidities, demands on their knee, their own
> psychological state, ideas, concerns, and expectations

Given immediately after decision 018, which defined the consultant tier as a
balance argument. This decides what goes on the scale.

## The five factors

They are in `pipeline/config/article_template.json` under `decision_factors`,
with the keywords the gate uses, so the standard and the check cannot drift
apart.

| Factor | What it means |
|---|---|
| Age and physiology | Chronological age, skeletal maturity, tissue and bone quality, healing capacity |
| Medical comorbidities | What the patient's medical state does to operative risk, healing and rehabilitation |
| Demands on the knee | Occupation, sport, level, and the loads the patient will actually impose |
| Psychological state | Fear of reinjury, motivation, confidence, mental health, and what the patient does with the result |
| Ideas, concerns and expectations | What the patient believes is wrong, what they fear, and what they expect the operation to deliver |

The client's wording groups psychological state with ideas, concerns and
expectations. They are separated here because they do different work. A patient
can be psychologically robust and still expect something the operation will not
deliver, and the second is the commoner failure.

## The gate

DEC-001, warn severity. It reads the five factors and their keywords from the
template, takes the consultant block's text, and reports any factor the block
does not name.

It is scoped to a consultant block that carries clinical direction, detected the
same way POS-001 detects it. That scoping matters: 3.1.7's consultant block is
about whether a teaching programme should date its biomechanical figures. There
is no patient in it, and the rule correctly leaves it alone without anybody
listing an exemption by hand.

It warns rather than fails for POS-001's reason. Keyword matching can be
satisfied by a passing mention, so the rule can tell you a factor is absent and
cannot tell you a factor is addressed. It catches the omission, not the
treatment.

## What the rule found when first run

| Page | Factors absent |
|---|---|
| 3.11.9 | Medical comorbidities, psychological state |
| 3.1.7 | Out of scope, correctly |
| 6.1.1 | Medical comorbidities, psychological state, ideas, concerns and expectations |

Both pages framed their decisions on the knee and on the evidence. Neither had
the patient in them. 3.11.9 weighed slope, revision status and surgeon volume
and never asked whether the patient would trust the knee. That is the omission
this decision exists to stop.

Both now carry all five. 3.11.9 puts them in What Changes It alongside the
anatomical and surgical factors, which is the honest arrangement: slope and fear
of reinjury sit on the same list because they move the same decision.

## Verb list extended again

Eliciting a patient factor is clinical direction, so Take, Factor, Elicit,
Explore, Counsel, Ask, Involve, Record, Share and Agree were added to
POSITION_VERBS. Decision 018 extended the same list for weighing verbs. Two
extensions in one day is a sign the list is the wrong shape, which is noted
below rather than fixed here.

## What is not settled

Whether the five factors belong above the consultant tier. The FRCS and
fellowship blocks give clinical direction and frame choices, and the rule does
not reach them. Extending it would touch every professional page on the site and
should be a decision of its own rather than a side effect of this one.

Whether POSITION_VERBS should stay a verb list. It has now been extended twice in
one day, each time because a new kind of sentence was written that the list had
never seen. A list that needs extending whenever the prose changes register is
keeping pace rather than leading. No replacement is proposed, because the
alternatives tried elsewhere are worse: a general imperative parser would
over-collect far more, and a model-based detector is not deterministic and cannot
sit in a gate. Flagged as EV-18 so the next person does not assume it was never
noticed.
