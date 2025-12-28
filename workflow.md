# Pointillist 3MF Workflow (Bambu Lab A1 + AMS, 0.4 mm)

End goal: from a source image and an AMS palette, produce halftoned dot geometry, STLs, and a sliced 3MF for pointillist tiles on the A1 with a 0.4 mm nozzle.

## Inputs
- Source image: PNG/JPEG, cropped to final aspect.
- Palette: 3-4 colors (CMYK-ish recommended) with hex codes; see `bambu-pla-matte-hex-codes.md`.
- Hardware: Bambu Lab A1 + AMS; nozzle 0.4 mm; filament profiles for chosen colors.

## Outputs
- Dithered per-color bitmaps.
- Dot geometry: base tile STL plus per-color dot STLs; SVG for reference/import.
- A sliced Bambu Studio project (3MF) targeting A1 with AMS assignments and purge settings.

## Workflow (pipeline)
1) **Palette selection**  
   - Choose 3-4 filaments. Prefer matte PLA. Map each to AMS slot (T0-T3).
2) **Image prep**  
   - Resize so pixel pitch equals desired dot spacing (e.g., 0.8 mm per pixel).  
   - Apply ordered or error-diffusion dithering to the limited palette; enforce minimum run length per color if possible.
3) **Dot geometry generation**  
   - Convert “on” pixels to circles at the chosen diameter and spacing.  
   - Project all circles onto a thin base tile. Keep dots at full extrusion width.  
   - Export per-color meshes or a multi-part 3MF with labeled parts per color.

## Workflow (manual)
1) **Slicing in Bambu Studio**  
   - Import the multi-part 3MF; assign each to the corresponding filement.  
   - Example1: Nozzle 0.4 mm, line width 0.4 mm, layer height 0.08 mm. 100% infill. Mirror along Y axis (the model is upside down for some reason).
   - Enable flush tower.
   - Optional: set flush volumes from calibration. Short travels; slow small perimeters; optional wipe/coast if available.
2) **Export**  
   - Save the Bambu Studio project as `.3mf` with AMS assignments.  
   - Keep STL/3MF and dithered bitmaps for reproducibility.

## Calibration Loop
- **Flush volumes**: print a color-change calibration tower for each filament pair; record mm needed for clean transition; update AMS flush.  
- **Dot spacing test**: print a 50x50 mm 4-color gradient tile with bands 0.35 / 0.40 / 0.45 / 0.50 mm; inspect bleed/registration and pick the best spacing.  
- **Sheen**: compare matte vs. glossy on the same test.

## Automation
- Generator:  
  ```
  python pointillism_pipeline.py sailboat.jpg bambu-pla-matte-hex-codes.md out
  ```  
  Defaults: width 180 mm, spacing 0.8 mm (center-to-center, hex grid), dot 0.8 mm, dot height 0.4 mm, base 0.6 mm, 12 segments, palette = Sky Blue, Scarlet Red, Lemon Yellow, Charcoal.  
  Outputs: `dithered.png`, per-color `mask_*.png`, `dots.svg`, `metadata.json`, and STLs (`base.stl` plus one per color).  
  Import STLs into CAD if you want to merge; in Bambu Studio assign each color STL to its AMS tool, 0.4 mm nozzle, 0.08 mm layer height, 0.4 mm line width, flush tower on with tuned flush volumes.  


## Parameter definitions
- width-mm: physical width of the printed tile. The image is resampled so that (pixels * spacing-mm) == width-mm.
- spacing-mm: center-to-center grid pitch for dots. Every pixel maps to a dot center spaced this far apart; it is not edge-to-edge.
- dot-mm: dot diameter (used for SVG and STL cylinders).
- dot-height-mm: dot height above the base.
- base-thickness-mm: thickness of the flat base tile before dots.
- segments: number of facets used to approximate each circular dot in STL.

