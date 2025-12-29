# Pointillist 3MF Workflow (Bambu Lab A1 + AMS, 0.2 mm)

Goal: start from an image and a small AMS palette, produce halftoned dot geometry (hex-staggered), STLs, and a sliced 3MF for the A1 with a 0.2 mm nozzle.

## Inputs
- Image: PNG/JPEG, cropped to final aspect.
- Palette: 3–4 colors (see `bambu-pla-matte-hex-codes.md`), or JSON with name/hex entries.
- Hardware: Bambu Lab A1 + AMS, 0.2 mm nozzle.

## Outputs
- `dithered.png` (palette-reduced with error diffusion).
- `mask_*.png` per color.
- `dots.svg` (mm units, hex grid).
- `base.stl` + per-color dot STLs.
- `metadata.json` with parameters, palette, grid, coverage, and filenames.

## Script defaults (from pointillism_pipeline.py)
- Image: `sailboat.jpg`; Palette: `bambu-pla-matte-hex-codes.md`; Out dir: `out/`.
- Width: 180 mm; Spacing: 0.8 mm (center-to-center, hex grid).
- Dot diameter: 0.8 mm; Dot height: 0.4 mm; Base thickness: 0.6 mm.
- Segments: 12 (coarser = fewer triangles).
- Palette: Sky Blue, Scarlet Red, Lemon Yellow, Charcoal.

Run with defaults:
```
python pointillism_pipeline.py
```

Run with custom size and palette:
```
python pointillism_pipeline.py my_image.png bambu-pla-matte-hex-codes.md out \
  --width-mm 120 --spacing-mm 0.4 --dot-mm 0.3 --dot-height-mm 0.2 --base-thickness-mm 0.2 \
  --colors "Sky Blue,Scarlet Red,Lemon Yellow,Charcoal"
```

## Workflow (pipeline)
1) Palette: pick 3–4 matte PLA colors; map to AMS slots.
2) Image prep: resize so pixel pitch equals `spacing-mm`; apply ordered or error-diffusion dithering to the limited palette.
3) Geometry: convert “on” pixels to circles (hex-staggered grid), project onto a thin base, emit SVG and STLs (base + per color).
4) Slice: import base + color STLs into Bambu Studio; assign each color part to its AMS tool; 0.2 mm nozzle, ~0.1 mm layers, 0.24–0.26 mm line width, PLA 195–205 C, fan 100%, flush tower on with tuned flush volumes.
5) Export: save 3MF with AMS assignments and purge settings.

## Calibration loop
- Flush volumes: run a color-change tower per filament pair; set AMS flush lengths.
- Coverage test: print a 50×50 mm tile with bands of different spacings (e.g., 0.35/0.40/0.45/0.50) and inspect bleed/registration.
- Sheen: test matte vs. glossy on the same pattern.

## Using the full A1 plate (~256×256 mm)
- Set `--width-mm` near 230–240 mm to leave edge clearance. Increase spacing or reduce dot count if needed; expect longer print times and more swaps.

## Parameter definitions
- width-mm: target physical width; image is resampled so (pixels * spacing) ≈ width.
- spacing-mm: center-to-center grid pitch (hex-staggered).
- dot-mm: dot diameter (SVG/STL).
- dot-height-mm: dot height above base.
- base-thickness-mm: base tile thickness before dots.
- segments: facets to approximate each dot cylinder.
- colors: comma-separated palette names (case-insensitive) to use.

## Acceptance criteria
- Visual: at 30–60 cm, colors mix optically; dots visible only up close.
- Geometry: dots distinct, not smeared; height ≤2 layers; base flat; no overhang of dots beyond base.
- Process: 3MF opens with correct AMS assignments and purge tower enabled; metadata retained for reproducibility.
