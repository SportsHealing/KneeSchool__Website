# Artificial Intelligence in Imaging

Systems trained on what readers said, which are strongest where reading was
already reliable and silent about their own uncertainty.

## For Medical Students

### What It Shows

These systems detect findings, measure structures and draft reports from the
images. 5.20.1 covers structured reporting.

They are trained on labels that human readers produced, so they learn what
readers said rather than what was there. 5.21.6 covers the artificial
intelligence literature.

It matters because that training sets both their accuracy and their blind spots.
5.1.7 covers evidence-based imaging.

### How It Is Acquired

Establish what the system was trained on, including which departments and which
scanners. 5.5.1 covers the standard protocol.

Establish where the labels came from, whether from another reader or from an
operative finding. 5.21.6 covers the artificial intelligence literature.

Establish what it was validated on and whether that set was independent. 5.1.7
covers evidence-based imaging.

Establish what it does not attempt, which is rarely stated as clearly as what it
does. 5.20.8 covers common reporting errors.

Establish whether the output carries an uncertainty. 5.18.1 covers the
quantitative MRI.

### What Normal Looks Like

A stated training population with its scanners and protocols. 5.5.1 covers the
standard protocol.

A validation set independent of the training set. 5.1.7 covers evidence-based
imaging.

An output that marks what it could not assess. 5.20.1 covers structured
reporting.

Performance reported by subgroup rather than as one figure. 5.21.6 covers the
artificial intelligence literature.

### What Abnormal Looks Like

A system deployed on scanners unlike those it was trained on. 5.5.1 covers the
standard protocol.

Performance quoted as a single number for a whole joint. 5.21.6 covers the
artificial intelligence literature.

An output with uniform confidence across easy and hard cases. 5.1.6 covers
imaging pitfalls.

A measurement produced with no convention named. 5.16.4 covers the TT-TG
measurement.

A complete report with nothing marked as unassessable. 5.20.8 covers common
reporting errors.

### Key Learning Points

- These systems learn what readers said.
- The training population sets the blind spots.
- Validation has to be independent of training.
- Performance varies by subgroup.
- An output should mark what it could not assess.

## MRCS Level

### How It Is Acquired

In a viva the expected answer asks what the system was trained on.

The expected points are the training population, the label reference, the
independent validation, the stated scope, and the uncertainty.

Say that a label from a reader inherits that reader's variability. 5.20.8 covers
common reporting errors.

Say that a system is strongest where readers already agreed. 5.21.6 covers the
artificial intelligence literature.

Say that an operative reference beats a reader reference and is harder to
obtain. 5.1.7 covers evidence-based imaging.

### What Abnormal Looks Like

The reasoning expected is that a system trained on reader labels can at best
reproduce the readers, so it performs best on the complete ACL tear and worst on
the partial one, which is where readers disagreed. 5.20.3 covers reporting ACL
injuries.

The same argument applies to cartilage grading, to meniscal tear
classification, and to any finding whose definition varies. 5.20.5 covers
reporting cartilage lesions.

Fixing the measurement rules removes variability without settling which
convention is correct, so consistency improves and validity does not. 5.16.4
covers the TT-TG measurement.

The departments that supplied the training data supplied their reporting
conventions with it, local phrasing included. 5.20.1 covers structured
reporting.

### How Good It Is

These systems are the best available way to make reading consistent and are no
better than the readers who labelled their training data.

Their best contribution is consistency, triage, and the removal of the missing
negative and the hedge. 5.20.8 covers common reporting errors.

They are limited by label quality, by the training population, by uniform
confidence, and by being weakest exactly where reading was hardest. 5.21.6
covers the artificial intelligence literature.

No figures appear for accuracy on this page, under decision 028, and no
performance statistics appear either: those are published quantities from
particular datasets and this environment cannot check them. The restriction
bites hardest here, since performance figures are the main claim made for these
systems.

### Key Learning Points

- A system can at best reproduce its labellers.
- It is strongest where readers already agreed.
- Fixing the rules improves consistency and not validity.
- Training departments supply their conventions too.
- It is weakest where reading was hardest.

## FRCS Level

### How Good It Is

At decision level nothing in a report should be acted on differently because a
system produced it. 5.20.1 covers structured reporting.

The gain is in workflow: triage, measurement, comparison with priors, and
completeness. 5.1.5 covers the cost-effectiveness of imaging.

A measurement produced automatically still needs its convention stated before it
can be compared. 5.16.4 covers the TT-TG measurement.

A finding the system did not report is not a negative unless the system reports
negatives. 5.20.8 covers common reporting errors.

The surgeon remains the last check, and that does not change because the report
was drafted differently. 4.1.8 covers the examination documentation.

### Where It Misleads

The commonest error is reading machine confidence as accuracy. 5.1.6 covers
imaging pitfalls.

A complete report is read as a thorough study. 5.20.1 covers structured
reporting.

Performance from the development dataset is assumed to hold locally. 5.21.6
covers the artificial intelligence literature.

Agreement between a system and a reader is counted as validation when both
learned the same convention. 5.1.7 covers evidence-based imaging.

A system silent on a structure is read as having cleared it. 5.5.9 covers the
ligaments.

### Key Learning Points

- Machine confidence is read as accuracy.
- Completeness is read as thoroughness.
- Development performance is assumed to hold locally.
- Agreement with a reader may be shared convention.
- Silence is read as clearance.

## Fellowship Level

### Where It Misleads

At fellowship level these outputs arrive inside reports from other departments,
usually unmarked as automated. 5.20.7 covers reporting the post-operative knee.

Post-operative knees, paediatric knees and revision cases are
under-represented in training data and over-represented in a tertiary practice.
5.17.9 covers the revision arthroplasty.

A system updated between two studies of one patient makes the comparison a
comparison of systems. 5.18.1 covers the quantitative MRI.

Automated measurement of the patellofemoral geometry inherits the convention
problem and returns a number that looks settled. 5.16.4 covers the TT-TG
measurement.

Trial outcomes read by an automated system are consistent, which improves the
statistics without improving the truth. 5.1.7 covers evidence-based imaging.

The honest position is that these systems will change the workflow before they
change the accuracy, and the accuracy they change will be in the easy cases.
5.21.6 covers the artificial intelligence literature.

### Key Learning Points

- Automated output arrives unmarked inside reports.
- Tertiary cases are under-represented in training data.
- A system update makes a serial comparison meaningless.
- An automated measurement looks settled and is not.
- Workflow will change before accuracy does.

## Explore Further

- [[5.21.6 | Artificial Intelligence Literature]]
- [[5.20.1 | Structured Reporting]]
- [[5.20.8 | Common Reporting Errors]]
- [[5.16.4 | TT-TG Measurement]]
- [[3.16.6 | Artificial Intelligence]]
- [[5.1.7 | Evidence-Based Imaging]]

## References

No reference list is attached to this draft. Evidence verification has not
run, because source retrieval was unavailable at generation time. Under the
Operations Handbook a missing reference is acceptable and an invented one is a
critical failure, so nothing has been cited and no citation marker appears in
the text. This page carries no diagnostic accuracy figure, which is decision
028 rather than an omission: the comparative standing of the modalities is
standard teaching and a specific sensitivity written from memory is the same
class of claim as an invented citation, so ACC-001 refuses the number and the
page states the comparison. A reviewer with the literature can add the figures
into How Good It Is without restructuring the page. Any measurement here,
including a sequence parameter, an angle or a millimetre, is written from
standard teaching, has not been checked, and is registered under decision 006
in pipeline/config/figures with a verification state of UNVERIFIED_FROM_MEMORY.
