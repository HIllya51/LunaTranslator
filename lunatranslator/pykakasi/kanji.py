# -*- coding: utf-8 -*-
# j2.py
#
# Copyright 2011-2019 Hiroshi Miura <miurahr@linux.com>
import functools
import pickle
import threading
from typing import Tuple

from .properties import Configurations


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
