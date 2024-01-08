import enum
from typing import Dict, List, Tuple


class Configurations:

    data_path = ('./files/data')
    jisyo_hepburn_hira = "hepburnhira3.db"
    jisyo_passport_hira = "passporthira3.db"
    jisyo_kunrei_hira = "kunreihira3.db"
    jisyo_itaiji = "itaijidict4.db"
    jisyo_kanwa = "kanwadict4.db"
    jisyo_hepburn = "hepburndict3.db"
    jisyo_passport = "passportdict3.db"
    jisyo_kunrei = "kunreidict3.db"
    jisyo_halfkana = "halfkana3.db"

    def dictpath(self, dbfile: str):
        return os.path.join(self.data_path, dbfile)


Configurations = Configurations()

class H2:

    _kanadict = None

    _diff = 0x30A1 - 0x3041  # KATAKANA LETTER A - HIRAGANA A
    _ediff = 0x1B164 - 0x1B150

    def __init__(self, mode, method="Hepburn"):
        if mode == "a":
            if method == "Passport":
                self._kanadict = Jisyo(Configurations.jisyo_passport_hira)
            elif method == "Kunrei":
                self._kanadict = Jisyo(Configurations.jisyo_kunrei_hira)
            else:
                self._kanadict = Jisyo(Configurations.jisyo_hepburn_hira)

            self.convert = self.convert_a
        elif mode == "K":
            self.convert = self.convert_K
        else:
            self.convert = self.convert_noop

    @classmethod
    def isRegion(cls, char):
        return 0x3040 < ord(char[0]) < 0x3097 or 0x1B150 <= ord(char[0]) <= 0x1B152

    def convert_a(self, text):
        Hstr = ""
        max_len = -1
        r = min(self._kanadict.maxkeylen(), len(text))
        for x in range(1, r + 1):
            if self._kanadict.haskey(text[:x]):
                if max_len < x:
                    max_len = x
                    Hstr = self._kanadict.lookup(text[:x])
        return (Hstr, max_len)

    def convert_K(self, text):
        Hstr = ""
        max_len = 0
        r = len(text)
        for x in range(r):
            if 0x3040 < ord(text[x]) < 0x3097:
                Hstr = Hstr + chr(ord(text[x]) + self._diff)
                max_len += 1
            elif 0x1B150 <= ord(text[x]) <= 0x1B152:
                Hstr = Hstr + chr(ord(text[x]) + self._ediff)
                max_len += 1
            else:  # pragma: no cover
                break
        return (Hstr, max_len)

    def convert_noop(self, text):
        return (text[0], 1)


