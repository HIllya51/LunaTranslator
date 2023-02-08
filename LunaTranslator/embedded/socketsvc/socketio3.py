# coding: utf8
# socketio.py
# jichi 4/28/2014

import os 
from embedded. sakurakit.skdebug import dprint, dwarn
from embedded. socketsvc import socketpack3 as socketpack

MESSAGE_HEAD_SIZE = socketpack.INT_SIZE # = 4
  
def initsocket(socket):
  """
  @param  socket  QIODevice
  """
  socket.messageSize = 0 # body size of the current message

def writesocket(data, socket, pack=True):
  """
  @param  data  str not unicode
  @param  socket  QQIODevice
  @param* pack  bool  whether pack data
  @return  bool

  Passing unicode will crash Python
  """
  #assert isinstance(data, str)
  if pack:
    data = socketpack.packdata(data)
  ok = len(data) == socket.write(data)
  dprint("pass: ok = %s" % ok)
  return ok

def readsocket(socket):
  """
  @param  QIODevice
  @return  QByteArray or None

  The socket used in this function must have messageSize property initialized to 0
  """
  headSize = MESSAGE_HEAD_SIZE
  bytesAvailable = socket.bytesAvailable()
  if not socket.messageSize:
    if bytesAvailable < headSize:
      dprint("insufficient head size")
      return
    ba = socket.read(headSize)
    size = socketpack.unpackuint32(ba)
    if not size:
      dwarn("empty message size")
      return
    socket.messageSize = size
    bytesAvailable -= headSize

  bodySize = socket.messageSize
  if bodySize == 0:
    dwarn("zero data size")
    return ''

  if bytesAvailable < bodySize:
    dprint("insufficient message size: %s < %s" % (bytesAvailable, bodySize))
    return

  dprint("message size = %s" % socket.messageSize)

  data = socket.read(bodySize)
  socket.messageSize = 0
  return data

# EOF
