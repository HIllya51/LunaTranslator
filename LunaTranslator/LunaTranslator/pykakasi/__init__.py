# -*- coding: utf-8 -*-
#  kakasi.py
#
# Copyright 2011-2021 Hiroshi Miura <miurahr@linux.com>
#

__license__ = "GPLv3"
__copyright__ = """\
PyKakasi::
    Copyright (C) 2010-2021 Hiroshi Miura and contributors

KAKASI Dictionary::
    Copyright (C) 2010-2021 Hiroshi Miura and contributors

    Copyright (C) 1992 1993 1994 Hironobu Takahashi, Masahiko Sato,
    Yukiyoshi Kameyama, Miki Inooka, Akihiko Sasaki, Dai Ando, Junichi Okukawa,
    Katsushi Sato and Nobuhiro Yamagishi

UniDic::
    PyKakasi re-licenses a part of the unidic under the GPL3+.

    Copyright (c) 2011-2021, The UniDic Consortium

    All rights reserved.

    Unidic is released under any of the GPL2, the LGPL2.1,
    or the 3-clause BSD License.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "restructuredtext en"

from .kakasi import Kakasi, PyKakasiException, UnknownCharacterException
from .legacy import (
    InvalidFlagValueException,
    InvalidModeValueException,
    UnknownOptionsException,
    UnsupportedRomanRulesException,
    kakasi,
    wakati,
)

__all__ = [
    "Kakasi",
    "kakasi",
    "wakati",
    "PyKakasiException",
    "UnknownCharacterException",
    "UnsupportedRomanRulesException",
    "UnknownOptionsException",
    "InvalidModeValueException",
    "InvalidFlagValueException",
]