class K2:

    _kanadict = None
    _halfkanadict = None

    _diff = 0x30A1 - 0x3041  # KATAKANA LETTER A - HIRAGANA A
    _ediff = 0x1B164 - 0x1B150

    def __init__(self, mode, method="Hepburn"):
        self._halfkanadict = Jisyo(Configurations.jisyo_halfkana)
        if mode == "a":
            if method == "Passport":
                self._kanadict = Jisyo(Configurations.jisyo_passport)
            elif method == "Kunrei":
                self._kanadict = Jisyo(Configurations.jisyo_kunrei)
            else:
                self._kanadict = Jisyo(Configurations.jisyo_hepburn)

            self.convert = self.convert_a
        elif mode == "H":
            self.convert = self.convert_h
        else:
            self.convert = self.convert_noop

    @classmethod
    def isRegion(cls, char):
        ch = ord(char[0])
        return (
            cls._is_katakana(ch)
            or cls._is_half_width_kana(ch)
            or 0x1B164 <= ch <= 0x1B167
        )

    @classmethod
    def _is_katakana(cls, ch):
        return 0x30A0 < ch < 0x30FD

    @classmethod
    def _is_half_width_kana(cls, ch):
        return 0xFF65 < ch < 0xFF9F

    def _convert_half_kana(self, text):
        Hstr = ""
        max_len = -1
        for x in [2, 1]:
            if self._halfkanadict.haskey(text[:x]):
                max_len = x
                Hstr = self._halfkanadict.lookup(text[:x])
                break
        return Hstr, max_len

    def convert_a(self, text):
        Hstr = ""
        max_len = -1
        r = min(self._kanadict.maxkeylen(), len(text))
        for x in range(1, r + 1):
            if self._kanadict.haskey(text[:x]):
                if max_len < x:
                    max_len = x
                    Hstr = self._kanadict.lookup(text[:x])
        return Hstr, max_len

    def convert_h(self, text):
        Hstr = ""
        max_len = 0
        r = len(text)
        x = 0
        while x < r:
            if 0x1B164 <= ord(text[x]) < 0x1B167:
                Hstr = Hstr + chr(ord(text[x]) - self._ediff)
                max_len += 1
                x += 1
            elif ord(text[x]) == 0x1B167:
                Hstr = Hstr + "\u3093"
                max_len += 1
                x += 1
            elif 0x30A0 < ord(text[x]) < 0x30F7:
                Hstr = Hstr + chr(ord(text[x]) - self._diff)
                max_len += 1
                x += 1
            elif 0x30F7 <= ord(text[x]) < 0x30FD:
                Hstr = Hstr + text[x]
                max_len += 1
                x += 1
            elif self._is_half_width_kana(ord(text[x])):
                kstr, length = self._convert_half_kana(text[x:])
                if length > 0:
                    max_len += length
                    x += length
                    if ord(kstr) == 0x309B:
                        Hstr = Hstr + kstr
                    else:
                        Hstr = Hstr + chr(ord(kstr) - self._diff)
                else:
                    max_len += 1
                    x += 1  # skip unknown character(issue #115)
            else:  # pragma: no cover
                break
        return (Hstr, max_len)

    def convert_noop(self, text):
        return text[0], 1


class Jisyo:
    _dict = None

    def __init__(self, dictname):
        src = Configurations.dictpath(dictname)
        with open(src, "rb") as d:
            self._dict = pickle.load(d)

    def haskey(self, key):
        return key in self._dict

    def lookup(self, key):
        return self._dict[key]

    def maxkeylen(self):
        return self._dict["_max_key_len_"]


class Sym2:
    def __init__(self, mode):
        if mode == "a":
            self.convert = self.convert_a
        else:
            self.convert = self.convert_noop

    @classmethod
    def isRegion(cls, char: str):
        c = ord(char[0])
        return (
            (Ch.ideographic_space <= c <= Ch.postal_mark_face)
            or (Ch.wavy_dash <= c <= Ch.ideographic_half_fill_space)
            or (Ch.greece_Alpha <= c <= Ch.greece_Rho)
            or (Ch.greece_Sigma <= c <= Ch.greece_Omega)
            or (Ch.greece_alpha <= c <= Ch.greece_omega)
            or (Ch.cyrillic_A <= c <= Ch.cyrillic_ya)
            or (Ch.zenkaku_exc_mark <= c <= Ch.zenkaku_number_nine)
            or (0xFF20 <= c <= 0xFF5E)
            or c == 0x0451
            or c == 0x0401
        )

    def _convert(self, text):
        c = ord(text[0])
        if Ch.ideographic_space <= c <= Ch.postal_mark_face:
            return Convert_Tables.symbol_table_1[c - Ch.ideographic_space]
        elif Ch.wavy_dash <= c <= Ch.ideographic_half_fill_space:
            return Convert_Tables.symbol_table_2[c - Ch.wavy_dash]
        elif Ch.greece_Alpha <= c <= Ch.greece_Omega:
            return Convert_Tables.symbol_table_3[c - Ch.greece_Alpha]
        elif Ch.greece_alpha <= c <= Ch.greece_omega:
            return Convert_Tables.symbol_table_4[c - Ch.greece_alpha]
        elif Ch.cyrillic_A <= c <= Ch.cyrillic_ya:
            return Convert_Tables.cyrillic_table[text[0]]
        elif c == Ch.cyrillic_E or c == Ch.cyrillic_e:
            return Convert_Tables.cyrillic_table[text[0]]
        elif Ch.zenkaku_exc_mark <= c <= Ch.zenkaku_slash_mark:
            return Convert_Tables.symbol_table_5[c - Ch.zenkaku_exc_mark]
        elif Ch.zenkaku_number_zero <= c <= Ch.zenkaku_number_nine:
            return chr(c - Ch.zenkaku_number_zero + ord("0"))
        elif 0xFF20 <= c <= 0xFF40:
            return chr(0x0041 + c - 0xFF21)  # u\ff21Ａ => u\0041:@A..Z[\]^_`
        elif 0xFF41 <= c < 0xFF5F:
            return chr(0x0061 + c - 0xFF41)  # u\ff41ａ => u\0061:a..z{|}
        else:
            return ""  # pragma: no cover

    def convert_a(self, text):
        t = self._convert(text)
        if t is not None and len(t) > 0:
            return t, 1
        else:
            return "", 0

    def convert_noop(self, text):
        return text[0], 1
