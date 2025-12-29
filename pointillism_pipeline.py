#!/usr/bin/env python3
"""
Generate pointillist dot data and an SVG from an image and palette for Bambu A1 + AMS (0.2 mm).

Outputs (in the chosen output directory):
- dithered.png: image reduced to the selected palette with error-diffusion.
- mask_<color>.png: per-color binary masks.
- dots.svg: circles in millimeters for import to CAD/slicer.
- metadata.json: parameters, palette, and dot positions for reproducibility.

Notes:
- Bring dots.svg (or per-color masks) into your CAD tool to extrude onto a thin base.
- In Bambu Studio, assign each color mesh/mask to the matching AMS tool, set 0.2 mm nozzle, ~0.1 mm layer height, 0.24–0.26 mm line width, 195–205 C PLA, and enable a flush tower with tuned flush volumes.
"""

import argparse
import json
import math
import pathlib
import re
from typing import Dict, List, Sequence, Tuple

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - Pillow may be absent in some environments
    raise SystemExit(
        "Pillow is required. Install with `pip install pillow` inside your environment."
    ) from exc

Color = Tuple[int, int, int]
Triangle = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]


def _parse_hex(s: str) -> Color:
    s = s.strip().lstrip("#")
    if len(s) != 6 or not all(c in "0123456789abcdefABCDEF" for c in s):
        raise ValueError(f"Invalid hex color: {s}")
    return tuple(int(s[i : i + 2], 16) for i in range(0, 6, 2))  # type: ignore[return-value]


def load_palette(path: pathlib.Path, select: Sequence[str] | None = None) -> List[Tuple[str, Color]]:
    """
    Load a palette from a .json (list of objects with name/hex) or a Markdown table (Name | Hex).
    The Markdown loader is tailored to bambu-pla-matte-hex-codes.md.
    """
    text = path.read_text(encoding="utf-8")
    colors: List[Tuple[str, Color]] = []

    if path.suffix.lower() == ".json":
        data = json.loads(text)
        for item in data:
            name = item["name"]
            hex_code = item["hex"]
            colors.append((name, _parse_hex(hex_code)))
    else:
        for line in text.splitlines():
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2 or parts[0].lower() == "name":
                continue
            name = parts[0]
            hex_candidates = [p for p in parts[1:] if "#" in p]
            if not hex_candidates:
                continue
            hex_code = re.findall(r"#?[0-9A-Fa-f]{6}", hex_candidates[0])
            if not hex_code:
                continue
            colors.append((name, _parse_hex(hex_code[0])))

    if select:
        lower = {s.lower() for s in select}
        colors = [(n, c) for n, c in colors if n.lower() in lower]

    if not colors:
        raise ValueError("Palette is empty after loading/filtering.")
    return colors


def resize_image_hex(img: Image.Image, target_width_mm: float, spacing_mm: float) -> Image.Image:
    """
    Resize so that horizontal center-to-center spacing equals spacing_mm.
    Height is derived from aspect; vertical pitch is spacing_mm * sqrt(3)/2.
    """
    target_px_w = max(1, int(round(target_width_mm / spacing_mm)))
    aspect = img.height / img.width
    target_px_h = max(1, int(round(target_px_w * aspect)))
    return img.resize((target_px_w, target_px_h), resample=Image.Resampling.LANCZOS)


def nearest_color(color: Color, palette: List[Tuple[str, Color]]) -> Tuple[str, Color]:
    cr, cg, cb = color
    best = palette[0]
    best_dist = float("inf")
    for name, (pr, pg, pb) in palette:
        dist = (cr - pr) ** 2 + (cg - pg) ** 2 + (cb - pb) ** 2
        if dist < best_dist:
            best = (name, (pr, pg, pb))
            best_dist = dist
    return best


