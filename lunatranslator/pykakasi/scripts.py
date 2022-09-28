# -*- coding: utf-8 -*-
# scripts.py
#
# Copyright 2011-2019 Hiroshi Miura <miurahr@linux.com>
import functools
import pickle
from typing import Dict

from .properties import Ch, Configurations, Convert_Tables


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