class A2:
    def __init__(self, mode):
        if mode == "E":
            self.convert = self.convert_E
        else:
            self.convert = self.convert_noop

    @classmethod
    def isRegion(cls, char):
        return Ch.space <= ord(char[0]) < Ch.delete

    def _convert(self, text):
        c = ord(text[0])
        if Ch.space <= c <= Ch.at_mark:
            return Convert_Tables.alpha_table_1[(c - Ch.space)]
        elif Ch.alphabet_A <= c <= Ch.alphabet_Z:
            return chr(Ch.zenkaku_A + c - Ch.alphabet_A)  # u\0041A => u\ff21Ａ
        elif Ch.square_bra <= c <= Ch.back_quote:
            return Convert_Tables.alpha_table_2[(c - Ch.square_bra)]
        elif Ch.alphabet_a <= c <= Ch.alphabet_z:
            return chr(Ch.zenkaku_a + c - Ch.alphabet_a)  # u\0061a => u\ff41ａ
        elif Ch.bracket_bra <= c <= Ch.tilda:
            return Convert_Tables.alpha_table_3[(c - Ch.bracket_bra)]
        else:
            return ""  # pragma: no cover

    def convert_E(self, text):
        t = self._convert(text)
        if len(t):
            return t, 1
        else:
            return "", 0

    def convert_noop(self, text):
        return text[0], 1

class Ch:
    space = 0x20
    at_mark = 0x40
    alphabet_A = 0x41
    alphabet_Z = 0x5A
    square_bra = 0x5B
    back_quote = 0x60
    alphabet_a = 0x61
    alphabet_z = 0x7A
    bracket_bra = 0x7B
    tilda = 0x7E
    delete = 0x7F
    ideographic_space = 0x3000
    postal_mark_face = 0x3020
    wavy_dash = 0x3030
    ideographic_half_fill_space = 0x303F
    greece_Alpha = 0x0391
    greece_Rho = 0x30A1
    greece_Sigma = 0x30A3
    greece_Omega = 0x03A9
    greece_alpha = 0x03B1
    greece_omega = 0x03C9
    cyrillic_A = 0x0410
    cyrillic_E = 0x0401
    cyrillic_e = 0x0451
    cyrillic_ya = 0x044F
    zenkaku_exc_mark = 0xFF01
    zenkaku_slash_mark = 0xFF0F
    zenkaku_number_zero = 0xFF10
    zenkaku_number_nine = 0xFF1A
    zenkaku_A = 0xFF21
    zenkaku_a = 0xFF41
    endmark = ")]!,.,\u3001\u3002\uff1f\uff10\uff1e\uff1c"
    long_symbols = "\u30FC\u2015\u2212\uFF70"  # "ー  ―  −  ｰ "
    # _UNCHECKED_LONG_SYMBOLS: str = "\u002D\u2010\u2011\u2013\u2014" # "-  ‐ ‑ – —"


Ch = Ch()
   


class PyKakasiException(Exception):
    pass


class UnknownCharacterException(PyKakasiException):
    pass


class _TYPE(enum.Enum):
    KANJI = 1
    KANA = 2
    HIRAGANA = 3
    SYMBOL = 4
    ALPHA = 5


import functools
import pickle
import threading
from typing import Tuple
 

