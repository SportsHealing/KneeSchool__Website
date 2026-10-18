# Robotic Surgery Planning

A plan built from a segmented scan, which becomes the model the system cuts to,
so a segmentation error becomes a bone cut.

## For Medical Students

### What It Shows

Robotic planning turns a computed tomography study into a three dimensional
model of the patient's bones, and the plan is made on that model. 5.2.25 covers
the 3D reconstruction.

The model is produced by segmentation, which decides where the system believes
the bone surface is. 5.2.23 covers the reconstruction.

It matters because the model becomes the reference the system works to, so an
error in the model becomes an error in the operation. 5.16.8 covers the 3D
reconstructions.

### How It Is Acquired

Acquire the study to the system's protocol, because the segmentation was
validated on it. 5.2.22 covers the CT acquisition.

Check the segmentation against the source slices rather than accepting the
model. 5.2.23 covers the reconstruction.

Check the landmarks the plan depends on, since those are where a segmentation
error matters. 2.1.8 covers the imaging anatomy.

Check the alignment against the standing radiograph, which a supine scan cannot
give. 5.3.6 covers the long leg alignment films.

Record the dose, since this is a planning study added to the usual radiographs.
5.2.24 covers the radiation dose.

### What Normal Looks Like

A segmentation whose surface follows the cortex on the source slices. 5.2.23
covers the reconstruction.

Landmarks identifiable both on the model and on the slices. 2.1.8 covers the
imaging anatomy.

An implant plan consistent with the standing alignment. 5.3.7 covers the
mechanical axis.

Osteophytes represented as osteophytes rather than as bone surface. 5.3.18
covers osteophytes.

### What Abnormal Looks Like

A segmentation that includes an osteophyte as native surface. 5.3.18 covers
osteophytes.

A surface that smooths over a defect the slices show. 5.3.19 covers subchondral
sclerosis.

Artefact from a previous implant carried into the model as anatomy. 5.2.19
covers the artefacts.

A plan whose alignment target disagrees with the standing film. 5.3.6 covers the
long leg alignment films.

A model accepted with no reference to the slices it came from. 5.16.8 covers the
3D reconstructions.

### Key Learning Points

- The plan is made on a model rather than on the images.
- Segmentation decides where the system believes the surface is.
- An error in the model becomes an error in the operation.
- Osteophytes are the commonest segmentation problem.
- A supine scan cannot give the standing alignment.

## MRCS Level

### How It Is Acquired

In a viva the expected answer treats the model as an interpretation.

The expected points are the system protocol, the segmentation check, the
landmarks, the standing alignment, and the dose.

Say that the model is derived data rather than the study. 5.2.23 covers the
reconstruction.

Say that the plan is made supine for an operation judged in stance. 5.18.5
covers weight-bearing MRI.

Say that the soft tissue balance remains intraoperative. 5.5.9 covers the
ligaments.

### What Abnormal Looks Like

The reasoning expected is that segmentation uses a density threshold, so a
structure near that density is included or excluded by the threshold rather than
by anatomy. 5.2.23 covers the reconstruction.

An osteophyte has the density of bone and is anatomically not the surface an
implant should sit on, which a threshold cannot distinguish. 5.3.18 covers
osteophytes.

Sclerotic bone and a cystic defect sit on either side of the threshold, so the
surface near them is where the model is least reliable. 5.3.19 covers
subchondral sclerosis.

Metal artefact raises and lowers density around an implant, which the threshold
reads as bone and as the absence of bone. 5.2.19 covers the artefacts.

### How Good It Is

A plan built from computed tomography is the most precise geometric plan
available and is precise about a model rather than about the patient.

Its best contribution is reproducible implant positioning relative to the
planned references. 5.16.6 covers arthroplasty planning.

It is limited by segmentation accuracy, by supine acquisition, by the absence of
soft tissue information, and by the dose it adds. 5.2.24 covers the radiation
dose.

No figures appear for accuracy on this page, under decision 028, and no
segmentation tolerances, cut accuracies or dose values appear either: those are
published quantities tied to particular systems and this environment cannot
check them.

### Key Learning Points

- Segmentation works from a density threshold.
- An osteophyte has bone density and is not the implant surface.
- Sclerosis and cysts sit either side of the threshold.
- Metal artefact reads as bone and as its absence.
- Precision about a model is not precision about the patient.

## FRCS Level

### How Good It Is

At decision level the plan is a document that will be executed, so reviewing it
is part of the operation rather than preparation for it. 5.20.1 covers
structured reporting.

The landmarks and the alignment target are the two things worth checking against
the source. 5.3.7 covers the mechanical axis.

Bone loss and previous implants are where the model is least trustworthy. 5.17.9
covers the revision arthroplasty.

The standing radiograph remains the alignment reference, because the plan is
supine. 5.3.6 covers the long leg alignment films.

Intraoperative registration can correct a model error only if the error is
noticed. 5.16.6 covers arthroplasty planning.

### Where It Misleads

The commonest error is reviewing the model and not the slices. 5.16.8 covers the
3D reconstructions.

A smooth rendering carries an authority the underlying data does not support.
5.2.25 covers the 3D reconstruction.

A plan's numerical precision is read as accuracy against the patient. 5.1.6
covers imaging pitfalls.

Osteophytes included in the model shift the planned resection. 5.3.18 covers
osteophytes.

The absence of soft tissue from the plan is read as the soft tissue having been
accounted for. 5.5.9 covers the ligaments.

### Key Learning Points

- The slices rather than the model are what to review.
- A smooth rendering carries unearned authority.
- Numerical precision is read as accuracy.
- Included osteophytes shift the planned resection.
- The plan contains no soft tissue information.

## Fellowship Level

### Where It Misleads

At fellowship level the plan arrives already made, and the surgeon reviewing it
did not acquire the scan or check the segmentation. 5.20.7 covers reporting the
post-operative knee.

Each system segments and references differently, so a plan is not portable
between systems. 5.16.6 covers arthroplasty planning.

A revision case is where the model is least reliable and where the plan is most
relied on. 5.17.9 covers the revision arthroplasty.

The planning dose is additional and recurs across a pathway, which weighs more
in younger patients. 5.2.24 covers the radiation dose.

Automated segmentation is improving, and its failures are now the quiet ones
rather than the obvious ones. 5.18.8 covers artificial intelligence in imaging.

The honest position is that the precision of these plans is real and is
precision about geometry, while the operation is judged on balance and function
that none of this measures. 5.5.9 covers the ligaments.

### Key Learning Points

- The reviewer did not acquire the scan or check the segmentation.
- A plan is not portable between systems.
- The model is least reliable where it is most relied on.
- The planning dose recurs across the pathway.
- The precision is geometric and the judgement is functional.

## Explore Further

- [[5.16.8 | 3D Reconstructions]]
- [[5.16.6 | Arthroplasty Planning]]
- [[5.2.25 | 3D Reconstruction]]
- [[5.2.23 | Reconstruction]]
- [[5.17.9 | Revision Arthroplasty]]
- [[5.2.24 | Radiation Dose]]

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
