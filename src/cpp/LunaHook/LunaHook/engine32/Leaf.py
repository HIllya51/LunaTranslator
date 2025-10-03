import numpy as np
import cv2, base64


def bytes_to_bitmap(data: bytes, fg=255, bg=0):
    img = np.full((24, 24), bg, dtype=np.uint8)

    for block in range(3):
        base = block * 24
        for row in range(24):
            val = data[base + row]
            for bit in range(8):
                if (val & 0x80) != 0:
                    col = block * 8 + bit
                    img[row, col] = fg
                val = (val << 1) & 0xFF
    return img


with open(
    r".\1.bin",
    "rb",
) as ff:
    bs = ff.read()

markdown = ""
for i in range(0x1000):

    bitmap = bytes_to_bitmap(bs[i * 72 : i * 72 + 72])

    img = cv2.resize(bitmap, (120, 120), interpolation=cv2.INTER_NEAREST)

    _, buffer = cv2.imencode(".png", img)

    img_base64 = base64.b64encode(buffer).decode("utf-8")

    markdown += hex(i) + "\n\n"
    markdown += f"![img](data:image/png;base64,{img_base64})\n\n"

with open("Leaf.md", "w") as ff:
    ff.write(markdown)