class JConv:
    def __init__(self):
        self._kanwa = Kanwa()
        self._itaiji = Itaiji()

    def isRegion(self, c: str):
        return 0x3400 <= ord(c[0]) < 0xE000 or self._itaiji.haskey(ord(c[0]))

    @functools.lru_cache(maxsize=512)
    def convert(self, itext: str) -> Tuple[str, int]:
        max_len = 0
        Hstr = ""
        text = self._itaiji.convert(itext)
        num_vs = len(itext) - len(text)
        table = self._kanwa.load(text[0])
        if table is None:
            return "", 0
        for (k, v) in table.items():
            length = len(k)
            if len(text) >= length:
                if text.startswith(k):
                    for yomi in v:
                        if max_len < length:
                            Hstr = yomi
                            max_len = length
        for _ in range(
            num_vs
        ):  # when converting string with kanji wit variation selector, calculate max_len again
            if max_len > len(itext):
                break
            elif text[max_len - 1] != itext[max_len - 1]:
                max_len += 1
            elif (
                max_len < num_vs + len(text)
                and max_len <= len(itext)
                and self._is_vschr(itext[max_len])
            ):
                max_len += 1
            else:
                pass
        return (Hstr, max_len)

    def _isCletter(self, literal: str, c: str) -> bool:
        if (0x3041 <= ord(c) <= 0x309F) and (
            literal in self._cl_table[ord(c) - 0x3040]
        ):  # ぁ:= u\3041
            return True
        return False

    def _is_vschr(self, ch):
        return 0x0E0100 <= ord(ch) <= 0x0E1EF or 0xFE00 <= ord(ch) <= 0xFE02


class Itaiji:

    # this class is Borg/Singleton
    _shared_state = {"_itaijidict": None, "_lock": threading.Lock()}

    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._shared_state
        return self

    def __init__(self):
        if self._itaijidict is None:
            with self._lock:
                if self._itaijidict is None:
                    itaijipath = Configurations.dictpath(Configurations.jisyo_itaiji)
                    with open(itaijipath, "rb") as d:
                        self._itaijidict = pickle.load(d)

    def haskey(self, c):
        return c in self._itaijidict

    def convert(self, text: str) -> str:
        return text.translate(self._itaijidict)


# This class is Borg/Singleton
# It provides same results becase lookup from a static dictionary.
# There is no state rather dictionary dbm.
class Kanwa:
    _shared_state = {"_lock": threading.Lock(), "_jisyo_table": None}

    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._shared_state
        return self

    def __init__(self):
        if self._jisyo_table is None:
            with self._lock:
                if self._jisyo_table is None:
                    dictpath = Configurations.dictpath(Configurations.jisyo_kanwa)
                    with open(dictpath, "rb") as d:
                        self._jisyo_table = pickle.load(d)

    def load(self, char: str):
        key = ord(char[0])
        return self._jisyo_table.get(key, None)
from typing import Dict, List, Optional, Tuple, Union
 
  

class UnsupportedRomanRulesException(PyKakasiException):
    pass


class UnknownOptionsException(PyKakasiException):
    pass


class InvalidModeValueException(PyKakasiException):
    pass


class InvalidFlagValueException(PyKakasiException):
    pass



class J2:
    def __init__(self, mode: str = "H", method: str = "Hepburn"):
        self._itaiji = Itaiji()
        self._jconv = JConv()
        if mode == "H":
            self.convert = self.convert_h
        elif mode in ("a", "K"):
            self._hconv = H2(mode, method)
            self.convert = self.convert_nonh
        else:
            self.convert = self.convert_noop

    def isRegion(self, c: str):
        return 0x3400 <= ord(c[0]) < 0xE000 or self._itaiji.haskey(ord(c[0]))

    def convert_h(self, itext) -> Tuple[str, int]:
        return self._jconv.convert(itext)

    def convert_nonh(self, text):
        if not self.isRegion(text[0]):
            return "", 0

        (t, l1) = self.convert_h(text)
        if l1 <= 0:  # pragma: no cover
            return "", 0

        m = 0
        otext = ""

        while True:
            if m >= len(t):
                break
            (s, n) = self._hconv.convert(t[m:])
            if n <= 0:  # pragma: no cover
                m = m + 1
            else:
                m = m + n
                otext = otext + s

        return otext, l1

    def convert_noop(self, text):
        return text[0], 1
