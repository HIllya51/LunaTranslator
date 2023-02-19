# coding: utf8
# rpcman.py
# 2/1/2013 jichi

__all__ = 'RpcServer' 
 
RPC_WAIT_TIME = 3000 # wait time after sending data
from  embedded.socketsvc.localsocketsrv3 import LocalSocketServer
from embedded.socketsvc import socketpack3 as socketpack  
APP_SOCKET_NAME='vnr.socket' 
  

def _unmarshalInteger(s): # str -> int, use hex
  #try: return int(s, 16) #if s.startswith('0x') else int(s)
  try: return int(s)
  except ValueError:
    print("failed to marshal number %s" % s)
    return 0
 
def _unmarshalBool(s): # str -> bool
  return s == '1'
 
#from ctypes import c_intint
from functools import partial
import json
from PyQt5.QtCore import pyqtSignal, Qt, QObject  
   

class RpcServer(QObject):  
  def __init__(self ): 
    super(RpcServer, self).__init__( )  
    self.server = LocalSocketServer( ) 
    self.server.setServerName(APP_SOCKET_NAME) 
    self.server.dataReceived.connect(self._onDataReceived)

    self.server.disconnected.connect(self._onDisconnected)

    self.agentSocket = None # QAbstractSocket
    self.agentPid = 0 # int
    self=self   
    
  def start(self):
    """@return  bool""" 
    return self.server.start()
     

  agentConnected = pyqtSignal(int) # pid
  agentDisconnected = pyqtSignal(int) # pid 
  engineReceived = pyqtSignal(str) # name
  engineTextReceived = pyqtSignal(str, str,  int ) # text, hash, role, needsTranslation
 
  def disableAgent(self): self.callAgent('disable')

  #def detachAgent(self): self.callAgent('detach')

  def agentProcessId(self): return self.agentPid

  def setAgentSettings(self, data):
    """
    @param  data  {k:v}
    """
    try:
       
      data = json.dumps(data) #, ensure_ascii=False) # the json parser in vnragent don't enforce ascii
      self.callAgent('settings', data)
    except TypeError as e:
      from traceback import print_exc 
      print_exc() 
  

  def callAgent(self, *args):
    if self.agentSocket:
      data = socketpack.packstrlist(args)
      #print("senddata",bytes(data))
      self.server.sendData(data, self.agentSocket, waitTime=RPC_WAIT_TIME)

  # Receive

  def _onDisconnected(self, socket):
    if socket is self.agentSocket:
      #print("pass: pid = %s" % self.agentPid)
      self.agentSocket = None
      self.agentDisconnected.emit(self.agentPid)
      self.agentPid  = 0

  def _onDataReceived(self, data, socket):
    args = socketpack.unpackstrlist(data)
    #print("datareceived",args)
    if not args:
      print("unpack data failed")
      return
    self._onCall(socket, *args)

  def _onCall(self, socket, cmd, *params): # on serverMessageReceived
    
    if cmd == 'agent.ping':
      if params:
        pid = _unmarshalInteger(params[0])
        if pid:
          self._onAgentPing(socket, pid) 
    elif cmd == 'agent.engine.name':
      if params:
        self.engineReceived.emit(params[0])
    elif cmd == 'agent.engine.text':
      if len(params) == 5: 
        self._onEngineText(*params)
       
 
  def _onAgentPing(self, socket, pid):
    """
    @param  socket  QTcpSocket
    @param  pid  int
    """  
    #print(self.agentSocket)
    if self.agentSocket:
      self.server.closeSocket(self.agentSocket)
    self.agentPid = pid
    self.agentSocket = socket
    self.agentConnected.emit(pid) # pyqtSignal TO BE CHANGED
 
  def _onEngineText(self, text, hash, sig, role, trans):
    """
    @param  text  unicode
    @param  hash  qint64
    @param  role  int
    @param  trans  bool   need translation
    """
    try:
      #hash = _unmarshalInteger(hash) # delay convert it to number
      role = _unmarshalInteger(role)
      sig = _unmarshalInteger(sig)
      trans = _unmarshalBool(trans) 
      if trans:
        #print(text) 
        self.engineTextReceived.emit(text, hash,   role ) 
    except ValueError:
      print("failed to convert text hash or role to integer")
 
 