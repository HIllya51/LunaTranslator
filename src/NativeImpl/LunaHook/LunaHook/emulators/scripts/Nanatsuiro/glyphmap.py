#!/usr/bin/env python3
# Nanatsuiro Drops Pure!! (SLPS-25758) glyph sheet renderer.
# Font cache: eeMemory.bin @ [0x27d8a8] (guest va = file offset).
#   24x24 4bpp, stride 288, 3476 glyphs (0..0xdb3).
# Pixel order (rasterizer 0x1c4290): linear row-major, 12 bytes/row;
#   per byte lo-nibble=LEFT px, hi-nibble=RIGHT px. Grayscale 0=white..5=black.
# Anchors: 0=space 1=、 2=。 3=ー 5=・.
import struct, os
from PIL import Image, ImageDraw, ImageFont

HERE    = os.path.dirname(os.path.abspath(__file__))
EE      = os.path.join(os.path.dirname(HERE), "savestate", "eeMemory.bin")
NGLYPH, STRIDE, CELL = 3476, 288, 24
COLS, RPS, SCALE = 16, 16, 6
LABEL_H, CELLPX = 22, CELL * SCALE + 6

ee = open(EE, "rb").read()
base = struct.unpack_from("<I", ee, 0x27d8a8)[0]
font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)
outdir = os.path.join(HERE, "sheets")
os.makedirs(outdir, exist_ok=True)

for sheet in range((NGLYPH + RPS * COLS - 1) // (RPS * COLS)):
    si = Image.new("RGB", (COLS * CELLPX, RPS * (CELLPX + LABEL_H)), (255, 255, 255))
    d = ImageDraw.Draw(si)
    bi = sheet * RPS * COLS
    d.text((2, 2), f"sheet {sheet}  0x{bi:x}..", (0, 0, 200), font=font)
    for i in range(RPS * COLS):
        idx = bi + i
        if idx >= NGLYPH:
            break
        col, row = i % COLS, i // COLS
        x, y = col * CELLPX, row * (CELLPX + LABEL_H) + LABEL_H
        g = Image.new("L", (CELL, CELL), 255)
        gp = g.load()
        off = base + idx * STRIDE
        for r in range(CELL):
            for c in range(CELL // 2):
                b = ee[off + r * 12 + c]
                v0, v1 = b & 0xF, b >> 4
                if v0:
                    gp[c * 2, r] = 255 - int(v0 / 5 * 255)
                if v1:
                    gp[c * 2 + 1, r] = 255 - int(v1 / 5 * 255)
        si.paste(g.resize((CELL * SCALE, CELL * SCALE), Image.NEAREST), (x + 3, y + 3))
        d.text((x + 2, y - LABEL_H + 2), f"0x{idx:03x}", (0, 0, 180), font=font)
    si.save(os.path.join(outdir, f"sheet_{sheet:02d}.png"))
print(f"rendered {NGLYPH} glyphs -> {outdir}/sheet_00..{sheet:02d}.png")
