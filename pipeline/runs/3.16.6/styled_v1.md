# Artificial Intelligence

Methods that find patterns in data without being told what to look for.
Powerful where the data is plentiful, and silent about why.

## FRCS Level

### The Principle

Conventional modelling starts from physics and derives a prediction. Machine
learning starts from examples and derives a rule.

That is useful exactly where the physics is intractable and the examples are
plentiful.

It also means the method inherits whatever is in the examples, including
anything systematically missing from them.

### At the Knee

The established applications are in imaging: segmentation of cartilage and
meniscus, and detection of structural findings. 5.18.8 covers imaging
applications.

In movement analysis, learned models estimate joint angles and loads from
fewer sensors than physics based methods require. 3.16.8 covers wearables.

That is the most likely route to measuring the knee outside a laboratory,
which is this chapter's recurring unmet need. 3.13.7 covers the gap.

Learned models can also replace slow computations, predicting a finite element
result in milliseconds after training on many solved models. 3.16.4 covers the
method.

What these methods do not provide is a mechanism. A prediction without an
explanation is useful clinically and weak scientifically.

### What Changes It

The training data, which determines what the model can represent and what it
cannot.

Whether the validation set was genuinely separate, which is the commonest
methodological failure.

The population the data came from, since a model trained on one group performs
worse on another.

How performance is reported, since accuracy on an imbalanced dataset is
misleading.

Whether the output is interpretable, which affects whether an error can be
recognised.

### Clinical Relevance

Ask what a model was trained on before asking how well it performed.

Expect performance to fall on a population unlike the training set.

Treat a prediction without a mechanism as a useful signal rather than an
explanation.

Note that reported accuracy depends on the test set's composition.

### Key Learning Points

- Physics based modelling derives a prediction; learning derives a rule from examples.
- The method inherits whatever is in the examples, including what is missing.
- Established knee applications are in imaging segmentation and detection.
- Learned models may be the route to measuring the knee outside a laboratory.
- A prediction without an explanation is clinically useful and scientifically weak.

## Fellowship Level

### At the Knee

The dataset is the model. Two groups using identical architectures on
different datasets produce different tools, and the dataset is the part least
often published.

Knee datasets are drawn disproportionately from populations that reach imaging
and surgery, which is a selected group. 3.15.7 covers the same bias in
athletics.

External validation on an independent cohort is the test that matters, and
internal cross validation is routinely reported in its place.

Performance degradation on new scanners, new protocols and new populations is
well described and is the main barrier to deployment.

Explainability methods exist and generally describe what the model attended to
rather than why, which is a weaker claim than it sounds.

### What Changes It

Dataset size, provenance and whether it is available for inspection.

Whether external validation was performed on a separate institution's data.

Class balance, which drives apparent accuracy.

Label quality, since a model trained on radiologist labels learns
radiologists.

Distribution shift between development and deployment.

### How It Is Measured

Area under the receiver operating characteristic curve, which is standard and
insensitive to class balance in a way that can flatter.

Sensitivity and specificity at a stated operating point, which is more
clinically meaningful and less often reported.

External validation on independent cohorts, which is the meaningful test.

Comparison against clinician performance, which is the comparison that matters
and is frequently against a weaker baseline than practice.

Prospective evaluation, which is rare and is what regulators increasingly ask
for.

### Clinical Relevance

Ask for external validation rather than cross validation.

Check what the comparison clinician baseline was, since it is often weaker
than real practice.

Expect degradation with a change of scanner, protocol or population.

Treat a label trained model as having learned the labellers, which bounds what
it can exceed.

### Key Learning Points

- The dataset is the model, and it is the part least often published.
- Knee datasets come from populations selected by reaching imaging and surgery.
- External validation is the test that matters; cross validation is reported in its place.
- A model trained on radiologist labels learns radiologists.
- Explainability usually describes what was attended to rather than why.

## Consultant Perspective

### At the Knee

The decision is not whether these methods work. It is what a clinician is
accountable for when a tool they cannot inspect contributes to a decision.

On one side, these methods are already better than available alternatives at
several narrow tasks, and refusing them has a cost measured in missed findings
and in time. 5.18.8 covers imaging.

On the other, a tool whose failure mode is unfamiliar fails differently from a
human, and a clinician who cannot predict the failure cannot supervise it.

The weight moves with the task. A segmentation that is checked before use is
low stakes. A triage decision that determines whether a clinician looks at all
is not.

What is not a defensible position is either extreme: refusing the tools
wholesale, or accepting an output because the reported performance was high.

### What Changes It

Whether the output is checked by a clinician before it acts, which is the main
determinant of risk.

Whether the deployment population matches the development population.

Regulatory status and post market surveillance arrangements.

Whether the failure modes have been characterised, rather than only the
accuracy.

Local monitoring capacity, since a model that degrades silently needs someone
watching.

### How It Is Measured

Prospective clinical evaluation, which is uncommon and is what the decision
needs.

Post deployment monitoring, which detects distribution shift and is rarer
still.

Published external validation, which is a precondition rather than sufficient.

Error analysis describing how the model fails, which is more useful than a
headline accuracy and is seldom published.

There is no established standard for how a clinical service should monitor a
deployed model, which is a governance gap rather than a technical one.

### Clinical Relevance

Decide by task and by whether the output is checked before it acts, rather
than by the technology.

Require external validation in a population resembling yours before
deployment.

Ask how the model fails rather than how often, since supervision depends on
the first.

State that no standard exists for monitoring a deployed model in a clinical
service.

Weigh the patient's age and physiology, comorbidities, knee demand,
psychological state and their own ideas, concerns and expectations, and tell
them when a tool contributed to a decision about them, because that is their
information rather than the service's.

### Key Learning Points

- The decision is what a clinician is accountable for when a tool they cannot inspect contributes.
- A tool whose failure mode is unfamiliar cannot be supervised by someone who cannot predict it.
- A checked segmentation is low stakes; a triage decision that stops a clinician looking is not.
- Neither wholesale refusal nor acceptance on reported performance is defensible.
- No standard exists for how a clinical service should monitor a deployed model.

## Explore Further

- [[3.16.5 | Computational Biomechanics]]
- [[3.16.8 | Wearable Technology]]
- [[3.16.9 | Digital Twins]]
- [[3.16.10 | Future Directions]]
- [[3.16.4 | Finite Element Modelling]]

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
