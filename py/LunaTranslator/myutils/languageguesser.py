from collections import defaultdict
import re
from myutils.utils import cinranges


def guess(string: str):
    if not string:
        return "en"
    if string.isascii():
        return "en"
    checkers = {
        "ru": lambda c: cinranges(
            c,
            (0x0400, 0x04FF),
            (0x0500, 0x052F),
            (0x2DE0, 0x2DFF),
            (0xA640, 0xA69F),
            (0x1C80, 0x1C8F),
            (0x1C90, 0x1CBF),
            (0x1D2C, 0x1D5F),
            (0x1D780, 0x1D7AF),
        ),
        "ko": lambda c: cinranges(
            c,
            (0x1100, 0x11FF),
            (0x3130, 0x318F),
            (0xAC00, 0xD7AF),
            (0xA960, 0xA97F),
            (0xD7B0, 0xD7FF),
        ),
        "ja": {
            lambda c: cinranges(
                c,
                (0x3040, 0x309F),
                (0x30A0, 0x30FF),
                (0xFF65, 0xFF9F),
                (0x31F0, 0x31FF),
                (0x3100, 0x312F),
                (0x31A0, 0x31BF),
                (0x3000, 0x303F),
            ): 20,
            lambda c: cinranges(
                c,
                (0x4E00, 0x9FA5),
            ): 4,
        },
        "zh": {
            lambda c: cinranges(
                c,
                (0x4E00, 0x9FA5),
            ): 5
        },
        "ar": lambda c: cinranges(
            c,
            (0x0600, 0x06FF),
            (0x0750, 0x077F),
            (0x08A0, 0x08FF),
            (0x0870, 0x089F),
            (0x1EE00, 0x1EEFF),
            (0x0600, 0x0603),
            (0x060C, 0x061F),
            (0x0660, 0x0669),
            (0x06F0, 0x06F9),
        ),
        "en": {
            lambda c: cinranges(
                c,
                (0x0000, 0x00FF),
            ): 0.2
        },
    }
    string = re.sub(r"ZX\wZ", "", string)
    cnt = defaultdict(int)
    for c in string.strip():
        for lang, ck in checkers.items():
            if isinstance(ck, dict):
                for f, w in ck.items():
                    if f(c):
                        cnt[lang] += w
            else:
                if ck(c):
                    cnt[lang] += 1
    if not cnt:
        return "en"

    max_key = max(cnt, key=cnt.get)
    return max_key
