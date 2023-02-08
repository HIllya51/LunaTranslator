# coding: utf8
# localsocketsrv.py
# jichi 4/28/2014

__all__ = 'LocalSocketServer',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import weakref
from functools import partial
from PyQt5.QtCore import QObject, pyqtSignal 
from embedded.sakurakit.skdebug import dprint, dwarn
from embedded.socketsvc import socketio3 as socketio

class LocalSocketServer(QObject):
  """
  Message protocol:
  The first 4b is int32 (message size - 4) (little-endian).
  """

  def __init__(self, parent=None):
    super(LocalSocketServer, self).__init__(parent)
    self.__d = _LocalSocketServer(self)
    self.__d.q=self
  connected = pyqtSignal(QObject) # client socket
  disconnected = pyqtSignal(QObject) # client socket
  socketError = pyqtSignal(QObject) # client socket

  dataReceived = pyqtSignal(bytes, QObject) # data, client socket

  def sendData(self, data, socket, waitTime=0):  # str, QLocalSocket, int -> bool
    ok = self.__d.writeSocket(data, socket)
    if ok and waitTime:
      ok = socket.waitForBytesWritten(waitTime)
    return ok

  def waitForBytesWritten(self, waitTime=30000): # -> bool
    ok = True
    for s in self.__d.sockets:
      ok = s.waitForBytesWritten(waitTime) and ok
    return ok

  def broadcastData(self, data, *args, **kwargs):  # str, int -> bool
    for s in self.__d.sockets:
      self.sendData(data, s, *args, **kwargs)

  def connectionCount(self):
    return len(self.__d.sockets)

  def serverName(self): return self.__d.name # -> str
  def setServerName(self, v): 
    print("setingservername",v)
    self.__d.name =s = "\\\\.\\pipe\\" + v
    print("setedservername",self.__d.name)
  def start(self): return self.__d.start() # -> bool
  def stop(self): self.__d.stop()

  def isListening(self): # -> bool
    return bool(self.__d.server) and self.__d.server.isListening()

  isActive = isListening

  def closeSocket(self, socket): # QLocalSocket
    if socket.isOpen():
      socket.close()
    self.__d.deleteSocket(socket)
 
class _LocalSocketServer(object):
  def __init__(self, q):
    self.encoding = 'utf8'
    self.name = '' # pipe name
    self.server = None # QLocalServer
    self.sockets = [] # [QLocalSocket]

  def _createServer(self):
    from PyQt5.QtNetwork import QLocalServer
    ret = QLocalServer(self.q)
    ret.newConnection.connect(self._onNewConnection)
    return ret

  def start(self): # -> bool
    
    if not self.server:
      dwarn("bad")
      self.server = self._createServer()
    ok = self.server.listen(self.name)
    dwarn("start",ok,self.name)
    dprint("pass: ok = %s" % ok)
    return ok

  def stop(self):
    if self.server:
      self.server.close()
      dprint("pass")

  def _onNewConnection(self):
    #assert self.server
    socket = self.server.nextPendingConnection();
    if socket:
      socketio.initsocket(socket)
      self.sockets.append(socket)
      ref = weakref.ref(socket)
      socket.error.connect(partial(lambda ref, error:
          self.q.socketError.emit(ref()),
          ref))
      socket.connected.connect(partial(lambda ref:
          self.q.connected.emit(ref()),
          ref))
      socket.disconnected.connect(partial(lambda ref:
          self.q.disconnected.emit(ref()),
          ref))

      socket.disconnected.connect(partial(lambda ref:
          self.deleteSocket(ref()),
          ref))

      socket.readyRead.connect(partial(lambda ref:
          self.readSocket(ref()),
          ref))
    dprint("pass");
    #self.readSocket(socket)

  def deleteSocket(self, socket):
    socket.deleteLater()
    try: self.sockets.remove(socket)
    except ValueError: pass

  def readSocket(self, socket):
    try:
      while socket.bytesAvailable():
        data = socketio.readsocket(socket)
        if data == None:
          break
        else:
          self.q.dataReceived.emit(data, socket)
    except Exception as e: # might raise runtime exception since the socket has been deleted
      dwarn(e)

  def writeSocket(self, data, socket):
    if isinstance(data, str):
      data = data.encode(self.encoding, errors='ignore')
    return socketio.writesocket(data, socket)
 