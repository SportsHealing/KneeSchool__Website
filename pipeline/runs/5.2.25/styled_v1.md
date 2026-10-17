# 3D Reconstruction

Turning a volume into a surface, which is what surgical planning and printing
are built on.

## For Medical Students

### What It Shows

A three dimensional reconstruction displays the volume as a surface by deciding
which voxels are bone and which are not. 5.2.23 covers the reconstruction.

That decision is a threshold, so the surface is an interpretation of the data
rather than a direct image of it. 5.2.22 covers the computed tomography
acquisition.

It matters because the surface looks definitive and depends on a setting, which
is the same lesson the radiographic pages taught about display. 5.2.2 covers the
image formation.

### How It Is Acquired

An isotropic volume is needed, otherwise the surface is smoother in one direction
than another. 5.2.22 covers the computed tomography acquisition.

A threshold separates bone from soft tissue, and moving it thickens or thins
every cortex in the model. 5.16.8 covers three dimensional reconstructions.

Segmentation separates the bones from each other, which is manual, automated or
both. 5.16.7 covers robotic surgery planning.

The resulting surface can be measured, printed or used to plan an implant
position. 5.16.6 covers arthroplasty planning.

Metal in the volume corrupts the surface locally, so an implant bearing knee
needs the artefact reduced version. 5.2.23 covers the reconstruction.

### Key Learning Points

- A surface is produced by deciding which voxels are bone.
- That decision is a threshold, so the surface is an interpretation.
- An isotropic volume is needed for an even surface.
- Moving the threshold thickens or thins every cortex.
- Metal corrupts the surface locally.

## MRCS Level

### How It Is Acquired

In a viva this is the page behind the answer that a printed model is only as good
as its segmentation.

The expected points are the isotropic volume, the threshold, the segmentation,
the uses, and metal.

Say that the threshold changes the apparent cortical thickness. 5.16.8 covers
three dimensional reconstructions.

Say that the surface looks more certain than the data beneath it. 5.2.2 covers
the image formation.

Say that a planning model carries the acquisition's limitations forward. 5.16.6
covers arthroplasty planning.

### How Good It Is

A three dimensional reconstruction communicates geometry better than any other
display and adds no information to the volume it came from.

Its best contribution is communication and planning, where a surgeon's
understanding of a complex fracture or deformity improves markedly. 5.16.2
covers tibial plateau fractures.

It is limited by being a rendering, so a fine detail or a thin cortex may be
present in the data and absent from the surface. 5.2.23 covers the
reconstruction.

No figures appear for accuracy on this page, under decision 028, and no threshold
values appear either, in Hounsfield units: those are protocol and vendor
specific and this environment cannot check published figures.

### Key Learning Points

- It communicates geometry better than any other display.
- It adds no information to the volume it came from.
- Planning and communication are its real contributions.
- A thin cortex can be in the data and absent from the surface.
- The threshold is not stated here because it cannot be checked.

## FRCS Level

### How Good It Is

At decision level a reconstruction is a planning aid and should not be the only
thing looked at.

A complex articular fracture is understood faster from a surface than from
slices, which changes the approach chosen. 5.16.2 covers tibial plateau
fractures.

Deformity correction planning uses the surface for the plan and the slices for
the detail, and both are needed. 5.16.5 covers osteotomy planning.

Robotic and patient specific planning depend on segmentation accuracy, so the
plan inherits every segmentation error silently. 5.16.7 covers robotic surgery
planning.

A revision with widened tunnels needs the slices, because the surface will render
a wall the data does not support. 5.7.12 covers tunnel assessment.

### Where It Misleads

The commonest error is planning from the surface without reviewing the slices.
5.16.8 covers three dimensional reconstructions.

A threshold set high thins the cortex and overstates bone loss. 5.2.23 covers
the reconstruction.

A threshold set low fills a defect and understates it. 5.16.2 covers tibial
plateau fractures.

Metal corruption is read as the shape of the bone. 5.7.14 covers revision
cruciate imaging.

An automated segmentation is accepted without checking it against the slices.
5.18.8 covers artificial intelligence in imaging.

### Key Learning Points

- Planning from the surface without the slices is the commonest error.
- A high threshold thins the cortex and overstates bone loss.
- A low threshold fills a defect and understates it.
- Metal corruption is read as the shape of the bone.
- An automated segmentation is accepted unchecked.

## Fellowship Level

### Where It Misleads

At fellowship level the three dimensional surface is where this chapter's
argument has the largest practical consequence, because a plan is built on it
and executed.

Patient specific instrumentation and robotic planning both convert a segmentation
into a cut, so a segmentation error becomes a bone cut rather than a misread
image. 5.16.7 covers robotic surgery planning.

Segmentation is increasingly automated, and its errors are systematic by
anatomy and by population rather than random, which makes them hard to catch by
inspection. 5.18.8 covers artificial intelligence in imaging.

The threshold and the reconstruction method travel with the model and are not
recorded in the plan, so a measurement taken from a model has an unstated
provenance. 5.2.23 covers the reconstruction.

The surface carries no uncertainty, which is its advantage for communication and
its hazard for measurement, and nothing in the workflow restores the uncertainty.
5.20.1 covers structured reporting.

So the chapter ends where it started, with the point that every imaging
appearance is made jointly by the tissue and the instrument, and that a plan
built on one should name both. 5.2.1 covers the generation of X-rays.

### Key Learning Points

- A segmentation error becomes a bone cut rather than a misread image.
- Automated segmentation errors are systematic by anatomy and population.
- The threshold and method are not recorded in the plan.
- The surface carries no uncertainty and nothing restores it.
- An appearance is made jointly by the tissue and the instrument.

## Explore Further

- [[5.2.22 | CT Acquisition]]
- [[5.2.23 | Reconstruction]]
- [[5.16.8 | 3D Reconstructions]]
- [[5.16.7 | Robotic Surgery Planning]]
- [[5.16.5 | Osteotomy Planning]]
- [[5.16.2 | Tibial Plateau Fractures]]

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
