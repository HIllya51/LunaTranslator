  
from functools import partial
from PyQt5.QtCore import QObject, pyqtSignal  
from embedded.socketsvc import socketio3 as socketio
from PyQt5.QtNetwork import QLocalServer
class LocalSocketServer(QObject):
  """
  Message protocol:
  The first 4b is int32 (message size - 4) (little-endian).
  """

  def __init__(self, parent=None):
    super(LocalSocketServer, self).__init__(parent)
     
    self.encoding = 'utf8'
    self.name = '' # pipe name
    self.server = None # QLocalServer 
  connected = pyqtSignal(QObject) # client socket
  disconnected = pyqtSignal(QObject) # client socket 

  dataReceived = pyqtSignal(bytes, QObject) # data, client socket

  def sendData(self, data, socket, waitTime=0):  # str, QLocalSocket, int -> bool
    ok = self.writeSocket(data, socket)
    if ok and waitTime:
      ok = socket.waitForBytesWritten(waitTime)
    return ok
 
  def setServerName(self, v):  
    self.name  = "\\\\.\\pipe\\" + v 
  def start(self): 
    self.server = QLocalServer(self )
    self.server.newConnection.connect(self._onNewConnection)
    self.server.listen(self.name) 
   
 
  def _onNewConnection(self):
    #assert self.server
    socket = self.server.nextPendingConnection();
    if socket:
      socketio.initsocket(socket)  
      socket.connected.connect(partial(self.connected.emit,socket))
      socket.disconnected.connect(partial(self.disconnected.emit,socket)) 

      socket.readyRead.connect(partial(self.readSocket,socket)) 
    #self.readSocket(socket)
 

  def readSocket(self, socket):
    try:
      while socket.bytesAvailable():
        data = socketio.readsocket(socket)
        if data == None:
          break
        else:
          self.dataReceived.emit(data, socket)
    except Exception as e: # might raise runtime exception since the socket has been deleted
      print(e)

  def writeSocket(self, data, socket):
    if isinstance(data, str):
      data = data.encode(self.encoding, errors='ignore')
    return socketio.writesocket(data, socket)
 