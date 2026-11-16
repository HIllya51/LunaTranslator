import re

_ARABIC_FORMS = {
    0x0621: (0xFE80,),
    0x0622: (0xFE81, 0xFE82),
    0x0623: (0xFE83, 0xFE84),
    0x0624: (0xFE85, 0xFE86),
    0x0625: (0xFE87, 0xFE88),
    0x0626: (0xFE89, 0xFE8A, 0xFE8B, 0xFE8C),
    0x0627: (0xFE8D, 0xFE8E),
    0x0628: (0xFE8F, 0xFE90, 0xFE91, 0xFE92),
    0x0629: (0xFE93, 0xFE94),
    0x062A: (0xFE95, 0xFE96, 0xFE97, 0xFE98),
    0x062B: (0xFE99, 0xFE9A, 0xFE9B, 0xFE9C),
    0x062C: (0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0),
    0x062D: (0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4),
    0x062E: (0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8),
    0x062F: (0xFEA9, 0xFEAA),
    0x0630: (0xFEAB, 0xFEAC),
    0x0631: (0xFEAD, 0xFEAE),
    0x0632: (0xFEAF, 0xFEB0),
    0x0633: (0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4),
    0x0634: (0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8),
    0x0635: (0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC),
    0x0636: (0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0),
    0x0637: (0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4),
    0x0638: (0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8),
    0x0639: (0xFEC9, 0xFECA, 0xFECB, 0xFECC),
    0x063A: (0xFECD, 0xFECE, 0xFECF, 0xFED0),
    0x0640: (0x0640, 0x0640, 0x0640, 0x0640),
    0x0641: (0xFED1, 0xFED2, 0xFED3, 0xFED4),
    0x0642: (0xFED5, 0xFED6, 0xFED7, 0xFED8),
    0x0643: (0xFED9, 0xFEDA, 0xFEDB, 0xFEDC),
    0x0644: (0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0),
    0x0645: (0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4),
    0x0646: (0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8),
    0x0647: (0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC),
    0x0648: (0xFEED, 0xFEEE),
    0x0649: (0xFEEF, 0xFEF0),
    0x064A: (0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4),
    0x067E: (0xFB56, 0xFB57, 0xFB58, 0xFB59),
    0x0686: (0xFB7A, 0xFB7B, 0xFB7C, 0xFB7D),
    0x0698: (0xFB8A, 0xFB8B),
    0x06A9: (0xFB8E, 0xFB8F, 0xFB90, 0xFB91),
    0x06AF: (0xFB92, 0xFB93, 0xFB94, 0xFB95),
    0x06CC: (0xFBFC, 0xFBFD, 0xFBFE, 0xFBFF),
}

_LAM_ALEF_LIGATURES = {
    0x0622: (0xFEF5, 0xFEF6),
    0x0623: (0xFEF7, 0xFEF8),
    0x0625: (0xFEF9, 0xFEFA),
    0x0627: (0xFEFB, 0xFEFC),
}

_BIDI_MIRROR = str.maketrans("()[]{}<>«»", ")(][}{><»«")
_LTR_RUN_RE = re.compile(
    r"(<[^>]+>|\[[^\]]+\]|\{[^\}]+\}|[A-Za-z0-9]+(?:[.,:/'-][A-Za-z0-9]+)*)"
)


def is_arabic_diacritic(code: int) -> bool:
    return (0x064B <= code <= 0x065F) or code == 0x0670 or (0x06D6 <= code <= 0x06ED)


def has_arabic(text: str) -> bool:
    return any(
        (0x0600 <= ord(c) <= 0x06FF)
        or (0x0750 <= ord(c) <= 0x077F)
        or (0x08A0 <= ord(c) <= 0x08FF)
        for c in text
    )


def shape_arabic_line(line: str) -> str:
    if not has_arabic(line):
        return line
    n = len(line)
    out = []
    prev_connects_left = False
    i = 0
    while i < n:
        ch = line[i]
        code = ord(ch)
        if is_arabic_diacritic(code):
            if out:
                out[-1] = out[-1] + ch
            else:
                out.append(ch)
            i += 1
            continue
        forms = _ARABIC_FORMS.get(code)
        if forms is None:
            out.append(ch)
            prev_connects_left = False
            i += 1
            continue
        j = i + 1
        diacritics = []
        while j < n and is_arabic_diacritic(ord(line[j])):
            diacritics.append(line[j])
            j += 1
        if code == 0x0644 and j < n and ord(line[j]) in _LAM_ALEF_LIGATURES:
            lig = _LAM_ALEF_LIGATURES[ord(line[j])]
            shaped = chr(lig[1 if prev_connects_left else 0])
            k = j + 1
            while k < n and is_arabic_diacritic(ord(line[k])):
                diacritics.append(line[k])
                k += 1
            out.append(shaped + "".join(diacritics))
            prev_connects_left = False
            i = k
            continue
        next_forms = _ARABIC_FORMS.get(ord(line[j])) if j < n else None
        next_connects_right = bool(next_forms and len(next_forms) >= 2)
        if len(forms) == 1:
            idx = 0
            prev_connects_left = False
        elif len(forms) == 2:
            idx = 1 if prev_connects_left else 0
            prev_connects_left = False
        else:
            if prev_connects_left and next_connects_right:
                idx = 3
            elif not prev_connects_left and next_connects_right:
                idx = 2
            elif prev_connects_left and not next_connects_right:
                idx = 1
            else:
                idx = 0
            prev_connects_left = next_connects_right
        out.append(chr(forms[idx]) + "".join(diacritics))
        i = j

    shaped_str = "".join(out)
    tokens = []
    for idx, part in enumerate(_LTR_RUN_RE.split(shaped_str)):
        if not part:
            continue
        if idx % 2 == 1:
            tokens.append(part)
        else:
            for c in part.translate(_BIDI_MIRROR):
                if is_arabic_diacritic(ord(c)) and tokens:
                    tokens[-1] = c + tokens[-1]
                else:
                    tokens.append(c)
    tokens.reverse()
    return "".join(tokens)
