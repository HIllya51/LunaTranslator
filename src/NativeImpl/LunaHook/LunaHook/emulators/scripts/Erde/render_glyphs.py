import struct, numpy as np
from PIL import Image
import erde_font as F
import os

os.makedirs('sheets', exist_ok=True)

def glyph_img(g, scale=4):
    dec = F.melt8Ex(F.SD[F.DESC+F.OFFS[g]+1:], 0x120)  # 288 bytes, 24x24 4bpp
    arr = np.zeros((24,24), dtype=np.uint8)
    for y in range(24):
        for x in range(24):
            b = dec[y*12 + (x//2)]
            nib = (b >> (4 if x%2==0 else 0)) & 0xf
            arr[y,x] = nib * 17
    img = Image.fromarray(arr, 'L').resize((24*scale,24*scale), Image.NEAREST)
    return img

# render sheets of 16x16 = 256 glyphs, labeled, at 4x (cell 96+label)
COLS, ROWS = 16, 16
SCALE = 4
CELLW = 24*SCALE + 8
CELLH = 24*SCALE + 18
for sheet in range(8):
    base = sheet * 256
    if base >= F.COUNT: break
    sheetimg = Image.new('L', (COLS*CELLW, ROWS*CELLH), 255)
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheetimg)
    for i in range(256):
        g = base + i
        if g >= F.COUNT: break
        gi = glyph_img(g, SCALE)
        cx = (i % COLS) * CELLW + 4
        cy = (i // COLS) * CELLH
        # paste inverted (black on white)
        inv = Image.eval(gi, lambda v: 255-v)
        sheetimg.paste(inv, (cx, cy))
        d.text((cx, cy + 24*SCALE + 1), str(g), fill=0)
    sheetimg.save(f'sheets/sheet_{sheet:02d}.png')
    print(f'sheet {sheet}: glyphs {base}-{base+255} -> sheets/sheet_{sheet:02d}.png')
print('done')
