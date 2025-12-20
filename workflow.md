# Pointillist 3MF Workflow (Bambu Lab A1 + AMS, 0.2 mm)

End goal: from a source image and an AMS palette, produce halftoned dot geometry, STLs, and a sliced 3MF for pointillist tiles on the A1 with a 0.2 mm nozzle.

## Inputs
- Source image: PNG/JPEG, cropped to final aspect.
- Palette: 3-4 colors (CMYK-ish recommended) with hex codes; see `bambu-pla-matte-hex-codes.md`.
- Hardware: Bambu Lab A1 + AMS; nozzle 0.2 mm; filament profiles for chosen colors.

## Outputs
- Dithered per-color bitmaps.
- Dot geometry: base tile STL plus per-color dot STLs; SVG for reference/import.
- A sliced Bambu Studio project (3MF) targeting A1 with AMS assignments and purge settings.

## Target Print Parameters
- Nozzle 0.2 mm; line width 0.22-0.28 mm; layer height 0.08-0.12 mm.
- Dot diameter 0.25-0.35 mm; center spacing 0.35-0.50 mm.
- Speeds: external 35-45 mm/s; small perimeters slow.
- Temp: 195-205 C for PLA (low end to reduce ooze); fan 100% after first layers.
- Dots 1-2 layers tall for a flush surface.

## Workflow (pipeline)
1) **Palette selection**  
   - Choose 3-4 filaments. Prefer matte PLA. Map each to AMS slot (T0-T3).
2) **Image prep**  
   - Resize so pixel pitch equals desired dot spacing (e.g., 0.4 mm per pixel).  
   - Apply ordered or error-diffusion dithering to the limited palette; enforce minimum run length per color if possible.
3) **Dot geometry generation**  
   - Convert “on” pixels to circles of diameter 0.25-0.35 mm at the chosen spacing.  
   - Project all circles onto a thin base tile (1-2 layers, single shell). Keep dots at full extrusion width.  
   - Export per-color meshes or a multi-part 3MF with labeled parts per color.
4) **Slicing in Bambu Studio**  
   - Import the base and color meshes; assign each to the corresponding AMS tool.  
   - Nozzle 0.2 mm, line width 0.24-0.26 mm, layer height 0.10 mm.  
   - Temps per filament at low end; fan 100%; Z-hop off; combing within infill.  
   - Enable flush tower; set flush volumes from calibration.  
   - Short travels; slow small perimeters; optional wipe/coast if available.
5) **Export**  
   - Save the Bambu Studio project as `.3mf` with AMS assignments.  
   - Keep STL/3MF and dithered bitmaps for reproducibility.

## Calibration Loop
- **Flush volumes**: print a color-change calibration tower for each filament pair; record mm needed for clean transition; update AMS flush.  
- **Dot spacing test**: print a 50x50 mm 4-color gradient tile with bands 0.35 / 0.40 / 0.45 / 0.50 mm; inspect bleed/registration and pick the best spacing.  
- **Sheen**: compare matte vs. glossy on the same test.

## Automation
- Generator:  
  ```
  python pointillism_pipeline.py A_Sunday_on_La_Grande_Jatte.jpg bambu-pla-matte-hex-codes.md out
  ```  
  Defaults: width 100 mm, spacing 0.4 mm, dot 0.3 mm, dot height 0.2 mm, base 0.2 mm, 24 segments, palette = Sky Blue, Scarlet Red, Lemon Yellow, Charcoal.  
  Outputs: `dithered.png`, per-color `mask_*.png`, `dots.svg`, `metadata.json`, and STLs (`base.stl` plus one per color).  
  Import STLs into CAD if you want to merge; in Bambu Studio assign each color STL to its AMS tool, 0.2 mm nozzle, 0.1 mm layer height, 0.24-0.26 mm line width, 195-205 C PLA, fan 100%, flush tower on with tuned flush volumes.  
- Optional: auto-generate a Bambu Studio 3MF template by duplicating a known-good project and swapping meshes via 3MF XML (ZIP) edits.  
- Palette data: keep as JSON/CSV or the provided Markdown; include AMS tool mapping and purge length per filament.

## Acceptance Criteria
- Visual: at 30-60 cm, colors optically mix; dots visible only on close inspection.  
- Geometry: dots are distinct, not smeared; height <=2 layers; base tile flat.  
- Process: 3MF opens with correct AMS assignments, purge tower enabled, and tuned flush volumes.  
- Reproducibility: source image, palette file, dithered bitmaps, and generated meshes are versioned alongside the 3MF.