# -*- coding: utf-8 -*-
#  properties.py
#
# Copyright 2019 Hiroshi Miura <miurahr@linux.com>

import os
 




class Convert_Tables:
    """
    convert symbols to alphabet
    based on Original KAKASI's EUC_JP - alphabet converter table
    --------------------------------------------------------------------------
     a1 a0 | 　 、 。 ， ． ・ ： ； ？ ！ ゛ ゜ ´ ｀ ¨
             " ",",",".",",",".",".",":",";","?",
             "!","\"","(maru)","'","`","..",
     a1 b0 | ＾ ￣ ＿ ヽ ヾ ゝ ゞ 〃 仝 々 〆 〇 ー ― ‐ ／
           "~","~","_","(kurikaesi)","(kurikaesi)","(kurikaesi)",
           "(kurikaesi)","(kurikaesi)","(kurikaesi)","(kurikaesi)",
           "sime","(maru)","^","-","-","/",
     a1 c0 | ＼ ～ ∥ ｜ … ‥ ‘ ’ “ ” （ ） 〔 〕 ［ ］
          "\\","~","||","|","...","..","`","'","\"","\"","(",")","[","]","[","]",
          "{","}","<",">","<<",">>","(",")","(",")","(",")","+","-","+-","X",
     a1 d0 | ｛ ｝ 〈 〉 《 》 「 」 『 』 【 】 ＋ － ± ×

     a1 e0 | ÷ ＝ ≠ ＜ ＞ ≦ ≧ ∞ ∴ ♂ ♀ ° ′ ″ ℃ ￥
          "/","=","!=","<",">","<=",">=","(kigou)","...",
          "(osu)","(mesu)","(do)","'","\"","(Sessi)","\\",
     a1 f0 | ＄ ￠ ￡ ％ ＃ ＆ ＊ ＠ § ☆ ★ ○ ● ◎ ◇
          "$","(cent)","(pound)","%","#","&","*","@",
          "(setu)","(hosi)","(hosi)","(maru)","(maru)","(maru)","(diamond)"
    ---------------------------------------------------------------------------

    ----------------------------------------------------------
     a2 a0 | ◆ □ ■ △ ▲ ▽ ▼ ※ 〒 → ← ↑ ↓ 〓
     a2 b0 | ∈ ∋ ⊆ ⊇ ⊂ ⊃ a2 c0 | ∪ ∩ ∧ ∨ ￢ ⇒ ⇔ ∀
     a2 d0 | ∃ ∠ ⊥ ⌒ ∂
     a2 e0 | ∇ ≡ ≒ ≪ ≫ √ ∽ ∝ ∵ ∫ ∬
     a2 f0 | Å ‰ ♯ ♭ ♪ † ‡ ¶ ◯
    ----------------------------------------------------------

    Greek convertion table
    ----------------------------------------------------------
       "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
       "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
       "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
       "", "", "", "", "", "", "", "",
       "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
       "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", "rho",
       "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"
    ----------------------------------------------------------
    """

    # U3000 - 301F
    # \u3000、。〃〄〇〆々〈〉《》「」『』【】〒〓〔〕〖〗〘〙
    # 〚〛〜〝〞〟〠
    symbol_table_1 = [
        " ",
        ",",
        ".",
        '"',
        "(kigou)",
        "(kurikaesi)",
        "(sime)",
        "(maru)",
        "<",
        ">",
        "<<",
        ">>",
        "(",
        ")",
        "(",
        ")",
        "(",
        ")",
        "(kigou)",
        "(geta)",
        "(",
        ")",
        "(",
        ")",
        "(",
        ")",
        "(",
        ")",
        "~",
        "(kigou)",
        '"',
        "(kigou)",
        "(kigou)",
    ]
    # U3030 - 3040
    # 〰〱〲〳〴〵〶〷〼〽〾〿
    symbol_table_2 = [
        "-",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kurikaesi)",
        "(kigou)",
        "XX",
        None,
        None,
        None,
        None,
        "(masu)",
        "(kurikaesi)",
        " ",
        " ",
    ]
    # U0391-03A9
    symbol_table_3 = [
        "Alpha",
        "Beta",
        "Gamma",
        "Delta",
        "Epsilon",
        "Zeta",
        "Eta",
        "Theta",
        "Iota",
        "Kappa",
        "Lambda",
        "Mu",
        "Nu",
        "Xi",
        "Omicron",
        "Pi",
        "Rho",
        None,
        "Sigma",
        "Tau",
        "Upsilon",
        "Phi",
        "Chi",
        "Psi",
        "Omega",
    ]
    # U03B1-03C9
    symbol_table_4 = [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "omicron",
        "pi",
        "rho",
        "final sigma",
        "sigma",
        "tau",
        "upsilon",
        "phi",
        "chi",
        "psi",
        "omega",
    ]
    # UFF01-FF0F
    symbol_table_5 = [
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
    ]
    # cyriilic
    cyrillic_table = {  # basic cyrillic characters
        "\u0410": "A",
        "\u0411": "B",
        "\u0412": "V",  # АБВ
        "\u0413": "G",
        "\u0414": "D",
        "\u0415": "E",  # ГДЕ
        "\u0401": "E",
        "\u0416": "Zh",
        "\u0417": "Z",  # ЁЖЗ
        "\u0418": "I",
        "\u0419": "Y",
        "\u041a": "K",  # ИЙК
        "\u041b": "L",
        "\u041c": "M",
        "\u041d": "N",  # ЛМН
        "\u041e": "O",
        "\u041f": "P",
        "\u0420": "R",  # ОПР
        "\u0421": "S",
        "\u0422": "T",
        "\u0423": "U",  # СТУ
        "\u0424": "F",
        "\u0425": "H",
        "\u0426": "Ts",  # ФХЦ
        "\u0427": "Ch",
        "\u0428": "Sh",
        "\u0429": "Sch",  # ЧШЩ
        "\u042a": "",
        "\u042b": "Y",
        "\u042c": "",  # ЪЫЬ
        "\u042d": "E",
        "\u042e": "Yu",
        "\u042f": "Ya",  # ЭЮЯ
        "\u0430": "a",
        "\u0431": "b",
        "\u0432": "v",  # абв
        "\u0433": "g",
        "\u0434": "d",
        "\u0435": "e",  # где
        "\u0451": "e",
        "\u0436": "zh",
        "\u0437": "z",  # ёжз
        "\u0438": "i",
        "\u0439": "y",
        "\u043a": "k",  # ийк
        "\u043b": "l",
        "\u043c": "m",
        "\u043d": "n",  # лмн
        "\u043e": "o",
        "\u043f": "p",
        "\u0440": "r",  # опр
        "\u0441": "s",
        "\u0442": "t",
        "\u0443": "u",  # сту
        "\u0444": "f",
        "\u0445": "h",
        "\u0446": "ts",  # фхц
        "\u0447": "ch",
        "\u0448": "sh",
        "\u0449": "sch",  # чшщ
        "\u044a": "",
        "\u044b": "y",
        "\u044c": "",  # ъыь
        "\u044d": "e",
        "\u044e": "yu",
        "\u044f": "ya",  # эюя
    }

    alpha_table_1 = [
        "\u3000",
        "\uff01",
        "\uff02",
        "\uff03",
        "\uff04",
        "\uff05",
        "\uff06",
        "\uff07",
        "\uff08",
        "\uff09",
        "\uff0a",
        "\uff0b",
        "\uff0c",
        "\uff0d",
        "\uff0e",
        "\uff0f",  # ！＂＃＄％＆＇（）＊＋，－．／
        "\uff10",
        "\uff11",
        "\uff12",
        "\uff13",
        "\uff14",
        "\uff15",
        "\uff16",
        "\uff17",
        "\uff18",
        "\uff19",  # ０...９
        "\uff1a",
        "\uff1b",
        "\uff1c",
        "\uff1d",
        "\uff1e",
        "\uff1f",
        "\uff20",
    ]  # ：；＜＝＞？＠
    alpha_table_2 = [
        "\uff3b",
        "\uff3c",
        "\uff3d",
        "\uff3e",
        "\uff3f",
        "\uff40",
    ]  # ［＼］＾＿｀
    alpha_table_3 = ["\uff5b", "\uff5c", "\uff5d", "\uff5e"]  # ｛｜｝～


