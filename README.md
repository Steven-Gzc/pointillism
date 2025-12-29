# Pointillism 3D Printing Toolkit

Generate Seurat-style pointillist 3D printing models from any image and a limited filament palette. The pipeline reduces an image to a small palette, dithers it, places dots on a hex grid, and emits SVG + STLs for slicing in Bambu Studio.

## Requirements
- Python 3.9+
- Pillow (`pip install pillow`)
- A multicolor FDM 3D printing machine (e.g. Bambu Lab A1 with AMS and 0.4mm nozzle)
- A slicer (e.g. Bambu Studio)

## Quick start (defaults)
```
python pointillism_pipeline.py
```
Defaults:
- Image: `sailboat.jpg`
- Palette: `bambu-pla-matte-hex-codes.md`
- Out dir: `out/`
- Width: 180 mm; Spacing: 0.8 mm (center-to-center, hex grid)
- Dot: 0.8 mm dia, 0.4 mm tall; Base: 0.6 mm; Segments: 12 facets
- Palette colors: Sky Blue, Scarlet Red, Lemon Yellow, Charcoal

Outputs in `out/`: `dithered.png`, `mask_*.png`, `dots.svg`, `base.stl`, per-color dot STLs, `metadata.json`.

## Custom run
```
python pointillism_pipeline.py my_image.png bambu-pla-matte-hex-codes.md out \
  --width-mm 120 --spacing-mm 0.4 --dot-mm 0.3 --dot-height-mm 0.2 --base-thickness-mm 0.2 \
  --segments 12 --colors "Sky Blue,Scarlet Red,Lemon Yellow,Charcoal"
```

## What the script does
1) Loads palette (Markdown table or JSON with name/hex). Optional color subset via `--colors`.
2) Rescales the image so one pixel corresponds to `spacing-mm` (horizontal) on a hex-staggered grid (vertical pitch = spacing * √3/2).
3) Floyd–Steinberg dithers the image to the chosen palette; each pixel becomes a dot center.
4) Generates:
   - `dithered.png` and per-color `mask_*.png`
   - `dots.svg` (mm units) with a dark background (Charcoal if available)
   - `base.stl` and per-color dot STLs (cylinders), hex-staggered, trimmed to stay within the base
   - `metadata.json` capturing all parameters, coverage percent, palette, and file names

## Slicing guidance (Bambu Studio, A1 + AMS, 0.4 mm nozzle)
- Import `base.stl` and per-color STLs; assign each color to its AMS tool.
- 0.08 mm layers; 0.4 mm line width; PLA 195–205 C; fan 100%.
- Enable flush tower; use measured flush volumes for your filaments.
- Keep travels short; slow small perimeters; Z-hop off; combing within infill.

## Coverage and gaps
- Hex grid increases packing vs. square, but spacing/dot size dominate coverage.
- Increase coverage by lowering `spacing-mm`, increasing `dot-mm`, or adding a light channel (white/ivory) to brighten gaps.
- Metadata reports coverage_fraction and coverage_percent to quantify fill.

## Full-plate runs
- A1 bed ~256×256 mm. Use `--width-mm 230`–`240` to leave edge clearance; expect longer slicing, longer prints and more swaps. Adjust spacing and dot size to control dot count.

## Calibration
- Flush: run color-change towers per filament pair to set AMS flush lengths.
- Coverage: print a 50×50 mm tile with multiple spacing bands to pick the best bleed/sharpness trade-off.
- Sheen: test matte vs. glossy to see how highlights affect blending.

## Known limitations / next steps
- Potential improvements:
  - Use 0.2mm nozzle for finer detail.
  - Use CMYK filaments over a white base tile to maximize gamut and brighten gaps.
  - Apply gamma correction (e.g., linearize to gamma 2.2, dither, then map) to compensate for dot gaps darkening the image.
  - Encode transparency/coverage as variable dot height or base thickness for relief-style translucency (dynamic thickness).
- limitations
  - Palette mapping is simple RGB nearest-color; no gamma or perceptual color space.
  - Overlap/bleed control is manual (adjust spacing and dot size); no adaptive spacing yet.
  - STL generation is ASCII for simplicity; binary STL would be smaller.
  - Defaults are coarse (0.8 mm spacing/dots); adjust down for finer A1 output (e.g., 0.3–0.4 mm spacing, 0.3–0.35 mm dots).

## Files
- `pointillism_pipeline.py` — CLI generator for dithering, SVG, and STLs.
- `bambu-pla-matte-hex-codes.md` — sample palette (name + hex).
- `workflow.md` — condensed workflow and usage notes.
