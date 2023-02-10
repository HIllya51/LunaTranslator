# -*- coding: utf-8 -*-
#  kakasi.py
#
# Copyright 2011-2021 Hiroshi Miura <miurahr@linux.com>
from typing import Dict, List, Optional, Tuple, Union

from deprecated import deprecated  # type: ignore  # noqa

from .kakasi import Kakasi, PyKakasiException
from .kanji import Itaiji, JConv
from .properties import Ch
from .scripts import A2, H2, K2, Sym2


class UnsupportedRomanRulesException(PyKakasiException):
    pass


class UnknownOptionsException(PyKakasiException):
    pass


class InvalidModeValueException(PyKakasiException):
    pass


class InvalidFlagValueException(PyKakasiException):
    pass


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

    # v1 API implementations
    @deprecated(version=2.1, reason="Old API will be removed in v3.0.")
    def setMode(self, fr: str, to: Optional[Union[bool, str]]) -> None:
        if fr in self._keys:
            if to is None:
                self._mode[fr] = None
            elif isinstance(to, str) and to[0] in self._values:
                self._mode[fr] = to[0]
                if len(to) == 2 and to[1] == "F":
                    self._furi[fr] = True
            else:
                raise InvalidModeValueException("Invalid value for mode")
        elif fr in self._flag.keys():
            if isinstance(to, bool):
                self._flag[fr] = to
            else:
                raise InvalidFlagValueException("Invalid flag value")
        elif fr == "r":
            if isinstance(to, str) and to in self._roman_vals:
                self._option["r"] = to
            else:
                raise UnsupportedRomanRulesException("Unknown roman table name")
        elif fr == "S":
            if isinstance(to, str):
                self._separator = to
            else:
                raise InvalidFlagValueException("Incompatible separator value")
        else:
            raise UnknownOptionsException("Unhandled options")  # pragma: no cover

    @deprecated(version=2.1, reason="Old API will be removed in v3.0.")
    def getConverter(self):
        self._conv["J"] = J2(self._mode["J"], method=self._option["r"])
        self._conv["H"] = H2(self._mode["H"], method=self._option["r"])
        self._conv["K"] = K2(self._mode["K"], method=self._option["r"])
        self._conv["E"] = Sym2(self._mode["E"])
        self._conv["a"] = A2(self._mode["a"])
        return self

    @deprecated(version=2.1, reason="Old API will be removed in v3.0.")
    def do(self, text: str) -> str:
        _MAXLEN = 32
        otext = ""
        i = 0
        while True:
            if i >= len(text):
                break

            if self._conv["J"].isRegion(text[i]):
                mode = "J"
            elif self._conv["H"].isRegion(text[i]):
                mode = "H"
            elif self._conv["K"].isRegion(text[i]):
                mode = "K"
            elif self._conv["E"].isRegion(text[i]):
                mode = "E"
            elif self._conv["a"].isRegion(text[i]):
                mode = "a"
            else:
                mode = "o"

            if mode in ("J", "E"):
                w = min(i + _MAXLEN, len(text))
                (t, l1) = self._conv[mode].convert(text[i:w])

                if l1 > 0:
                    orig = text[i : i + l1]
                    chunk = t
                    i += l1
                else:
                    orig = text[i : i + 1]
                    if self._flag["t"]:
                        chunk = orig
                    else:
                        chunk = "???"
                    i += 1

            elif mode in ("H", "K", "a"):
                orig = ""
                chunk = ""

                while i < len(text):

                    if text[i] in "\u30FC\u2015\u2212\uFF70":

                        # FIXME: q&d workaround when hiragana/katanaka dash is first char.
                        if self._mode[mode] is not None and len(chunk) > 0:
                            # use previous char as a transliteration for kana-dash
                            orig += text[i]
                            chunk = chunk + chunk[-1]
                            i += 1
                        elif len(chunk) == 0:
                            orig += text[i]
                            chunk += "-"
                            i += 1
                            break
                        else:
                            orig += text[i]
                            chunk += text[i]
                            i += 1
                            break

                    elif self._conv[mode].isRegion(text[i]):
                        w = min(i + _MAXLEN, len(text))
                        (t, l1) = self._conv[mode].convert(text[i:w])
                        if l1 > 0:
                            orig += text[i : i + l1]
                            chunk += t
                            i += l1
                        else:
                            orig = text[i : i + 1]
                            if self._flag["t"]:
                                chunk = orig
                            else:
                                chunk = "???"
                            i += 1
                            break

                    else:
                        # i += 1
                        break

            else:
                otext += text[i]
                i += 1
                continue

            if mode in ("J", "E"):
                if self._flag["U"]:
                    chunk = chunk.upper()
                elif self._flag["C"]:
                    chunk = chunk.capitalize()

            if mode in self._keys and self._furi[mode]:
                otext += orig + "[" + chunk + "]"
            else:
                otext += chunk

            # insert separator when option specified and it is not a last character and not an end mark
            if (
                self._flag["s"]
                and otext[-len(self._separator) :] != self._separator
                and i < len(text)
                and text[i] not in Ch.endmark
            ):
                otext += self._separator

        return otext


@deprecated(version=2.1, reason="Old API will be removed in v3.0.")
class wakati(kakasi):
    def __init__(self):
        super(wakati, self).__init__()
        self._jconv = JConv()
        self._state = True  # type: bool

    def getConverter(self):
        return self

    def setMode(self, fr: str, to: Optional[Union[bool, str]]) -> None:
        if fr in self._flag.keys():
            if isinstance(to, bool):
                self._flag[fr] = to
            else:
                raise InvalidFlagValueException("Invalid flag value")
            raise UnknownOptionsException("Unhandled options")

    def do(self, text: str) -> str:

        if len(text) == 0:
            return ""

        otext = ""
        i = 0
        while True:
            if i >= len(text):
                break

            if self._jconv.isRegion(text[i]):
                _, ln = self._jconv.convert(text[i:])
                if ln <= 0:  # pragma: no cover
                    otext = otext + text[i]
                    i += 1
                    self._state = False
                elif (i + ln) < len(text):
                    if self._state:
                        otext = otext + text[i : i + ln] + self._separator
                    else:
                        otext = (
                            otext + self._separator + text[i : i + ln] + self._separator
                        )
                        self._state = True
                    i = i + ln
                else:
                    if self._state:
                        otext = otext + text[i : i + ln]
                    else:  # pragma: no cover
                        otext = otext + self._separator + text[i : i + ln]
                    break

            else:
                self._state = False
                otext = otext + text[i]
                i += 1

        return otext


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
