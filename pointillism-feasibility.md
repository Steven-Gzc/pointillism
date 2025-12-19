# Pointillist 3D Printing on Bambu Lab A1 + AMS (0.2 mm Nozzle)

## Objective
Adapt Seurat-style pointillism to a Bambu Lab A1 with AMS using a 0.2 mm nozzle, focusing on achievable dot size, slicing strategy, and settings that minimize bleed and waste.

## What the Hardware Enables
- AMS gives up to 4 colors with automatic swaps; expect purge towers or flush volumes per change.
- 0.2 mm nozzle supports finer features: typical extrusion width 0.22–0.28 mm, practical colored dot diameter about 0.25–0.35 mm.
- Layer height: 0.08–0.12 mm keeps dots low-profile and visually flush.
- XY precision is good, but stringing and ooze must be controlled to keep dots crisp.

## Achievable Dot Size and Spacing (A1 + AMS, 0.2 mm)
- Aim for dot diameter 0.25–0.35 mm; center-to-center spacing 0.35–0.50 mm to avoid color bleed.
- At 30–60 cm viewing distance, these should visually mix; up close, dots remain visible (pointillist intent).
- Keep dot height to 1–2 layers so the surface stays smooth and optical, not tactile.

## Palette and Materials
- Use 3–4 filaments approximating CMY + K or a reduced palette matched to the artwork’s dominant hues.
- Prefer matte PLA to avoid specular highlights that break blending.
- Keep a dated swatch card per filament batch for repeatability.

## Image to Toolpath Workflow (Bambu Studio)
1) Image prep: Resize to the final print size. Apply ordered or error-diffusion dithering with minimum dot size of about 0.25 mm and spacing about 0.4 mm (matches 0.2 mm nozzle constraints).
2) Geometry: Project each color’s dot layer onto a thin base tile (single shell, 1–2 layers). Keep dots as single-extrusion pixels at full flow (no thin-wall scaling).
3) Import: Load the base and per-color meshes into Bambu Studio; assign each color mesh to a tool slot in the AMS.
4) Slicing:
   - Nozzle: 0.2 mm; line width 0.22–0.28 mm; layer height 0.08–0.12 mm.
   - Speeds: External walls 35–45 mm/s; small perimeters slow; travel as short as possible.
   - Temps: Lower end of filament spec (for PLA, about 195–205 C) to reduce ooze.
   - Retraction/pressure advance: Use Bambu defaults; enable wipe or coast if available for the filament profile.
   - Z-hop off to avoid Z-scars; use combing within infill if it shortens travels.
   - Cooling: 100% part fan after first layers for sharper dots.
5) Purge management:
   - Use AMS flush volumes tuned per filament (print a calibration tower to measure color change distance).
   - Enable flush tower; use flush into infill only if the model has infill space (flat tiles usually do not).
   - Cluster same-color dots in your dithering algorithm if possible to reduce swap count.

## Calibration Prints (A1, 0.2 mm)
- Print a 50 x 50 mm tile with a 4-color gradient dither. Vary spacing bands: 0.35 / 0.40 / 0.45 / 0.50 mm. Inspect bleed and registration.
- Print a purge calibration tower for each filament pair to set AMS flush volumes accurately.
- Test matte vs. glossy PLA on the same pattern to see sheen impact on blending.

## Risks and Mitigations (Specific to A1 + AMS)
- Dot blur from ooze or heat: Run cooler temps; keep fan high; use shorter layer times by printing multiple tiles to avoid lingering heat.
- Swap time and waste: Limit palette to 3–4 colors; cluster colors; accept tower waste; prefer shorter prints to learn flush volumes quickly.
- Registration drift: Keep belts tensioned; slow small perimeters; avoid aggressive accelerations on tiny features.
- Surface artifacts: Keep dots to 1–2 layers; disable elephant foot compensation on thin tiles; use a smooth PEI sheet for clean bottoms.

## Feasibility Verdict for This Setup
- With a 0.2 mm nozzle and AMS, pointillist halftoning is practical for small wall tiles and plaques. Dots will be visible at close range but blend at normal viewing distances. Key constraints are purge waste and managing ooze; both are manageable with calibration and a reduced palette.

## Suggested First Run
1) Choose 4 matte PLA colors approximating CMYK.
2) Dither a 60 x 60 mm test image to 0.25–0.35 mm dots at 0.40–0.45 mm spacing.
3) Slice at 0.1 mm layer height, 0.24–0.26 mm line width, external walls 40 mm/s, PLA at about 200 C, fan 100%.
4) Enable flush tower; use measured flush volumes from a calibration print.
5) Evaluate dot sharpness and bleed; adjust spacing and temperature and rerun if needed. Use the best spacing in your final artwork.

## Seurat Palette Notes: A Sunday on La Grande Jatte
- Likely pigments: lead white and zinc white; chrome yellow and zinc yellow; vermilion; red lake/madder lake; French ultramarine; cobalt blue; emerald green (copper acetoarsenite) and viridian/chrome green; ochres and raw sienna; ivory/charcoal black (used sparingly); violet and orange mixtures from ultramarine plus red lake and yellow.
- Color pairs he emphasized: blue-orange, red-green, and violet-yellow complements for optical vibration.
- Fading behavior: zinc yellow can brown or fade; red lakes can lose saturation, which is why some areas look muted today compared to 1880s intent.
- Mapping to AMS palette: pick matte cyan/blue, magenta/red, yellow, and a dark neutral (black or deep indigo). Optionally add a warm orange if you want stronger orange-blue contrasts with fewer swaps in greens.