def floyd_steinberg_dither(img: Image.Image, palette: List[Tuple[str, Color]]) -> Tuple[Image.Image, List[List[str]]]:
    """
    Return a palettized image and a same-sized grid of palette names for geometry generation.
    """
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size
    color_grid: List[List[str]] = [["" for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            old_r, old_g, old_b = pixels[x, y]
            name, (nr, ng, nb) = nearest_color((old_r, old_g, old_b), palette)
            pixels[x, y] = (nr, ng, nb)
            color_grid[y][x] = name
            err_r = old_r - nr
            err_g = old_g - ng
            err_b = old_b - nb

            def add_error(px: int, py: int, fr: float, fg: float, fb: float) -> None:
                if 0 <= px < width and 0 <= py < height:
                    pr, pg, pb = pixels[px, py]
                    pr = min(255, max(0, int(pr + fr)))
                    pg = min(255, max(0, int(pg + fg)))
                    pb = min(255, max(0, int(pb + fb)))
                    pixels[px, py] = (pr, pg, pb)

            add_error(x + 1, y, err_r * 7 / 16, err_g * 7 / 16, err_b * 7 / 16)
            add_error(x - 1, y + 1, err_r * 3 / 16, err_g * 3 / 16, err_b * 3 / 16)
            add_error(x, y + 1, err_r * 5 / 16, err_g * 5 / 16, err_b * 5 / 16)
            add_error(x + 1, y + 1, err_r * 1 / 16, err_g * 1 / 16, err_b * 1 / 16)

    return img, color_grid


def export_masks(
    color_grid: List[List[str]],
    palette: List[Tuple[str, Color]],
    spacing_mm: float,
    dot_diameter_mm: float,
    out_dir: pathlib.Path,
) -> Dict[str, List[Tuple[float, float]]]:
    height = len(color_grid)
    width = len(color_grid[0])
    coords: Dict[str, List[Tuple[float, float]]] = {name: [] for name, _ in palette}
    pitch = spacing_mm * math.sqrt(3) / 2
    radius = dot_diameter_mm / 2
    width_limit = (width - 1) * spacing_mm + dot_diameter_mm

    for y in range(height):
        for x in range(width):
            name = color_grid[y][x]
            # Hex stagger: odd rows offset by half spacing; vertical pitch is spacing * sqrt(3)/2
            x_off = spacing_mm / 2 if (y % 2 == 1) else 0.0
            y_mm = radius + y * pitch
            x_mm = radius + x * spacing_mm + x_off
            if x_mm > width_limit - radius:  # drop overhanging dots on staggered rows
                continue
            coords[name].append((x_mm, y_mm))

    for name, color in palette:
        mask_img = Image.new("1", (width, height), 0)
        mask_pixels = mask_img.load()
        for idx, (cx, cy) in enumerate(coords[name]):
            # Reverse mapping: nearest pixel index; good enough for reference masks
            px = min(width - 1, max(0, int(round((cx - radius) / spacing_mm))))
            py = min(height - 1, max(0, int(round((cy - radius) / pitch))))
            mask_pixels[px, py] = 1
        mask_img.save(out_dir / f"mask_{slugify(name)}.png")
    return coords


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _add_box(tris: List[Triangle], x0: float, y0: float, x1: float, y1: float, z0: float, z1: float) -> None:
    """
    Add triangles for a rectangular prism defined by opposite corners.
    """
    # Bottom
    tris.append(((x0, y0, z0), (x1, y0, z0), (x1, y1, z0)))
    tris.append(((x0, y0, z0), (x1, y1, z0), (x0, y1, z0)))
    # Top
    tris.append(((x0, y0, z1), (x1, y1, z1), (x1, y0, z1)))
    tris.append(((x0, y0, z1), (x0, y1, z1), (x1, y1, z1)))
    # Sides
    tris.append(((x0, y0, z0), (x0, y0, z1), (x1, y0, z1)))
    tris.append(((x0, y0, z0), (x1, y0, z1), (x1, y0, z0)))

    tris.append(((x1, y0, z0), (x1, y0, z1), (x1, y1, z1)))
    tris.append(((x1, y0, z0), (x1, y1, z1), (x1, y1, z0)))

    tris.append(((x1, y1, z0), (x1, y1, z1), (x0, y1, z1)))
    tris.append(((x1, y1, z0), (x0, y1, z1), (x0, y1, z0)))

    tris.append(((x0, y1, z0), (x0, y1, z1), (x0, y0, z1)))
    tris.append(((x0, y1, z0), (x0, y0, z1), (x0, y0, z0)))


def _add_cylinder(tris: List[Triangle], cx: float, cy: float, r: float, z0: float, z1: float, segments: int = 24) -> None:
    """
    Approximate a vertical cylinder with given radius and z extents using segmented circles.
    """
    two_pi = 2 * math.pi
    for i in range(segments):
        a0 = two_pi * i / segments
        a1 = two_pi * (i + 1) / segments
        x0 = cx + r * math.cos(a0)
        y0 = cy + r * math.sin(a0)
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)

        # Side quad split into two triangles
        tris.append(((x0, y0, z0), (x1, y1, z0), (x1, y1, z1)))
        tris.append(((x0, y0, z0), (x1, y1, z1), (x0, y0, z1)))

        # Top fan
        tris.append(((cx, cy, z1), (x1, y1, z1), (x0, y0, z1)))
        # Bottom fan
        tris.append(((cx, cy, z0), (x0, y0, z0), (x1, y1, z0)))


def write_ascii_stl(tris: List[Triangle], name: str, path: pathlib.Path) -> None:
    """
    Write triangles to an ASCII STL file.
    """
    with path.open("w", encoding="ascii") as fh:
        fh.write(f"solid {name}\n")
        for (p1, p2, p3) in tris:
            fh.write("facet normal 0 0 0\n  outer loop\n")
            fh.write(f"    vertex {p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f}\n")
            fh.write(f"    vertex {p2[0]:.6f} {p2[1]:.6f} {p2[2]:.6f}\n")
            fh.write(f"    vertex {p3[0]:.6f} {p3[1]:.6f} {p3[2]:.6f}\n")
            fh.write("  endloop\nendfacet\n")
        fh.write(f"endsolid {name}\n")


def export_svg(
    coords: Dict[str, List[Tuple[float, float]]],
    palette: List[Tuple[str, Color]],
    dot_diameter_mm: float,
    width_mm: float,
    height_mm: float,
    out_path: pathlib.Path,
) -> None:
    radius = dot_diameter_mm / 2

    def color_hex(name: str) -> str:
        for n, c in palette:
            if n == name:
                return "#" + "".join(f"{v:02X}" for v in c)
        return "#000000"

    # Background uses charcoal (if present) to match the darkest filament; else black.
    charcoal = "#000000"
    for n, c in palette:
        if n.lower() == "charcoal":
            charcoal = "#" + "".join(f"{v:02X}" for v in c)
            break

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm}mm" height="{height_mm}mm" viewBox="0 0 {width_mm} {height_mm}">',
        f'<rect x="0" y="0" width="{width_mm}" height="{height_mm}" fill="{charcoal}" />',
    ]

    for name, positions in coords.items():
        fill = color_hex(name)
        lines.append(f'<g id="{slugify(name)}" fill="{fill}">')
        for x_mm, y_mm in positions:
            lines.append(f'<circle cx="{x_mm:.3f}" cy="{y_mm:.3f}" r="{radius:.3f}" />')
        lines.append("</g>")

    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def export_stl_meshes(
    coords: Dict[str, List[Tuple[float, float]]],
    palette: List[Tuple[str, Color]],
    width_mm: float,
    height_mm: float,
    dot_diameter_mm: float,
    dot_height_mm: float,
    base_thickness_mm: float,
    segments: int,
    out_dir: pathlib.Path,
) -> Dict[str, str]:
    """
    Export base tile and per-color dot meshes as STL files.
    Returns mapping of part name to filename.
    """
    radius = dot_diameter_mm / 2.0

    # Base tile
    base_tris: List[Triangle] = []
    _add_box(base_tris, 0.0, 0.0, width_mm, height_mm, 0.0, base_thickness_mm)
    base_name = "base"
    base_file = out_dir / f"{base_name}.stl"
    write_ascii_stl(base_tris, base_name, base_file)

    files: Dict[str, str] = {"base": base_file.name}

    for name, positions in coords.items():
        tris: List[Triangle] = []
        z0 = base_thickness_mm
        z1 = base_thickness_mm + dot_height_mm
        for x_mm, y_mm in positions:
            _add_cylinder(tris, x_mm, y_mm, radius, z0, z1, segments=segments)
        part_name = slugify(name)
        part_file = out_dir / f"{part_name}.stl"
        write_ascii_stl(tris, part_name, part_file)
        files[part_name] = part_file.name
    return files


