# coding: utf8
# skunicode.py
# 10/5/2012 jichi

import locale
from windefs import winlocale

# ja_JP, cp932 on Windows (Japanese)
# en_US, UTF-8 on Mac (English)
PY_LC, PY_ENC = locale.getdefaultlocale()
assert PY_ENC, "cannot detect os encoding"

def u(s, enc=PY_ENC):
  """
  @param  enc  str not None
  @param  s  str or bytearray or None
  @return  unicode or u""
  """
  return s.decode(enc, errors='ignore') if s else u""

def u8(s): return u(s, 'utf8')
def u16(s):return u(s, 'utf16')

def pyunicode(s, enc):
  """
  @param  enc  str not None
  @param  s  str or bytearray or None
  @return  unicode or u""
  """
  if not s:
    return u""
  enc = winlocale.encoding2py(enc) or enc
  return s.decode(enc, errors='ignore')

_Q_C = {}
_Q_D = {}
def qunicode(s, enc):
  """
  @param  enc  str not None
  @param  s  str or bytearray or None
  @return  unicode or u""
  """
  enc = winlocale.encoding2qt(enc) or enc
  if isinstance(enc, unicode):
    enc = enc.encode('utf8', errors='ignore')
  try: d = _Q_D[enc]
  except KeyError:
    from PySide.QtCore import QTextCodec
    c = QTextCodec.codecForName(enc)
    d = c.makeDecoder()
    _Q_C[enc] = c
    _Q_D[enc] = d
  return d.toUnicode(s) if s else u""

def qu8(s): return qunicode(s, 'utf8')
def qu16(s): return qunicode(s, 'utf-16')

_Q_C0 = _Q_D0 = None
def qu(s):
  """
  @param  s  str or bytearray or None
  @return  unicode or u""
  """
  global _Q_D0
  if not _Q_D0:
    global _Q_C0
    from PySide.QtCore import QTextCodec
    _Q_C0 = QTextCodec.codecForLocale()
    _Q_D0 = _Q_C0.makeDecoder()
  return _Q_D0.toUnicode(s) if s else u""

def encodable(s, enc):
  """
  @param  s  str or unicode
  @param  enc  str
  """
  try: s.encode(enc); return True
  except (UnicodeEncodeError, LookupError, AttributeError): return False

def decodable(s, enc):
  """
  @param  s  str or unicode
  @param  enc  str
  """
  try: s.decode(enc); return True
  except (UnicodeDecodeError, LookupError, AttributeError): return False

# Use shift_jis_2004 instead of sjis
def sjis_encodable(s): return encodable(s, 'cp932')
def sjis_decodable(s): return decodable(s, 'cp932')

def u_sjis(s):
  try: return s.decode('cp932')
  except (UnicodeDecodeError, AttributeError): return u(s)
 