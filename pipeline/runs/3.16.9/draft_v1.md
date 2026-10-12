# Digital Twins

A patient specific model updated by that patient's own data. A coherent idea,
a fashionable phrase, and very little at the knee that meets the definition.

## FRCS Level

### The Principle

A model becomes a twin when it is tied to one individual and updated as that
individual changes.

A model built from a patient's scan is patient specific. It becomes a twin
only when new data about that patient keeps changing it.

The difference is the update loop, and it is the part most often missing from
things called digital twins.

### At the Knee

The components exist separately. Patient specific geometry from imaging, a
finite element or musculoskeletal model, and continuous data from wearables.
3.16.4 and 3.16.8 cover two of them.

What is missing is the loop that feeds the data back into the model and
revises it.

A knee twin would predict how this patient's cartilage responds to this
patient's activity, and update the prediction as the activity changes.

Nothing at the knee currently does that outside research demonstrations.

Industrial digital twins work because the physical system is manufactured to a
specification. A knee is not, which is why biological twins are harder than
the phrase suggests.

### What Changes It

Availability of continuous individual data, which wearables are beginning to
supply.

Computational speed, since a model that takes hours cannot update usefully.
3.16.6 covers the shortcut.

Material property estimation in a living person, which remains the hardest
gap. 3.16.4 covers it.

Validation methods for an individualised prediction, which differ from
population ones.

Clear definition, since the term is used for anything patient specific.

### Clinical Relevance

Ask whether a claimed digital twin has an update loop, which is the
definition.

Treat patient specific modelling as valuable and as a different thing from a
twin.

Expect material properties to be the limiting gap rather than geometry or
computation.

Note that nothing at the knee currently meets the definition outside research.

### Key Learning Points

- A model becomes a twin when it is tied to one person and updated as they change.
- The update loop is the definition and the part usually missing.
- Geometry, models and continuous data all exist separately.
- Industrial twins work because the system is built to a specification; a knee is not.
- Nothing at the knee meets the definition outside research demonstrations.

## Fellowship Level

### At the Knee

The plausible near term version is narrower than the phrase: a patient
specific model of one tissue, updated by one stream of data, answering one
question.

Cartilage response to cumulative loading is the obvious candidate, because the
exposure is now measurable and the outcome is slow enough to track. 3.16.8
covers the exposure.

The hard part is not the model. It is estimating this person's material
properties without a biopsy, and current practice assumes population values.
3.16.4 covers that assumption.

Quantitative magnetic resonance imaging offers a route to individual cartilage
composition and lacks clinical thresholds. 5.11 covers cartilage imaging.

Without individual material properties, a twin is a population model wearing
one patient's shape, which is a weaker claim than the term implies.

### What Changes It

Whether individual material properties can be estimated non invasively.

Quality and continuity of the data stream feeding the update.

Model reduction and learned surrogates, which make the update computationally
feasible.

The specific question, since a narrow twin is tractable and a general one is
not.

Validation design, since predicting one person's future cannot be validated by
a cohort.

### How It Is Measured

Validation of an individualised prediction requires prospective follow up of
that individual, which is a different study design from anything else in this
chapter.

Group level validation tells you the method works on average, which is the
thing a twin is supposed to improve on.

Research demonstrations report geometric and kinematic agreement rather than
predictive accuracy.

Imaging based material property estimation, which is active research without
clinical thresholds.

No knee digital twin has been prospectively validated to predict an
individual's outcome, which is the claim the concept rests on.

### Clinical Relevance

Judge a twin by its prediction of a future event in that individual rather
than by its resemblance to them.

Expect material properties to be assumed from a population, and ask whether
they were.

Treat narrow single tissue twins as the plausible version and general ones as
marketing.

Note that group validation does not establish an individual prediction.

### Key Learning Points

- The plausible version is narrow: one tissue, one data stream, one question.
- The hard part is estimating this person's material properties without a biopsy.
- Without them, a twin is a population model wearing one patient's shape.
- Validating an individual prediction needs prospective follow up of that individual.
- No knee twin has been prospectively validated to predict an individual's outcome.

## Consultant Perspective

### At the Knee

The decision this page poses is about language before it is about technology:
whether to let a term be used in a department when the thing it names does not
yet exist there.

On one side, the concept is coherent, the components are real, and premature
dismissal has a cost in missed early adoption. 3.16.8 covers the component
that arrived.

On the other, the term is already being applied to ordinary patient specific
models, and a borrowed word that implies prediction where there is only
resemblance misleads colleagues and patients.

What moves the weight is whether an update loop and a prospective validation
exist. Those two questions deflate most current claims and will eventually
stop deflating them.

Both positions are defensible: insisting on the strict definition, or using
the term loosely and qualifying it. What is not defensible is presenting a
patient specific model to a patient as a prediction about them.

### What Changes It

Whether an update loop exists, which is the definitional question.

Whether individual rather than population material properties were used.

Whether any prospective individual validation has been published.

Who is making the claim, since this term currently travels faster in industry
than in literature.

The use to which the output is being put, since a planning aid and a prognosis
are different.

### How It Is Measured

Prospective individual prediction studies, which is the measurement that would
settle it and which do not yet exist at the knee.

Component validation, which is what is currently published and is necessary
rather than sufficient.

Agreement between the twin and the patient on a measurable present quantity,
which is resemblance rather than prediction.

Regulatory evaluation, which is beginning to distinguish decision support from
visualisation.

There is no agreed standard for what a clinical digital twin must demonstrate,
which is why the term is doing work the evidence is not.

### Clinical Relevance

Ask for the update loop and for prospective individual validation before
accepting the term.

Describe a patient specific model to a patient as a model of their anatomy
rather than as a prediction about them.

Hold a stated position on the terminology rather than letting it drift.

State that no agreed standard exists for what a clinical digital twin must
demonstrate.

Weigh the patient's age and physiology, comorbidities, knee demand,
psychological state and their own ideas, concerns and expectations before
showing them a model of their own knee, because a picture of your own joint
failing is a powerful thing to be given.

### Key Learning Points

- The decision is about language before it is about technology.
- The components are real and the update loop is usually missing.
- A borrowed word implying prediction where there is resemblance misleads colleagues and patients.
- Two defensible positions: insist on the strict definition, or use it loosely and qualify it.
- No agreed standard exists for what a clinical digital twin must demonstrate.

## Explore Further

- [[3.16.4 | Finite Element Modelling]]
- [[3.16.8 | Wearable Technology]]
- [[3.16.6 | Artificial Intelligence]]
- [[3.16.10 | Future Directions]]
- [[3.16.5 | Computational Biomechanics]]

## References

No reference list is attached to this draft. Evidence verification has not
run, because source retrieval was unavailable at generation time. Under the
Operations Handbook a missing reference is acceptable and an invented one is a
critical failure, so nothing has been cited and no citation marker appears in
the text. Every measurement on this page is written from standard teaching
rather than from a retrieved paper, and none has been checked against a
source. Under decision 006 each one is registered in pipeline/config/figures
with the sentence it supports and a verification state of
UNVERIFIED_FROM_MEMORY, so the whole list can be checked and corrected rather
than hunted for.
