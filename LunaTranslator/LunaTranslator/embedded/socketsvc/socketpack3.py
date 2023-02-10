# coding: utf8
# socketpack.py
# jichi 4/28/2014
# Marshal bytes

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  
#from PySide.QtCore import QByteArray

# Little endian
ENDIANNESS = 'little'

INT32_SIZE = 4 # number of bytes of int32
INT_SIZE = INT32_SIZE

# Bytes

#def signedord(c):
#  """Return signed char value of the character
#  @param  c  char
#  @return  int[-128,127]
#  """
#  ret = ord(c)
#  return ret if ret < 128 else ret - 256

# http://stackoverflow.com/questions/444591/convert-a-string-of-bytes-into-an-int-python
def unpackuint(s): #
  """
  @param  s  str|bytearray|QByteArray
  @return  int
  """
  #return sum(ord(c) << (i * 8) for i,c in enumerate(s[::-1])) # reverse sign does not work for QByteArray 
  size = len(s)
  return sum((ord(c) << (8 * (size - i - 1))) for i,c in enumerate(s))

def unpackuint32(s, i=0): #
  """
  @param  s  str|bytearray|QByteArray
  @param*  i  int  start index
  @return  int
  """ 
  return ( (s[i]) << 24) | ( (s[i+1]) << 16) | ( (s[i+2]) << 8) |  (s[i+3]) if len(s) >= 4 + i else 0
 
def packuint32(i): # int -> str
  """
  @param  number  i
  @return  str  4 bytes
  """ 
  return bytes(chr((i >> 24) & 0xff) + chr((i >> 16) & 0xff) + chr((i >> 8) & 0xff) + chr(i & 0xff),encoding='latin-1')
 

def packdata(data):
  """
  @param  data  str not unicode
  @return  str
  """
  # Explicitly use QByteArray to preserve message size
  #if isinstance(data, unicode):
  #  data = data.encode(encoding, errors=encodingErrors)
  #if not isinstance(data, QByteArray):
  #  data = QByteArray(data)
  size = len(data)
  return packuint32(size) + data

# String list

def _unicode(data, encoding): # str|QByteArray, str -> unicode
  return data.decode(encoding,errors='ignore') 
import sys
def packstrlist(l, encoding='utf8'):
  """
  @param  l  [unicode]
  @return  str
  """
  head = []
  body = []
  head.append(len(l))
  for s in l:

    s = s.encode(encoding, errors='ignore')
    head.append(len(s))
    body.append(s) 
  return b''.join(map(packuint32, head)) + b''.join(body)

def unpackstrlist(data, encoding='utf8'):
  """
  @param  data  str|bytearray|QByteArray
  @return  [unicode] not None
  """
  dataSize = len(data)
  if dataSize < INT32_SIZE:
    print("insufficient list size")
    return []
  offset = 0
  count = unpackuint32(data, offset); offset += INT32_SIZE
  if count == 0:
    print("empty list")
    return []
  if count * INT32_SIZE > dataSize - offset:
    print("insufficient head size")
    return []
  sizes = [] # [int]
  for i in range(0, count):
    size = unpackuint32(data, offset); offset += INT32_SIZE
    sizes.append(size)
  if sum(sizes) > dataSize - offset:
    print("insufficient body size")
    return []
  ret = []
  for size in sizes:
    if size == 0:
      ret.append('')
    else:
      s = data[offset:offset+size]
      s = _unicode(s, encoding)
      ret.append(s)
      offset += size
  return ret
 