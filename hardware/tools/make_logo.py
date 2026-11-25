"""Turns media/IDESynthLogo.png into the board's silkscreen logo:
libraries.pretty/IDESynth_Logo_<height>mm.kicad_mod.

Run with KiCad's own Python (it has pcbnew):
  macOS:   /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 \
             hardware/tools/make_logo.py [height_mm] [--pbm preview.pbm]
  Windows: "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/tools/make_logo.py [height_mm]

Silkscreen is one colour, so dark pixels become silk and everything else stays bare: the discs'
grey shading drops out, leaving their black outlines. Silkscreen prints nothing under about
0.15 mm, so the image is sampled at PX mm per pixel and every stroke widened by a pixel each side,
which keeps the thin outer sound waves and "Synth" printable.

The PNG is read with Pillow where KiCad's Python has it (Windows), else converted to BMP with
macOS's sips and read here, so nothing needs installing. Adapted from IDE Synth Bay's
hardware/tools/make_logo.py.
"""
import struct
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sexpr import Sym as S, dump  # noqa: E402

HW = Path(__file__).resolve().parent.parent
SRC = HW.parent / "media" / "IDESynthLogo.png"
PX = 0.04          # mm per pixel
DARK = 128         # luminance below this is silk


def luminance_rows():
    """The image as rows of luminance (0-255)."""
    try:
        from PIL import Image
        im = Image.open(SRC).convert("L")
        w, h = im.size
        data = list(im.getdata())
        return [data[y * w:(y + 1) * w] for y in range(h)]
    except ImportError:
        pass
    with tempfile.TemporaryDirectory() as tmp:
        bmp = Path(tmp) / "logo.bmp"
        subprocess.run(["sips", "-s", "format", "bmp", str(SRC), "--out", str(bmp)],
                       check=True, capture_output=True)
        raw = bmp.read_bytes()
    offset, = struct.unpack_from("<I", raw, 10)
    w, h, _, bpp = struct.unpack_from("<iiHH", raw, 18)
    if bpp not in (24, 32):
        sys.exit(f"unexpected BMP depth {bpp}")
    step = bpp // 8
    stride = (w * step + 3) & ~3
    rows = []
    for y in range(abs(h)):
        base = offset + (abs(h) - 1 - y if h > 0 else y) * stride   # BMP rows run bottom-up
        rows.append([round(0.114 * raw[base + x * step] + 0.587 * raw[base + x * step + 1]
                           + 0.299 * raw[base + x * step + 2]) for x in range(w)])
    return rows


def ink(height_mm):
    """Rows of booleans (True: silkscreen), height_mm tall on the PX grid."""
    lum = luminance_rows()
    dark = [[v < DARK for v in row] for row in lum]
    ys = [y for y, row in enumerate(dark) if any(row)]
    xs = [x for x in range(len(dark[0])) if any(row[x] for row in dark)]
    dark = [row[xs[0]:xs[-1] + 1] for row in dark[ys[0]:ys[-1] + 1]]   # to the ink: the image has margins
    h, w = len(dark), len(dark[0])
    rows = round(height_mm / PX)
    cols = round(w * rows / h)
    # Area-average each target pixel's source box; half or more dark is silk.
    thin = []
    for ty in range(rows):
        y0, y1 = ty * h // rows, max((ty + 1) * h // rows, ty * h // rows + 1)
        line = []
        for tx in range(cols):
            x0, x1 = tx * w // cols, max((tx + 1) * w // cols, tx * w // cols + 1)
            n = sum(dark[y][x] for y in range(y0, y1) for x in range(x0, x1))
            line.append(2 * n >= (y1 - y0) * (x1 - x0))
        thin.append(line)
    # Widen strokes by one pixel in each direction.
    return [[any(thin[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                 if 0 <= y + dy < rows and 0 <= x + dx < cols) for x in range(cols)] for y in range(rows)]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    height_mm = float(args[0]) if args else 9.5
    name = f"IDESynth_Logo_{height_mm:g}mm".replace(".", "_")
    out = HW / "libraries.pretty" / f"{name}.kicad_mod"
    fat = ink(height_mm)
    h, w = len(fat), len(fat[0])
    if "--pbm" in sys.argv:
        Path(sys.argv[sys.argv.index("--pbm") + 1]).write_text(
            f"P1\n{w} {h}\n" + "\n".join(" ".join("1" if v else "0" for v in row) for row in fat) + "\n")

    poly = pcbnew.SHAPE_POLY_SET()
    x0, y0 = -w * PX / 2, -h * PX / 2
    for y, row in enumerate(fat):
        x = 0
        while x < w:
            if not row[x]:
                x += 1
                continue
            start = x
            while x < w and row[x]:
                x += 1
            poly.NewOutline()
            for px, py in ((start, y), (x, y), (x, y + 1), (start, y + 1)):
                poly.Append(pcbnew.FromMM(x0 + px * PX), pcbnew.FromMM(y0 + py * PX))
    poly.Simplify()
    poly.Fracture()

    def u(*k):
        return [S("uuid"), str(uuid.uuid5(uuid.NAMESPACE_URL, f"idesynth/{name}/" + "/".join(map(str, k))))]

    fx = [S("effects"), [S("font"), [S("size"), 1, 1], [S("thickness"), 0.15]]]
    fp = [S("footprint"), name, [S("version"), 20241229], [S("generator"), "idesynth_make_logo"],
          [S("generator_version"), "1.0"], [S("layer"), "F.Cu"],
          [S("descr"), f"IDE Synth logo, silkscreen, {w * PX:.1f} x {h * PX:.1f} mm, from media/IDESynthLogo.png"],
          [S("tags"), "logo"],
          [S("property"), "Reference", "G***", [S("at"), 0, -h * PX / 2 - 1.5, 0], [S("layer"), "F.SilkS"],
           [S("hide"), S("yes")], u("ref"), fx],
          [S("property"), "Value", "LOGO", [S("at"), 0, h * PX / 2 + 1.5, 0], [S("layer"), "F.Fab"],
           [S("hide"), S("yes")], u("val"), fx],
          [S("attr"), S("board_only"), S("exclude_from_pos_files"), S("exclude_from_bom")]]
    for i in range(poly.OutlineCount()):
        ol = poly.Outline(i)
        pts = [S("pts")] + [[S("xy"), round(pcbnew.ToMM(ol.CPoint(k).x), 4), round(pcbnew.ToMM(ol.CPoint(k).y), 4)]
                            for k in range(ol.PointCount())]
        fp.append([S("fp_poly"), pts, [S("stroke"), [S("width"), 0], [S("type"), S("solid")]], [S("fill"), S("yes")],
                   [S("layer"), "F.SilkS"], u("poly", i)])
    fp.append([S("embedded_fonts"), S("no")])
    out.write_text(dump(fp) + "\n")
    print(f"wrote {out.name}: {w * PX:.1f} x {h * PX:.1f} mm, {poly.OutlineCount()} polygons")


if __name__ == "__main__":
    main()