Convert_Tables = Convert_Tables()
# -*- coding: utf-8 -*-
# scripts.py
#
# Copyright 2011-2019 Hiroshi Miura <miurahr@linux.com>
import functools
import pickle
from typing import Dict
 

class IConv:

    _MAXLEN: int = 32

    def __init__(self):
        self._hahconv = H2("a", method="Hepburn")
        self._hakconv = H2("a", method="Kunrei")
        self._hapconv = H2("a", method="Passport")
        self._hkconv = H2("K")
        self._khconv = K2("H")
        self._saconv = Sym2("a")

    @functools.lru_cache(maxsize=256)
    def convert(self, otext: str, hira: str) -> Dict[str, str]:
        kana = self._h2k(hira)
        hira = self._k2h(hira)  # make sure hiragana doesn't contain katakana
        tmp = {
            "orig": otext,
            "hira": hira,
            "kana": kana,
            "hepburn": self._s2a(self._h2ah(hira)),
            "kunrei": self._s2a(self._h2ak(hira)),
            "passport": self._s2a(self._h2ap(hira)),
        }
        return tmp

    def _s2a(self, text: str) -> str:
        result = ""  # type: str
        i = 0
        length = len(text)
        while i < length:
            w = min(i + self._MAXLEN, length)  # type: int
            (t, l1) = self._saconv.convert(text[i:w])
            if l1 > 0:
                result += t
                i += l1
            elif text[i] in Ch.long_symbols:  # handle chōonpu sound marks
                # use previous char as a transliteration for kana-dash
                if len(result) > 0:
                    result += result[-1]
                else:
                    result += "-"
                i += 1
            else:
                result += text[i : i + 1]
                i += 1
        return result

    def _k2h(self, text: str) -> str:
        result = ""
        i = 0
        while i < len(text):
            w = min(i + self._MAXLEN, len(text))
            (t, l1) = self._khconv.convert(text[i:w])
            if l1 > 0:
                result += t
                i += l1
            else:
                result += text[i : i + 1]
                i += 1
        return result

    def _h2k(self, text: str) -> str:
        result = ""
        i = 0
        while i < len(text):
            w = min(i + self._MAXLEN, len(text))
            (t, l1) = self._hkconv.convert(text[i:w])
            if l1 > 0:
                result += t
                i += l1
            else:
                result += text[i : i + 1]
                i += 1
        return result

    def _h2ak(self, text: str) -> str:
        result = ""
        i = 0
        while i < len(text):
            w = min(i + self._MAXLEN, len(text))
            (t, l1) = self._hakconv.convert(text[i:w])
            if l1 > 0:
                result += t
                i += l1
            else:
                result += text[i : i + 1]
                i += 1
        return result

    def _h2ah(self, text: str) -> str:
        result = ""
        i = 0
        while i < len(text):
            w = min(i + self._MAXLEN, len(text))
            (t, l1) = self._hahconv.convert(text[i:w])
            if l1 > 0:
                result += t
                i += l1
            else:
                result += text[i : i + 1]
                i += 1
        return result

    def _h2ap(self, text: str) -> str:
        result = ""
        i = 0
        while i < len(text):
            w = min(i + self._MAXLEN, len(text))
            (t, l1) = self._hapconv.convert(text[i:w])
            if l1 > 0:
                result += t
                i += l1
            else:
                result += text[i : i + 1]
                i += 1
        return result




