#!/usr/bin/env python3
"""
Render the dumped Fragments Blue glyph cache (../glyphcache.bin, 506880 bytes)
to labeled PNG sheets so each glyph index can be identified.

Cache format (verified from draw fn 0x1A1CD0 -> 0x1A1D50):
  - 144 bytes per glyph = 24x24 pixels, 2bpp
  - row-major, 6 bytes/row, 4 pixels/byte, pixel0 = bits 0-1 (LSB-first)
  - value 0 = background (transparent); 1/2/3 = foreground shades (AA)

Usage: python render_glyphs.py [glyphcache.bin]
Writes sheets/sheet_000.png .. with 256 glyphs each, index labeled.
Also prints ASCII art of the first glyphs to confirm the bit order.
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont

W = H = 24
REC = 144
BPR = 6  # bytes per row (24 px * 2bpp / 8)

def render(rec, lsb=True):
    img = Image.new("L", (W, H), 255)
    px = img.load()
    for y in range(H):
        for xb in range(BPR):
            b = rec[y * BPR + xb]
            for p in range(4):
                v = (b >> (p * 2)) & 3 if lsb else (b >> ((3 - p) * 2)) & 3
                x = xb * 4 + p
                if x < W:
                    px[x, y] = [255, 200, 120, 0][v]  # 0=white,3=black
    return img

def ascii_art(rec, lsb=True):
    lines = []
    for y in range(H):
        s = ""
        for xb in range(BPR):
            b = rec[y * BPR + xb]
            for p in range(4):
                v = (b >> (p * 2)) & 3 if lsb else (b >> ((3 - p) * 2)) & 3
                s += " .-#"[v]
        lines.append(s.rstrip())
    return "\n".join(lines)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "../glyphcache.bin"
    data = open(path, "rb").read()
    n = len(data) // REC
    print("cache size %d, %d glyphs" % (len(data), n))
    lsb = True  # confirmed from 0x1A1D50 bit-field order
    # ASCII preview of first 8 non-blank glyphs
    shown = 0
    for i in range(n):
        rec = data[i * REC:(i + 1) * REC]
        if any(rec):
            print("=== glyph %d (0x%X) ===" % (i, i))
            print(ascii_art(rec, lsb))
            shown += 1
            if shown >= 8:
                break
    # labeled PNG sheets, 256 per sheet, 32 cols
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()
    cols = 32
    cell = W + 4 + 14  # glyph + gap + label strip
    rows = 16
    os.makedirs("sheets", exist_ok=True)
    per_sheet = cols * rows
    for s in range((n + per_sheet - 1) // per_sheet):
        sheet = Image.new("L", (cols * cell, rows * cell), 240)
        d = ImageDraw.Draw(sheet)
        for j in range(per_sheet):
            gi = s * per_sheet + j
            if gi >= n:
                break
            rec = data[gi * REC:(gi + 1) * REC]
            g = render(rec, lsb)
            cx = (j % cols) * cell
            cy = (j // cols) * cell
            sheet.paste(g, (cx + 2, cy + 12))
            d.text((cx + 1, cy), "%04X" % gi, fill=0, font=font)
        fn = "sheets/sheet_%03d.png" % s
        sheet.save(fn)
        print("wrote", fn)
    print("done. Open sheets/ and identify each glyph's character.")

if __name__ == "__main__":
    main()
