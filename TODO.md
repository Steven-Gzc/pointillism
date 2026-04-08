# Pointillism Project Todo

This file turns the current plan into a practical implementation backlog.
We will implement these items one by one later.

## Current Direction

- Keep the workflow optimized for a `0.4 mm` nozzle while experiments are still in progress.
- Reduce slicer friction before adding more image-processing sophistication.
- Avoid hard-coding "good" print parameters until they are validated by repeatable test prints.

## Priority Order

1. Replace circular dot geometry with triangle-based geometry that slicers handle more predictably.
2. Simplify parameter tuning and remove misleading default print settings from docs.
3. Research and prototype better color science using gamma-aware processing and OKLab.
4. Modularize the codebase and align the documentation with the actual workflow.

## Todo List

### 1. Triangle Geometry For Dots

- Replace the current circle/cylinder dot representation with triangle-based geometry.
  - 2D triangular pixels on a triangular grid.
- Preserve exact physical positioning when changing geometry generation.
- Re-check coordinate math for:
  - hex/triangular packing offsets,
  - even/odd row staggering,
  - bounds trimming at the print edges,
  - exported SVG and STL alignment.
- Confirm the generated mesh imports cleanly into the slicer and does not create tiny invalid features.
- Add at least one visual/debug export to verify coordinates before slicing.

Definition of done:
- Geometry is easier for the slicer to process than the current circular approach.
- Dot placement still matches the dithered image without drift or row misalignment.
- Exported parts stay within the base tile and remain color-aligned.

### 2. Parameter Tuning Workflow

- Remove "recommended" dot-size and spacing defaults in the docs.
- Replace fixed values in the docs with placeholders, ranges, or "to be calibrated" language.
- Keep code defaults only if they are clearly labeled as temporary examples, not validated recommendations.
- Update the project to reflect the current `0.4 mm` nozzle workflow instead of mixing `0.2 mm` and `0.4 mm` guidance.
- Create a simpler tuning process for spacing, dot size, and related print parameters.
- Add a dedicated calibration mode or repeatable test workflow that generates:
  - spacing sweeps,
  - dot-size sweeps,
  - combined comparison tiles.
- Make tuning outputs easy to compare and record from one test print to the next.

Definition of done:
- The docs do not imply confidence in values that are still experimental.
- It is faster to run structured parameter tests than to tweak values manually.
- The workflow for finding usable spacing and dot size is repeatable.

### 3. Color Science Research

- Research OKLab as a better palette-matching space than raw RGB distance.
- Research gamma-aware preprocessing so palette reduction is based on perceptual brightness instead of display-space RGB alone.
- Decide where color science should enter the pipeline:
  - before palette reduction,
  - during nearest-color matching,
  - during dithering error propagation,
  - or all three.
- Compare current RGB nearest-color mapping with an OKLab-based prototype on a few sample images.
- Document tradeoffs:
  - visual improvement,
  - processing cost,
  - implementation complexity,
  - whether the benefit is noticeable in physical prints.

Definition of done:
- There is a clear decision about whether to adopt OKLab, gamma correction, both, or neither.
- The decision is based on side-by-side output comparisons, not just theory.

### 4. Modularization And Docs

- Split the single script into logical modules, likely around:
  - palette loading,
  - image resizing and dithering,
  - coordinate generation,
  - mesh/SVG export,
  - CLI entrypoint.
- Keep behavior unchanged while refactoring unless a task explicitly requires behavior changes.
- Update docs so they match the code exactly.
- Consolidate duplicated workflow notes across `README.md`, `workflow.md`, and `feasibility.md`.
- Make it clear which docs are:
  - stable usage instructions,
  - experimental notes,
  - future research directions.

Definition of done:
- The code is easier to modify without touching unrelated parts.
- The docs are consistent with each other and with the current nozzle/workflow assumptions.

## Notes For Later Implementation

- Start with geometry first because slicer compatibility affects everything downstream.
- Do not treat current spacing and dot-size values as permanent baselines.
- When we reach the color-science step, keep the comparison measurable and visual.
- Refactoring should come after the geometry and tuning workflow are clearer, so we do not reorganize code around assumptions that may change.