class Kakasi:
    """Kakasi is a conversion class for Japanese text."""

    def __init__(self):
        self._jconv = JConv()
        self._iconv = IConv()
 

    def convert(self, text: str) -> List[Dict[str, str]]:
        """Convert input text to dictionary contains KANA, HIRA and romaji results."""

        if len(text) == 0:
            return [
                {
                    "orig": "",
                    "kana": "",
                    "hira": "",
                    "hepburn": "",
                    "passport": "",
                    "kunrei": "",
                }
            ]

        original_text = ""
        kana_text = ""
        _result = []
        i = 0
        prev_type = _TYPE.KANJI
        output_flag: Tuple[bool, bool, bool] = (False, False, False)

        while i < len(text):
            # output_flag
            # means (output buffer?, output text[i]?, copy and increment i?)
            # possible (False, True, True), (True, False, False), (True, True, True)
            #          (False, False, True)
            if text[i] in Ch.endmark:
                prev_type = _TYPE.SYMBOL
                output_flag = (True, True, True)
            elif text[i] in Ch.long_symbols:
                # FIXME: special case
                output_flag = (False, False, True)
            elif Sym2.isRegion(text[i]):
                if prev_type != _TYPE.SYMBOL:
                    output_flag = (True, False, True)
                else:
                    output_flag = (False, True, True)
                prev_type = _TYPE.SYMBOL
            elif K2.isRegion(text[i]):
                output_flag = (prev_type != _TYPE.KANA, False, True)
                prev_type = _TYPE.KANA
            elif H2.isRegion(text[i]):
                output_flag = (prev_type != _TYPE.HIRAGANA, False, True)
                prev_type = _TYPE.HIRAGANA
            elif A2.isRegion(text[i]):
                output_flag = (prev_type != _TYPE.ALPHA, False, True)
                prev_type = _TYPE.ALPHA
            elif self._jconv.isRegion(text[i]):
                if len(original_text) > 0:
                    _result.append(self._iconv.convert(original_text, kana_text))
                t, ln = self._jconv.convert(text[i:])
                prev_type = _TYPE.KANJI
                if ln > 0:
                    original_text = text[i : i + ln]
                    kana_text = t
                    i += ln
                    output_flag = (False, False, False)
                else:  # unknown kanji
                    original_text = text[i]
                    kana_text = ""
                    i += 1
                    output_flag = (True, False, False)
            else:
                if len(original_text) > 0:
                    _result.append(self._iconv.convert(original_text, kana_text))
                _result.append(self._iconv.convert(text[i], ""))
                i += 1
                output_flag = (False, False, False)

            # Convert to kana and Output based on flag
            if output_flag[0] and output_flag[1]:
                original_text += text[i]
                kana_text += text[i]
                _result.append(self._iconv.convert(original_text, kana_text))
                original_text = ""
                kana_text = ""
                i += 1
            elif output_flag[0] and output_flag[2]:
                if len(original_text) > 0:
                    _result.append(self._iconv.convert(original_text, kana_text))
                original_text = text[i]
                kana_text = text[i]
                i += 1
            elif output_flag[2]:
                original_text += text[i]
                kana_text += text[i]
                i += 1
            else:
                pass

        # last word
        if len(original_text) > 0:
            _result.append(self._iconv.convert(original_text, kana_text))

        return _result
    