def save_metadata(out_path: pathlib.Path, meta: dict) -> None:
    out_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def run(
    image_path: pathlib.Path,
    palette_path: pathlib.Path,
    out_dir: pathlib.Path,
    selected_colors: Sequence[str] | None,
    width_mm: float,
    spacing_mm: float,
    dot_diameter_mm: float,
    dot_height_mm: float,
    base_thickness_mm: float,
    segments: int,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    palette = load_palette(palette_path, select=selected_colors)

    img = Image.open(image_path)
    resized = resize_image_hex(img, width_mm, spacing_mm)
    pal_img, color_grid = floyd_steinberg_dither(resized, palette)

    pal_img.save(out_dir / "dithered.png")
    coords = export_masks(color_grid, palette, spacing_mm, dot_diameter_mm, out_dir)
    pitch = spacing_mm * math.sqrt(3) / 2
    radius = dot_diameter_mm / 2
    width_limit = (resized.width - 1) * spacing_mm + dot_diameter_mm

    # Compute actual extents from generated coordinates (accounts for stagger offsets).
    all_points = [pt for pts in coords.values() for pt in pts]
    max_x = max(pt[0] for pt in all_points) if all_points else 0.0
    max_y = max(pt[1] for pt in all_points) if all_points else 0.0
    width_mm_used = max(width_limit, max_x + radius)
    height_mm_used = max_y + radius

    export_svg(
        coords,
        palette,
        dot_diameter_mm,
        width_mm_used,
        height_mm_used,
        out_dir / "dots.svg",
    )

    stl_files = export_stl_meshes(
        coords,
        palette,
        width_mm_used,
        height_mm_used,
        dot_diameter_mm,
        dot_height_mm,
        base_thickness_mm,
        segments,
        out_dir,
    )

    total_dots = sum(len(v) for v in coords.values())
    dot_area = math.pi * (dot_diameter_mm / 2) ** 2
    total_area = width_mm_used * height_mm_used if width_mm_used > 0 and height_mm_used > 0 else 1
    coverage_fraction = (total_dots * dot_area) / total_area

    metadata = {
        "image": str(image_path),
        "palette_file": str(palette_path),
        "selected_colors": [c for c in selected_colors] if selected_colors else "all",
        "width_mm": width_mm,
        "spacing_mm": spacing_mm,
        "dot_diameter_mm": dot_diameter_mm,
        "dot_height_mm": dot_height_mm,
        "base_thickness_mm": base_thickness_mm,
        "segments": segments,
        "pixel_dimensions": {"width": resized.width, "height": resized.height},
        "grid": {
            "type": "hex_staggered",
            "vertical_pitch_mm": pitch,
            "width_mm": width_mm_used,
            "height_mm": height_mm_used,
        },
        "coverage": {
            "total_dots": total_dots,
            "dot_area_mm2": dot_area,
            "coverage_area_mm2": total_dots * dot_area,
            "coverage_fraction": coverage_fraction,
            "coverage_percent": coverage_fraction * 100,
        },
        "palette": [{ "name": n, "rgb": c } for n, c in palette],
        "stl_files": stl_files,
    }
    save_metadata(out_dir / "metadata.json", metadata)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pointillist dots and SVG for Bambu A1 + AMS.")
    parser.add_argument(
        "image",
        type=pathlib.Path,
        nargs="?",
        default=pathlib.Path("sailboat.jpg"),
        help="Input image (PNG/JPEG). Defaults to sailboat.jpg",
    )
    parser.add_argument(
        "palette",
        type=pathlib.Path,
        nargs="?",
        default=pathlib.Path("bambu-pla-matte-hex-codes.md"),
        help="Palette file (.json or Markdown table with Name|Hex). Defaults to bambu-pla-matte-hex-codes.md",
    )
    parser.add_argument(
        "out_dir",
        type=pathlib.Path,
        nargs="?",
        default=pathlib.Path("out"),
        help="Output directory for artifacts. Defaults to ./out",
    )
    parser.add_argument("--width-mm", type=float, default=180.0, help="Physical width of the print in mm (default: 180).")
    parser.add_argument("--spacing-mm", type=float, default=0.8, help="Dot spacing in mm (default: 0.8).")
    parser.add_argument("--dot-mm", type=float, default=0.8, help="Dot diameter in mm (default: 0.8).")
    parser.add_argument("--dot-height-mm", type=float, default=0.4, help="Dot height in mm (default: 0.4).")
    parser.add_argument("--base-thickness-mm", type=float, default=0.6, help="Base tile thickness in mm (default: 0.6).")
    parser.add_argument("--segments", type=int, default=12, help="Segments to approximate dot circles (default: 12; lower = fewer triangles, faster export/smaller files).")
    parser.add_argument(
        "--colors",
        type=str,
        default="Sky Blue,Scarlet Red,Lemon Yellow,Charcoal",
        help="Comma-separated color names to use from the palette (case-insensitive). Default: Sky Blue, Scarlet Red, Lemon Yellow, Charcoal.",
    )

    args = parser.parse_args()
    selected_colors = [c.strip() for c in args.colors.split(",") if c.strip()] or None

    run(
        image_path=args.image,
        palette_path=args.palette,
        out_dir=args.out_dir,
        selected_colors=selected_colors,
        width_mm=args.width_mm,
        spacing_mm=args.spacing_mm,
        dot_diameter_mm=args.dot_mm,
        dot_height_mm=args.dot_height_mm,
        base_thickness_mm=args.base_thickness_mm,
        segments=args.segments,
    )


if __name__ == "__main__":
    main()