class kakasi:

    _keys: List[str] = ["J", "H", "K", "E", "a"]
    _values: List[str] = ["a", "E", "H", "K"]
    _roman_vals: List[str] = ["Hepburn", "Kunrei", "Passport"]

    def __init__(self):
        self._kakasi = Kakasi()
        # for v1 api
        self._conv = {}  # type: Dict[str, Union[J2, H2, K2, A2, Sym2]]
        self._mode = {
            "J": None,
            "H": None,
            "K": None,
            "E": None,
            "a": None,
        }  # type: Dict[str, Optional[str]]
        self._furi = {
            "J": False,
            "H": False,
            "K": False,
            "E": False,
            "a": False,
        }  # type: Dict[str, bool]
        self._flag = {
            "p": False,
            "s": False,
            "f": False,
            "c": False,
            "C": False,
            "U": False,
            "u": False,
            "t": True,
        }  # type: Dict[str, bool]
        self._option = {"r": "Hepburn"}  # type: Dict[str, str]
        self._separator = " "  # type: str
        self._separator_string = " "  # type: str

    # v2 API
    def convert(self, text: str) -> List[Dict[str, str]]:
        return self._kakasi.convert(text)
 
class hira:
    def __init__(self) -> None:  
        self.kks = kakasi ()
          
    def fy(self,text): 
        result =self.kks . convert ( text )
        return result
    